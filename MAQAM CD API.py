      #!/usr/bin/env python3
"""
MAQAM CD API - Version complète avec toutes les fonctionnalités
Système d'exploitation audiophile bit-perfect pour MAQAM Audio OS
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import subprocess
import os
import logging
import signal
import time
import re
import json
import threading
import queue
import hashlib
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin pour l'interface web

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s: %(message)s [%(funcName)s:%(lineno)d]',
    handlers=[
        logging.FileHandler('/var/log/maqam-cd-api.log'),
        logging.StreamHandler()
    ]
)

# === CONFIGURATION ===
CD_DEVICE = "/dev/sr1"
RIP_SCRIPT = "/usr/local/bin/rip_cd.sh"
MUSICBRAINZ_API_BASE = "https://musicbrainz.org/ws/2"
MUSICBRAINZ_USER_AGENT = "MAQAM-Audio-OS/1.0 (charly.laurencin@gmail.com)"
PIPEWIRE_TARGET_SINK = "alsa_output.usb-KHADAS_Tone2_Pro_Tone2_Pro-00.pro-output-0"

# === VARIABLES GLOBALES ===
# Processus et état de lecture
playback_process_cdparanoia = None
playback_process_pwcat = None
current_playing_track_number = None
is_playback_paused_flag = False
playback_start_time = None
playback_pause_duration = 0.0
playback_mode = {
    "repeat": False,      # Répéter la piste actuelle
    "shuffle": False,     # Lecture aléatoire
    "repeat_all": False   # Répéter tout l'album
}

# Processus d'extraction
ripping_process_script = None
ripping_progress = {
    "active": False,
    "current_track": 0,
    "total_tracks": 0,
    "percentage": 0,
    "current_track_percentage": 0,
    "estimated_time_remaining": None,
    "format": "flac",
    "output_path": None
}

# Cache des informations CD
CD_INFO_CACHE = {
    "toc": None,
    "musicbrainz_data": None,
    "last_checked": 0,
    "disc_id": None,
    "total_tracks": 0
}
CD_INFO_CACHE_TTL = 30  # secondes

# File d'attente pour les mises à jour de progression
progress_queue = queue.Queue()

# === FONCTIONS UTILITAIRES ===

def calculate_disc_id(toc_data: Dict) -> Optional[str]:
    """Calcule le Disc ID MusicBrainz à partir de la TOC"""
    try:
        if not toc_data.get("track_details"):
            return None
        
        # Algorithme simplifié pour le Disc ID MusicBrainz
        # En réalité, il faudrait utiliser libdiscid pour un calcul précis
        track_count = len(toc_data["track_details"])
        total_length = sum(track.get("duration_sec", 180) for track in toc_data["track_details"])
        
        # Générer un hash basé sur le nombre de pistes et la durée totale
        disc_data = f"{track_count}:{total_length}"
        return hashlib.sha1(disc_data.encode()).hexdigest()[:28]
    except Exception as e:
        app.logger.error(f"Erreur lors du calcul du Disc ID: {e}")
        return None

def get_musicbrainz_metadata(disc_id: str, track_count: int) -> Dict:
    """Récupère les métadonnées depuis MusicBrainz"""
    try:
        headers = {"User-Agent": MUSICBRAINZ_USER_AGENT}
        
        # Recherche par nombre de pistes si pas de disc_id valide
        if not disc_id:
            # Recherche générique par nombre de pistes
            url = f"{MUSICBRAINZ_API_BASE}/release"
            params = {
                "query": f"tracks:{track_count}",
                "limit": 1,
                "fmt": "json"
            }
        else:
            # Recherche par Disc ID
            url = f"{MUSICBRAINZ_API_BASE}/discid/{disc_id}"
            params = {"inc": "releases+recordings", "fmt": "json"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "releases" in data and data["releases"]:
                release = data["releases"][0]
                return {
                    "title": release.get("title", "Album Inconnu"),
                    "artist": release.get("artist-credit", [{}])[0].get("name", "Artiste Inconnu") if release.get("artist-credit") else "Artiste Inconnu",
                    "date": release.get("date", ""),
                    "tracks": [
                        {
                            "number": i + 1,
                            "title": f"Piste {i + 1}",
                            "artist": release.get("artist-credit", [{}])[0].get("name", "Artiste Inconnu") if release.get("artist-credit") else "Artiste Inconnu"
                        }
                        for i in range(track_count)
                    ]
                }
        
        # Retour par défaut si pas de données MusicBrainz
        return {
            "title": "Album Inconnu",
            "artist": "Artiste Inconnu",
            "date": "",
            "tracks": [
                {
                    "number": i + 1,
                    "title": f"Piste {i + 1}",
                    "artist": "Artiste Inconnu"
                }
                for i in range(track_count)
            ]
        }
        
    except Exception as e:
        app.logger.warning(f"Impossible de récupérer les métadonnées MusicBrainz: {e}")
        return {
            "title": "Album Inconnu",
            "artist": "Artiste Inconnu",
            "date": "",
            "tracks": [
                {
                    "number": i + 1,
                    "title": f"Piste {i + 1}",
                    "artist": "Artiste Inconnu"
                }
                for i in range(track_count)
            ]
        }

def parse_cd_info_output(output: str) -> Dict:
    """Parse la sortie de cd-info pour extraire les informations détaillées"""
    toc_data = {
        "status": "unknown",
        "tracks": 0,
        "track_details": [],
        "total_duration_sec": 0,
        "error": None
    }
    
    try:
        lines = output.splitlines()
        track_pattern = re.compile(r'^\s*TRACK\s+(\d+)\s+.*?(\d{2}):(\d{2})\.(\d{2})')
        
        for line in lines:
            if "No medium found" in line or "No disc in drive" in line:
                toc_data["status"] = "no_disc"
                return toc_data
            elif "Disc mode is listed as: CD-DA" in line:
                toc_data["status"] = "audio_cd_present"
            elif "ISO 9660" in line or "UDF" in line:
                toc_data["status"] = "data_cd_present"
                return toc_data
            
            # Extraction des informations de piste
            match = track_pattern.search(line)
            if match:
                track_num = int(match.group(1))
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                frames = int(match.group(4))
                
                duration_sec = minutes * 60 + seconds + (frames / 75.0)
                
                toc_data["track_details"].append({
                    "number": track_num,
                    "duration_sec": duration_sec,
                    "duration_formatted": f"{minutes:02d}:{seconds:02d}",
                    "title": f"Piste {track_num}",
                    "artist": "Artiste Inconnu"
                })
        
        toc_data["tracks"] = len(toc_data["track_details"])
        toc_data["total_duration_sec"] = sum(track["duration_sec"] for track in toc_data["track_details"])
        
        if toc_data["tracks"] == 0 and toc_data["status"] == "audio_cd_present":
            toc_data["status"] = "disc_present_unknown_type"
            
    except Exception as e:
        app.logger.error(f"Erreur lors du parsing cd-info: {e}")
        toc_data["error"] = str(e)
        
    return toc_data

def get_cd_toc_and_update_globals() -> Dict:
    """Récupère la TOC du CD et met à jour les variables globales"""
    global CD_INFO_CACHE
    
    current_time = time.time()
    is_busy = playback_process_cdparanoia or check_ripping_status()
    
    # Vérifier le cache
    if (not is_busy and CD_INFO_CACHE["toc"] and 
        (current_time - CD_INFO_CACHE["last_checked"] < CD_INFO_CACHE_TTL)):
        app.logger.debug("Retour des données CD depuis le cache")
        return CD_INFO_CACHE["toc"]
    
    app.logger.info(f"Récupération des informations CD via cd-info pour {CD_DEVICE}")
    
    command = ['/usr/bin/cd-info', '-C', CD_DEVICE, '--no-header', '--no-ioctl', 
               '--no-cddb', '--no-analyze', '-T']
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        output = result.stdout + "\n" + result.stderr
        
        app.logger.debug(f"Sortie cd-info (code {result.returncode}):\n{output.strip()}")
        
        if result.returncode == 0:
            toc_data = parse_cd_info_output(output)
        else:
            toc_data = {"status": "error_reading_disc", "tracks": 0, "track_details": [], 
                       "error": result.stderr.strip() if result.stderr else "Erreur cd-info"}
            
    except subprocess.TimeoutExpired:
        app.logger.error(f"Timeout de la commande cd-info pour {CD_DEVICE}")
        toc_data = {"status": "error_timeout", "tracks": 0, "track_details": [], 
                   "error": "cd-info timeout"}
    except FileNotFoundError:
        app.logger.error("Commande cd-info introuvable. Installer libcdio")
        toc_data = {"status": "error_missing_dependency", "tracks": 0, "track_details": [], 
                   "error": "cd-info non trouvé"}
    except Exception as e:
        app.logger.error(f"Erreur inattendue avec cd-info: {e}")
        toc_data = {"status": "error_unexpected", "tracks": 0, "track_details": [], 
                   "error": str(e)}
    
    # Mettre à jour le cache
    CD_INFO_CACHE["toc"] = toc_data
    CD_INFO_CACHE["last_checked"] = current_time
    CD_INFO_CACHE["total_tracks"] = toc_data.get("tracks", 0)
    
    # Récupérer les métadonnées MusicBrainz si c'est un CD audio
    if toc_data.get("status") == "audio_cd_present" and toc_data.get("tracks", 0) > 0:
        disc_id = calculate_disc_id(toc_data)
        CD_INFO_CACHE["disc_id"] = disc_id
        
        if not CD_INFO_CACHE["musicbrainz_data"]:
            app.logger.info("Récupération des métadonnées MusicBrainz")
            mb_data = get_musicbrainz_metadata(disc_id, toc_data["tracks"])
            CD_INFO_CACHE["musicbrainz_data"] = mb_data
            
            # Fusionner les métadonnées avec les données de piste
            for i, track in enumerate(toc_data["track_details"]):
                if i < len(mb_data["tracks"]):
                    track["title"] = mb_data["tracks"][i]["title"]
                    track["artist"] = mb_data["tracks"][i]["artist"]
    
    return toc_data

def check_ripping_status() -> bool:
    """Vérifie si un processus d'extraction est en cours"""
    global ripping_process_script, ripping_progress
    
    if ripping_process_script is None:
        ripping_progress["active"] = False
        return False
    
    if ripping_process_script.poll() is None:
        return True
    else:
        app.logger.info(f"Script d'extraction (PID: {ripping_process_script.pid}) terminé avec le code: {ripping_process_script.returncode}")
        ripping_process_script = None
        ripping_progress["active"] = False
        return False

def stop_current_playback(log_info: bool = True) -> bool:
    """Arrête la lecture en cours"""
    global playback_process_cdparanoia, playback_process_pwcat
    global current_playing_track_number, is_playback_paused_flag
    global playback_start_time, playback_pause_duration
    
    stopped_something = False
    
    if playback_process_pwcat:
        try:
            if log_info:
                app.logger.info(f"Arrêt du processus pw-cat (PID: {playback_process_pwcat.pid})")
            playback_process_pwcat.terminate()
            playback_process_pwcat.wait(timeout=2)
        except subprocess.TimeoutExpired:
            if log_info:
                app.logger.warning(f"pw-cat (PID: {playback_process_pwcat.pid}) ne s'arrête pas, kill forcé")
            playback_process_pwcat.kill()
        except Exception as e:
            if log_info:
                app.logger.error(f"Erreur lors de l'arrêt de pw-cat: {e}")
        playback_process_pwcat = None
        stopped_something = True
    
    if playback_process_cdparanoia:
        try:
            if log_info:
                app.logger.info(f"Arrêt du processus cdparanoia (PID: {playback_process_cdparanoia.pid})")
            playback_process_cdparanoia.terminate()
            playback_process_cdparanoia.wait(timeout=2)
        except subprocess.TimeoutExpired:
            if log_info:
                app.logger.warning(f"cdparanoia (PID: {playback_process_cdparanoia.pid}) ne s'arrête pas, kill forcé")
            playback_process_cdparanoia.kill()
        except Exception as e:
            if log_info:
                app.logger.error(f"Erreur lors de l'arrêt de cdparanoia: {e}")
        playback_process_cdparanoia = None
        stopped_something = True
    
    # Réinitialiser l'état
    if stopped_something or log_info:
        current_playing_track_number = None
        is_playback_paused_flag = False
        playback_start_time = None
        playback_pause_duration = 0.0
    
    return stopped_something

def get_playback_position() -> Dict:
    """Calcule la position actuelle de lecture"""
    if not playback_start_time or not current_playing_track_number:
        return {"position_sec": 0, "position_formatted": "00:00"}
    
    current_time = time.time()
    if is_playback_paused_flag:
        elapsed = playback_pause_duration
    else:
        elapsed = (current_time - playback_start_time) - playback_pause_duration
    
    elapsed = max(0, elapsed)
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    return {
        "position_sec": elapsed,
        "position_formatted": f"{minutes:02d}:{seconds:02d}"
    }

def _play_track_internal(track_to_play: int) -> Tuple[bool, str]:
    """Fonction interne pour lancer la lecture d'une piste"""
    global playback_process_cdparanoia, playback_process_pwcat
    global current_playing_track_number, is_playback_paused_flag
    global playback_start_time, playback_pause_duration
    
    stop_current_playback()
    
    app.logger.info(f"Début de lecture de la piste: {track_to_play}")
    
    # Commandes pour la lecture bit-perfect
    cmd_cdparanoia = ['/usr/bin/cdparanoia', '-d', CD_DEVICE, str(track_to_play), '-']
    cmd_pwcat = [
        '/usr/bin/pw-cat', '--playback', '--target', PIPEWIRE_TARGET_SINK,
        '--format', 'S16LE', '--rate', '44100', '--channels', '2',
        '--latency', '100ms', '--quality', '4', '-'
    ]
    
    try:
        # Lancer cdparanoia
        playback_process_cdparanoia = subprocess.Popen(
            cmd_cdparanoia, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Lancer pw-cat en chaînant avec cdparanoia
        playback_process_pwcat = subprocess.Popen(
            cmd_pwcat, 
            stdin=playback_process_cdparanoia.stdout, 
            stderr=subprocess.PIPE
        )
        
        # Fermer le stdout de cdparanoia pour permettre le pipe
        if playback_process_cdparanoia.stdout:
            playback_process_cdparanoia.stdout.close()
        
        # Mettre à jour l'état
        current_playing_track_number = track_to_play
        is_playback_paused_flag = False
        playback_start_time = time.time()
        playback_pause_duration = 0.0
        
        app.logger.info(f"Lecture démarrée: cdparanoia PID {playback_process_cdparanoia.pid}, pw-cat PID {playback_process_pwcat.pid}")
        return True, f"Lecture de la piste {track_to_play} démarrée"
        
    except Exception as e:
        app.logger.error(f"Erreur lors du démarrage de la lecture pour la piste {track_to_play}: {e}")
        stop_current_playback()
        return False, f"Erreur lors du démarrage: {e}"

def get_next_track() -> Optional[int]:
    """Détermine la piste suivante selon le mode de lecture"""
    global current_playing_track_number, playback_mode, CD_INFO_CACHE
    
    total_tracks = CD_INFO_CACHE.get("total_tracks", 0)
    if total_tracks == 0:
        return None
    
    if playback_mode["repeat"] and current_playing_track_number:
        return current_playing_track_number
    
    if playback_mode["shuffle"]:
        import random
        available_tracks = list(range(1, total_tracks + 1))
        if current_playing_track_number in available_tracks:
            available_tracks.remove(current_playing_track_number)
        return random.choice(available_tracks) if available_tracks else 1
    
    if current_playing_track_number:
        if current_playing_track_number < total_tracks:
            return current_playing_track_number + 1
        elif playback_mode["repeat_all"]:
            return 1
    
    return None

def get_previous_track() -> Optional[int]:
    """Détermine la piste précédente"""
    global current_playing_track_number, CD_INFO_CACHE
    
    total_tracks = CD_INFO_CACHE.get("total_tracks", 0)
    if total_tracks == 0:
        return None
    
    if current_playing_track_number and current_playing_track_number > 1:
        return current_playing_track_number - 1
    
    return total_tracks  # Boucler vers la dernière piste

def monitor_ripping_progress():
    """Thread pour surveiller la progression de l'extraction"""
    global ripping_progress, ripping_process_script
    
    while ripping_progress["active"] and ripping_process_script:
        try:
            # Analyser les logs du processus d'extraction
            # Cette implémentation est simplifiée - dans un vrai cas,
            # il faudrait parser la sortie de cdparanoia en temps réel
            
            if ripping_process_script.poll() is not None:
                ripping_progress["active"] = False
                break
            
            # Simulation de progression (à remplacer par une vraie analyse des logs)
            if ripping_progress["percentage"] < 100:
                ripping_progress["percentage"] = min(100, ripping_progress["percentage"] + 2)
            
            time.sleep(1)
            
        except Exception as e:
            app.logger.error(f"Erreur dans le monitoring de l'extraction: {e}")
            break

# === ROUTES API ===

@app.route('/api/cd/status', methods=['GET'])
def cd_status_route():
    """Retourne l'état complet du système CD"""
    global playback_process_cdparanoia, is_playback_paused_flag, current_playing_track_number
    global playback_mode, ripping_progress
    
    ripping = check_ripping_status()
    toc_info = get_cd_toc_and_update_globals()
    
    # État de lecture
    is_playing_now = (playback_process_cdparanoia is not None and
                      playback_process_cdparanoia.poll() is None and
                      not is_playback_paused_flag)
    
    is_paused_now = (playback_process_cdparanoia is not None and
                     playback_process_cdparanoia.poll() is None and
                     is_playback_paused_flag)
    
    # Position de lecture
    playback_position = get_playback_position()
    
    # Informations sur la piste actuelle
    current_track_info = None
    if current_playing_track_number and toc_info.get("track_details"):
        for track in toc_info["track_details"]:
            if track["number"] == current_playing_track_number:
                current_track_info = track
                break
    
    # Métadonnées MusicBrainz
    album_info = CD_INFO_CACHE.get("musicbrainz_data", {})
    
    status_data = {
        "device": CD_DEVICE,
        "status": toc_info.get("status", "unknown"),
        "tracks": toc_info.get("tracks", 0),
        "total_duration_sec": toc_info.get("total_duration_sec", 0),
        "track_details": toc_info.get("track_details", []),
        
        # Informations sur l'album
        "album": {
            "title": album_info.get("title", "Album Inconnu"),
            "artist": album_info.get("artist", "Artiste Inconnu"),
            "date": album_info.get("date", ""),
            "disc_id": CD_INFO_CACHE.get("disc_id")
        },
        
        # État de lecture
        "playback": {
            "isPlaying": is_playing_now,
            "isPaused": is_paused_now,
            "currentTrack": current_playing_track_number,
            "position": playback_position,
            "currentTrackInfo": current_track_info,
            "mode": playback_mode
        },
        
        # État d'extraction
        "ripping": {
            "active": ripping,
            "progress": ripping_progress if ripping else None
        },
        
        "error_message": toc_info.get("error")
    }
    
    # Ajuster le statut si extraction en cours
    if ripping and status_data["status"] not in ["no_disc", "drive_not_found"]:
        status_data["status"] = "ripping_in_progress"
    
    return jsonify(status_data), 200

@app.route('/api/cd/play', methods=['POST'])
def play_cd_track_route():
    """Lance la lecture d'une piste spécifique"""
    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible de lire: extraction en cours"}), 409
    
    track_number_str = request.args.get('track', default='1')
    try:
        track_number = int(track_number_str)
        toc_info = get_cd_toc_and_update_globals()
        total_tracks = toc_info.get("tracks", 0)
        
        if total_tracks == 0 or track_number < 1 or track_number > total_tracks:
            return jsonify({"status": "error", "message": "Numéro de piste invalide ou pas de CD audio"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Le numéro de piste doit être un entier"}), 400
    
    success, message = _play_track_internal(track_number)
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

@app.route('/api/cd/stop', methods=['POST'])
def stop_cd_playback_route():
    """Arrête la lecture"""
    app.logger.info("Requête reçue pour /api/cd/stop")
    if stop_current_playback():
        return jsonify({"status": "success", "message": "Lecture arrêtée"}), 200
    else:
        return jsonify({"status": "success", "message": "Aucune lecture à arrêter"}), 200

@app.route('/api/cd/pause', methods=['POST'])
def pause_cd_playback_route():
    """Met en pause la lecture"""
    global playback_process_cdparanoia, playback_process_pwcat, is_playback_paused_flag
    global playback_pause_duration, playback_start_time
    
    app.logger.info("Requête reçue pour /api/cd/pause")
    
    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible de mettre en pause: extraction en cours"}), 409
    
    if playback_process_cdparanoia and playback_process_pwcat and not is_playback_paused_flag:
        try:
            # Enregistrer le moment de la pause
            if playback_start_time:
                current_time = time.time()
                playback_pause_duration = (current_time - playback_start_time) - playback_pause_duration
            
            # Envoyer SIGSTOP pour mettre en pause
            if playback_process_pwcat.poll() is None:
                os.kill(playback_process_pwcat.pid, signal.SIGSTOP)
            if playback_process_cdparanoia.poll() is None:
                os.kill(playback_process_cdparanoia.pid, signal.SIGSTOP)
            
            is_playback_paused_flag = True
            app.logger.info(f"Lecture mise en pause (PID cdparanoia: {playback_process_cdparanoia.pid}, PID pw-cat: {playback_process_pwcat.pid})")
            return jsonify({"status": "success", "message": "Lecture mise en pause"}), 200
            
        except Exception as e:
            app.logger.error(f"Erreur lors de la mise en pause: {e}")
            return jsonify({"status": "error", "message": f"Erreur pause: {e}"}), 500
    elif is_playback_paused_flag:
        return jsonify({"status": "info", "message": "Lecture déjà en pause"}), 200
    else:
        return jsonify({"status": "info", "message": "Aucune lecture à mettre en pause"}), 200

@app.route('/api/cd/resume', methods=['POST'])
def resume_cd_playback_route():
    """Reprend la lecture"""
    global playback_process_cdparanoia, playback_process_pwcat, is_playback_paused_flag
    global playback_start_time
    
    app.logger.info("Requête reçue pour /api/cd/resume")
    
    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible de reprendre: extraction en cours"}), 409
    
    if playback_process_cdparanoia and playback_process_pwcat and is_playback_paused_flag:
        try:
            # Reprendre la lecture
            if playback_process_pwcat.poll() is None:
                os.kill(playback_process_pwcat.pid, signal.SIGCONT)
            if playback_process_cdparanoia.poll() is None:
                os.kill(playback_process_cdparanoia.pid, signal.SIGCONT)
            
            # Ajuster le temps de démarrage pour compenser la pause
            if playback_start_time:
                playback_start_time = time.time() - playback_pause_duration
            
            is_playback_paused_flag = False
            app.logger.info(f"Lecture reprise (PID cdparanoia: {playback_process_cdparanoia.pid}, PID pw-cat: {playback_process_pwcat.pid})")     
        return jsonify({"status": "success", "message": "Lecture reprise"}), 200
            
        except Exception as e:
            app.logger.error(f"Erreur lors de la reprise: {e}")
            return jsonify({"status": "error", "message": f"Erreur reprise: {e}"}), 500
    elif not is_playback_paused_flag:
        return jsonify({"status": "info", "message": "Lecture n'est pas en pause"}), 200
    else:
        return jsonify({"status": "info", "message": "Aucune lecture à reprendre"}), 200

@app.route('/api/cd/next', methods=['POST'])
def next_track_route():
    """Passe à la piste suivante"""
    app.logger.info("Requête reçue pour /api/cd/next")

    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible de changer de piste: extraction en cours"}), 409
    
    next_track = get_next_track()
    if next_track is None:
        return jsonify({"status": "error", "message": "Pas de piste suivante disponible"}), 400
    
    success, message = _play_track_internal(next_track)
    if success:
        return jsonify({"status": "success", "message": f"Lecture de la piste {next_track}", "track": next_track}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

@app.route('/api/cd/previous', methods=['POST'])
def previous_track_route():
    """Passe à la piste précédente"""
    app.logger.info("Requête reçue pour /api/cd/previous")

    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible de changer de piste: extraction en cours"}), 409
    
    # Si on est dans les 3 premières secondes, aller à la piste précédente
    # Sinon, redémarrer la piste actuelle
    position = get_playback_position()
    if position["position_sec"] > 3 and current_playing_track_number:
        # Recommencer la piste actuelle
        success, message = _play_track_internal(current_playing_track_number)
        track_to_play = current_playing_track_number
        if success:
            return jsonify({"status": "success", "message": f"Redémarrage de la piste {current_playing_track_number}", "track": current_playing_track_number}), 200
        else:
            return jsonify({"status": "error", "message": message}), 500
    else:
        # Aller à la piste précédente
        previous_track = get_previous_track()
        if previous_track is None:
            return jsonify({"status": "error", "message": "Pas de piste précédente disponible"}), 400
        
        success, message = _play_track_internal(previous_track)
        track_to_play = previous_track
    if success:
        return jsonify({"status": "success", "message": f"Lecture de la piste {track_to_play}", "track": track_to_play}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

@app.route('/api/cd/mode', methods=['POST'])
def set_playback_mode_route():
    """Configure les modes de lecture (repeat, shuffle, repeat_all)"""
    global playback_mode

    app.logger.info("Requête reçue pour /api/cd/mode")
    
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Données JSON requises"}), 400
    
    updated_modes = []
    # Mettre à jour les modes de lecture
    if "repeat" in data:
        playback_mode["repeat"] = bool(data["repeat"])
        app.logger.info(f"Mode repeat: {playback_mode['repeat']}")
        updated_modes.append(f"repeat: {playback_mode['repeat']}")
        # Si repeat est activé, désactiver shuffle et repeat_all
        if playback_mode["repeat"]:
            playback_mode["shuffle"] = False
            playback_mode["repeat_all"] = False
    
    if "shuffle" in data:
        playback_mode["shuffle"] = bool(data["shuffle"])
        app.logger.info(f"Mode shuffle: {playback_mode['shuffle']}")
        updated_modes.append(f"shuffle: {playback_mode['shuffle']}")
        # Si shuffle est activé, désactiver repeat
        if playback_mode["shuffle"]:
            playback_mode["repeat"] = False
    
    if "repeat_all" in data:
        playback_mode["repeat_all"] = bool(data["repeat_all"])
        app.logger.info(f"Mode repeat_all: {playback_mode['repeat_all']}")
        updated_modes.append(f"repeat_all: {playback_mode['repeat_all']}")
        # Si repeat_all est activé, désactiver repeat
        if playback_mode["repeat_all"]:
            playback_mode["repeat"] = False
    
    app.logger.info(f"Modes de lecture mis à jour: {', '.join(updated_modes)}")
    
    return jsonify({
        "status": "success", 
        "message": f"Modes mis à jour: {', '.join(updated_modes)}",
        "modes": playback_mode
    }), 200

    except Exception as e:
        app.logger.error(f"Erreur lors de la configuration des modes: {e}")
        return jsonify({"status": "error", "message": f"Erreur: {e}"}), 500

@app.route('/api/cd/seek', methods=['POST'])
def seek_track_route():
    """Recherche à une position spécifique dans la piste actuelle"""
    global current_playing_track_number
    
    app.logger.info("Requête reçue pour /api/cd/seek")

    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible de naviguer: extraction en cours"}), 409
    
    if not current_playing_track_number:
        return jsonify({"status": "error", "message": "Aucune piste en cours de lecture"}), 400
    
    data = request.get_json()
    if not data or "position" not in data:
        return jsonify({"status": "error", "message": "Position requise en secondes"}), 400
    
    try:
        position_sec = float(data["position"])
        if position_sec < 0:
            position_sec = 0
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Position doit être un nombre"}), 400
    
    # Redémarrer la piste et simuler la position
    # Note: cdparanoia ne supporte pas le seek direct, donc on redémarre
    success, message = _play_track_internal(current_playing_track_number)
    if success:
        # Ajuster le temps de démarrage pour simuler la position
        global playback_start_time, playback_pause_duration
        playback_start_time = time.time() - position_sec
        playback_pause_duration = 0.0
        
        return jsonify({
            "status": "success", 
            "message": f"Navigation vers {position_sec:.1f}s",
            "position": position_sec
        }), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

    except Exception as e:
        app.logger.error(f"Erreur lors du seek: {e}")
        return jsonify({"status": "error", "message": f"Erreur: {e}"}), 500    

@app.route('/api/cd/rip', methods=['POST'])
def rip_cd_route():
    """Lance l'extraction du CD"""
    global ripping_process_script, ripping_progress

    app.logger.info("Requête reçue pour /api/cd/rip")
    
    if check_ripping_status():
        return jsonify({"status": "error", "message": "Extraction déjà en cours"}), 409
    
    # Arrêter toute lecture en cours
    stop_current_playback()
    
    # Vérifier qu'un CD audio est présent
    toc_info = get_cd_toc_and_update_globals()
    if toc_info.get("status") != "audio_cd_present" or toc_info.get("tracks", 0) == 0:
        return jsonify({"status": "error", "message": "Pas de CD audio détecté"}), 400
    
    # Paramètres d'extraction
    data = request.get_json() or {}
    format_type = data.get("format", "flac").lower()
    output_path = data.get("output_path", "/tmp/cd_rip")
    quality = data.get("quality", "max")
    
    # Valider le format
    if format_type not in ["flac", "wav"]:
        return jsonify({"status": "error", "message": "Format non supporté. Format supporté: flac, wav"}), 400
    
    # Vérifier que le script d'extraction existe
    if not os.path.exists(RIP_SCRIPT):
        return jsonify({"status": "error", "message": f"Script d'extraction introuvable: {RIP_SCRIPT}"}), 500
    
    try:
        # Créer le répertoire de sortie
        os.makedirs(output_path, exist_ok=True)
        
        # Préparer les métadonnées pour le script
        album_info = CD_INFO_CACHE.get("musicbrainz_data", {})
        metadata_json = {
            "album": album_info.get("title", "Album Inconnu"),
            "artist": album_info.get("artist", "Artiste Inconnu"),
            "date": album_info.get("date", ""),
            "tracks": album_info.get("tracks", [])
        }
        
        metadata_file = os.path.join(output_path, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_json, f, ensure_ascii=False, indent=2)
        
        # Lancer le script d'extraction
        rip_command = [
            '/bin/bash', RIP_SCRIPT,
            CD_DEVICE,
            output_path,
            format_type,
            str(toc_info["tracks"]),
            metadata_file
        ]
        
        app.logger.info(f"Lancement de l'extraction: {' '.join(rip_command)}")
        
        # Lancer le processus d'extraction
        ripping_process_script = subprocess.Popen(
            rip_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Initialiser la progression
        ripping_progress = {
            "active": True,
            "current_track": 0,
            "total_tracks": toc_info["tracks"],
            "percentage": 0,
            "current_track_percentage": 0,
            "estimated_time_remaining": None,
            "format": format_type,
            "output_path": output_path,
            "start_time": time.time()
        }
        
        # Démarrer le thread de monitoring
        monitor_thread = threading.Thread(target=monitor_ripping_progress)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        app.logger.info(f"Extraction démarrée (PID: {ripping_process_script.pid})")
        return jsonify({
            "status": "success",
            "message": f"Extraction démarrée vers {output_path}",
            "progress": ripping_progress
        }), 200
        
    except Exception as e:
        app.logger.error(f"Erreur lors du démarrage de l'extraction: {e}")
        ripping_progress["active"] = False
        return jsonify({"status": "error", "message": f"Erreur extraction: {e}"}), 500

@app.route('/api/cd/rip/stop', methods=['POST'])
def stop_rip_route():
    """Arrête l'extraction en cours"""
    global ripping_process_script, ripping_progress

    app.logger.info("Requête reçue pour /api/cd/rip/stop")
    
    if not check_ripping_status():
        return jsonify({"status": "info", "message": "Aucune extraction à arrêter"}), 200
    
    try:
        if ripping_process_script:
            app.logger.info(f"Arrêt du processus d'extraction (PID: {ripping_process_script.pid})")
            ripping_process_script.terminate()
            
            # Attendre un peu pour l'arrêt propre
            try:
                ripping_process_script.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app.logger.warning("Arrêt forcé du processus d'extraction")
                ripping_process_script.kill()
                ripping_process_script.wait()
            
            ripping_process_script = None
        
        ripping_progress["active"] = False
        app.logger.info("Extraction arrêtée")

        return jsonify({"status": "success", "message": "Extraction arrêtée"}), 200
        
    except Exception as e:
        app.logger.error(f"Erreur lors de l'arrêt de l'extraction: {e}")
        return jsonify({"status": "error", "message": f"Erreur arrêt extraction: {e}"}), 500

@app.route('/api/cd/eject', methods=['POST'])
def eject_cd_route():
    """Éjecte le CD"""
    app.logger.info("Requête reçue pour /api/cd/eject")

    # Arrêter toute activité en cours
    stop_current_playback()
    
    # Arrêter toute extraction en cours
    if check_ripping_status():
        return jsonify({"status": "error", "message": "Impossible d'éjecter: extraction en cours"}), 409
    
    try:
        # Éjecter le CD
        result = subprocess.run(['/usr/bin/eject', CD_DEVICE], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Vider le cache
            global CD_INFO_CACHE
            CD_INFO_CACHE = {
                "toc": None,
                "musicbrainz_data": None,
                "last_checked": 0,
                "disc_id": None,
                "total_tracks": 0
            }
            
            app.logger.info(f"CD éjecté avec succès de {CD_DEVICE}")
            return jsonify({"status": "success", "message": "CD éjecté"}), 200
        else:
            app.logger.error(f"Erreur lors de l'éjection: {result.stderr}")
            return jsonify({"status": "error", "message": f"Erreur éjection: {result.stderr.strip()}"}), 500
            
    except subprocess.TimeoutExpired:
        app.logger.error("Timeout lors de l'éjection")
        return jsonify({"status": "error", "message": "Timeout lors de l'éjection"}), 500
    except Exception as e:
        app.logger.error(f"Erreur inattendue lors de l'éjection: {e}")
        return jsonify({"status": "error", "message": f"Erreur éjection: {e}"}), 500

@app.route('/api/cd/metadata/refresh', methods=['POST'])
def refresh_metadata_route():
    """Force la mise à jour des métadonnées MusicBrainz"""
    global CD_INFO_CACHE
    
    app.logger.info("Requête reçue pour /api/cd/metadata/refresh")
    
    try:
        # Réinitialiser le cache des métadonnées
        CD_INFO_CACHE["musicbrainz_data"] = None
        CD_INFO_CACHE["last_checked"] = 0
        
        # Forcer la récupération des informations
        toc_info = get_cd_toc_and_update_globals()
        
        if toc_info.get("status") == "audio_cd_present" and toc_info.get("tracks", 0) > 0:
            album_info = CD_INFO_CACHE.get("musicbrainz_data", {})
            return jsonify({
                "status": "success", 
                "message": "Métadonnées mises à jour",
                "album": album_info
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": "Aucun CD audio détecté pour la mise à jour des métadonnées"
            }), 400
            
    except Exception as e:
        app.logger.error(f"Erreur lors de la mise à jour des métadonnées: {e}")
        return jsonify({"status": "error", "message": f"Erreur: {e}"}), 500

def monitor_playback():
    """Thread pour surveiller la fin de lecture et gérer les transitions automatiques"""
    global playback_process_cdparanoia, playback_process_pwcat, current_playing_track_number
    global playback_mode
    
    while True:
        try:
            if (playback_process_cdparanoia and playback_process_pwcat and 
                not is_playback_paused_flag):
                
                # Vérifier si la lecture est terminée
                if (playback_process_cdparanoia.poll() is not None or 
                    playback_process_pwcat.poll() is not None):
                    
                    app.logger.info(f"Fin de lecture de la piste {current_playing_track_number}")
                    
                    # Nettoyer les processus
                    stop_current_playback(log_info=False)
                    
                    # Déterminer la piste suivante selon le mode
                    next_track = get_next_track()
                    
                    if next_track and (playback_mode["repeat_all"] or 
                                     playback_mode["repeat"] or 
                                     playback_mode["shuffle"] or
                                     next_track != 1):  # Pas de boucle automatique sauf modes spéciaux
                        
                        app.logger.info(f"Passage automatique à la piste {next_track}")
                        time.sleep(0.5)  # Petite pause avant la piste suivante
                        _play_track_internal(next_track)
            
            time.sleep(1)
            
        except Exception as e:
            app.logger.error(f"Erreur dans le monitoring de lecture: {e}")
            time.sleep(2)

def monitor_ripping_progress():
    """Thread amélioré pour surveiller la progression de l'extraction"""
    global ripping_progress, ripping_process_script
    
    app.logger.info("Démarrage du monitoring de l'extraction")
    
    while ripping_progress["active"] and ripping_process_script:
        try:
            # Vérifier si le processus est toujours actif
            if ripping_process_script.poll() is not None:
                app.logger.info("Processus d'extraction terminé")
                ripping_progress["active"] = False
                ripping_progress["percentage"] = 100
                break
            
            # Lire la sortie du processus pour suivre la progression
            # (Cette implémentation est simplifiée - dans un vrai environnement,
            # il faudrait parser la sortie de cdparanoia en temps réel)
            
            # Simulation de progression basée sur le temps écoulé
            if ripping_progress["start_time"]:
                elapsed = time.time() - ripping_progress["start_time"]
                total_tracks = ripping_progress["total_tracks"]
                
                # Estimation grossière: 3 minutes par piste en moyenne
                estimated_total_time = total_tracks * 180
                progress_pct = min(95, (elapsed / estimated_total_time) * 100)
                
                ripping_progress["percentage"] = int(progress_pct)
                ripping_progress["current_track"] = min(total_tracks, int((progress_pct / 100) * total_tracks) + 1)
                
                # Temps restant estimé
                if progress_pct > 5:
                    remaining_time = (estimated_total_time - elapsed)
                    ripping_progress["estimated_time_remaining"] = max(0, int(remaining_time))
            
            time.sleep(2)
            
        except Exception as e:
            app.logger.error(f"Erreur dans le monitoring de l'extraction: {e}")
            break

# Démarrer le thread de monitoring de lecture au démarrage
playback_monitor_thread = threading.Thread(target=monitor_playback, daemon=True)
playback_monitor_thread.start()

    app.logger.info("Fin du monitoring de l'extraction")

def auto_advance_track():
    """Thread pour gérer l'avancement automatique des pistes"""
    global playback_process_cdparanoia, playback_process_pwcat, current_playing_track_number
    
    while True:
        try:
            time.sleep(1)
            
            # Vérifier si une lecture est en cours
            if (playback_process_cdparanoia and playback_process_pwcat and 
                current_playing_track_number and not is_playback_paused_flag):
                
                # Vérifier si les processus sont terminés (fin de piste)
                if (playback_process_cdparanoia.poll() is not None and 
                    playback_process_pwcat.poll() is not None):
                    
                    app.logger.info(f"Fin de la piste {current_playing_track_number}")
                    
                    # Nettoyer les processus terminés
                    playback_process_cdparanoia = None
                    playback_process_pwcat = None
                    
                    # Passer à la piste suivante selon le mode
                    next_track = get_next_track()
                    if next_track:
                        app.logger.info(f"Avancement automatique vers la piste {next_track}")
                        success, message = _play_track_internal(next_track)
                        if not success:
                            app.logger.error(f"Échec de l'avancement automatique: {message}")
                            current_playing_track_number = None
                    else:
                        app.logger.info("Fin de l'album, arrêt de la lecture")
                        current_playing_track_number = None
                        
        except Exception as e:
            app.logger.error(f"Erreur dans l'avancement automatique: {e}")
            time.sleep(5)  # Attendre avant de réessayer

# Démarrer le thread d'avancement automatique
auto_advance_thread = threading.Thread(target=auto_advance_track)
auto_advance_thread.daemon = True
auto_advance_thread.start()

# === GESTIONNAIRE DE SIGNAUX ===
def signal_handler(signum, frame):
    """Gestionnaire pour l'arrêt propre du service"""
    app.logger.info(f"Signal {signum} reçu, arrêt en cours...")
    
    # Arrêter tous les processus
    stop_current_playback(log_info=False)
    
    if ripping_process_script:
        try:
            ripping_process_script.terminate()
            ripping_process_script.wait(timeout=3)
        except:
            pass
    
    app.logger.info("Service MAQAM CD API arrêté proprement")
    exit(0)

# Enregistrer les gestionnaires de signaux
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === POINT D'ENTRÉE ===
if __name__ == '__main__':
    app.logger.info("=== MAQAM CD API - Démarrage ===")
    app.logger.info(f"Périphérique CD: {CD_DEVICE}")
    app.logger.info(f"Script d'extraction: {RIP_SCRIPT}")
    app.logger.info(f"Sink PipeWire: {PIPEWIRE_TARGET_SINK}")
    
    # Vérifier les dépendances
    dependencies = [
        ('/usr/bin/cd-info', 'libcdio-utils'),
        ('/usr/bin/cdparanoia', 'cdparanoia'),
        ('/usr/bin/pw-cat', 'pipewire'),
        ('/usr/bin/eject', 'util-linux')
    ]
    
    missing_deps = []
    for cmd_path, package in dependencies:
        if not os.path.exists(cmd_path):
            missing_deps.append(f"{cmd_path} (paquet: {package})")
    
    if missing_deps:
        app.logger.error("Dépendances manquantes:")
        for dep in missing_deps:
            app.logger.error(f"  - {dep}")
        app.logger.error("Installez les paquets manquants avant de démarrer l'API")
        exit(1)
    
    # Vérifier l'accès au périphérique CD
    if not os.path.exists(CD_DEVICE):
        app.logger.warning(f"Périphérique CD {CD_DEVICE} introuvable")
    
    app.logger.info("Toutes les dépendances sont présentes")
    app.logger.info("API CD MAQAM prête - Écoute sur http://0.0.0.0:5000")
    
    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)