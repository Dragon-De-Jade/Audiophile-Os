#!/usr/bin/env python3
"""
maqam_cd_api.py - Version complète avec toutes les fonctionnalités
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
import platform # Added for system info
from functools import wraps # Added for API key decorator

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
USER_PREFERENCES_FILE = "user_preferences.json" 
DEFAULT_PREFERENCES = {"language": "fr", "theme": "dark"} 
RIP_SCRIPT = "/usr/local/bin/rip_cd.sh"
MUSICBRAINZ_API_BASE = "https://musicbrainz.org/ws/2"
MUSICBRAINZ_USER_AGENT = "MAQAM-Audio-OS/1.0 (charly.laurencin@gmail.com)"
PIPEWIRE_TARGET_SINK = "alsa_output.usb-KHADAS_Tone2_Pro_Tone2_Pro-00.pro-output-0"
EXPECTED_API_KEY = "maqam_secret_key" # Added for API Key Authentication


# === AUDIO SOURCES CONFIGURATION ===
AVAILABLE_AUDIO_SOURCES = [
    {"id": "alsa_card0_analog", "name": "Built-in Audio (Analog)", "type": "alsa", "status": "available", "device_string": "hw:0,0", "config_options": {"volume": 100, "exclusive_mode": False, "mute": False}},
    {"id": "usb_dac_xyz", "name": "My USB DAC", "type": "usb", "status": "available", "device_string": "hw:1,0", "config_options": {"samplerate": 96000, "bitdepth": 24, "volume": 90}},
    {"id": "network_stream_hq", "name": "HQ Network Stream", "type": "network", "status": "unavailable", "url": "http://example.com/stream", "config_options": {"buffer_size_ms": 500, "reconnect_attempts": 3}},
    {"id": "cd_player", "name": "CD Player (MAQAM)", "type": "internal", "status": "available", "device_string": CD_DEVICE, "config_options": {"enable_dac_passthrough": True, "oversampling": "2x"}}
]
CURRENT_ACTIVE_SOURCE_ID = "alsa_card0_analog" # Default active source


# === VARIABLES GLOBALES === (Existing global variables)
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


# === AUTHENTICATION DECORATOR ===
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == EXPECTED_API_KEY:
            return f(*args, **kwargs)
        else:
            app.logger.warning(f"Accès non autorisé à {request.path}. Clé API manquante ou invalide.")
            return jsonify({"status": "error", "message": "Non autorisé: Clé API manquante ou invalide"}), 401
    return decorated_function

# === USER PREFERENCES FUNCTIONS ===

def load_preferences() -> Dict:
    """Charge les préférences utilisateur depuis le fichier JSON."""
    prefs = DEFAULT_PREFERENCES.copy() 
    if os.path.exists(USER_PREFERENCES_FILE):
        try:
            with open(USER_PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                loaded_prefs = json.load(f)
            for key in DEFAULT_PREFERENCES:
                if key in loaded_prefs:
                    prefs[key] = loaded_prefs[key]
            app.logger.info(f"Préférences chargées et fusionnées depuis {USER_PREFERENCES_FILE}")
        except (json.JSONDecodeError, IOError) as e:
            app.logger.error(f"Erreur lors du chargement des préférences depuis {USER_PREFERENCES_FILE}: {e}. Utilisation des défauts.")
    else:
        app.logger.info(f"Fichier de préférences {USER_PREFERENCES_FILE} non trouvé, utilisation des défauts.")
    return prefs

def save_preferences(prefs_dict: Dict) -> bool:
    """Sauvegarde les préférences utilisateur dans le fichier JSON."""
    try:
        valid_prefs_to_save = {key: prefs_dict[key] for key in DEFAULT_PREFERENCES if key in prefs_dict}
        with open(USER_PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(valid_prefs_to_save, f, ensure_ascii=False, indent=4)
        app.logger.info(f"Préférences sauvegardées dans {USER_PREFERENCES_FILE}: {valid_prefs_to_save}")
        return True
    except IOError as e:
        app.logger.error(f"Erreur lors de la sauvegarde des préférences dans {USER_PREFERENCES_FILE}: {e}")
        return False

# === SYSTEM AND PREFERENCES API ROUTES ===

@app.route('/api/system/info', methods=['GET'])
def system_info_route():
    """Retourne les informations de base du système."""
    app.logger.info("Requête reçue pour /api/system/info")
    uptime_seconds_val = None
    uptime_formatted_str = "N/A"
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds_val = float(f.readline().split()[0])
            days = int(uptime_seconds_val // (24 * 3600))
            hours = int((uptime_seconds_val % (24 * 3600)) // 3600)
            minutes = int((uptime_seconds_val % 3600) // 60)
            seconds = int(uptime_seconds_val % 60)
            uptime_formatted_str = f"{days}j {hours:02}h {minutes:02}m {seconds:02}s"
    except Exception as e:
        app.logger.error(f"Impossible de lire ou parser l'uptime depuis /proc/uptime: {e}")

    system_info = {
        "hostname": platform.node(),
        "os_version": platform.platform(),
        "kernel_version": platform.release(),
        "uptime_seconds": uptime_seconds_val,
        "uptime_formatted": uptime_formatted_str
    }
    return jsonify(system_info), 200

@app.route('/api/system/shutdown', methods=['POST'])
@require_api_key
def system_shutdown_route():
    """Simule une demande d'arrêt du système (ne l'exécute pas)."""
    app.logger.info("Requête reçue pour /api/system/shutdown (simulée)")
    return jsonify({"status": "success", "message": "Shutdown command received (simulated)"}), 200

@app.route('/api/preferences', methods=['GET'])
@require_api_key # Protected as per instructions
def get_preferences_route():
    """Retourne les préférences utilisateur actuelles."""
    app.logger.info("Requête reçue pour GET /api/preferences")
    preferences = load_preferences()
    return jsonify(preferences), 200

@app.route('/api/preferences', methods=['POST'])
@require_api_key
def set_preferences_route():
    """Met à jour les préférences utilisateur."""
    app.logger.info("Requête reçue pour POST /api/preferences")
    new_prefs_data = request.get_json()
    if not new_prefs_data:
        app.logger.warning("Requête POST /api/preferences reçue sans données JSON.")
        return jsonify({"status": "error", "message": "Données JSON requises"}), 400

    current_preferences = load_preferences()
    updated_any_valid_key = False
    
    for key, value in new_prefs_data.items():
        if key in DEFAULT_PREFERENCES: 
            if current_preferences.get(key) != value:
                current_preferences[key] = value
                app.logger.info(f"Préférence '{key}' mise à jour à '{value}'")
                updated_any_valid_key = True
        else:
            app.logger.warning(f"Clé de préférence inconnue '{key}' ignorée lors de la mise à jour.")
            
    if updated_any_valid_key:
        if save_preferences(current_preferences):
            return jsonify(current_preferences), 200
        else:
            return jsonify({"status": "error", "message": "Échec de la sauvegarde des préférences"}), 500
    else:
        app.logger.info("Aucune préférence valide n'a été modifiée (valeurs identiques ou clés inconnues).")
        return jsonify(current_preferences), 200

# === AUDIO SOURCE MANAGEMENT ===

def get_source_by_id(source_id: str) -> Optional[Dict]:
    """Récupère une source audio par son ID."""
    for source in AVAILABLE_AUDIO_SOURCES:
        if source["id"] == source_id:
            return source
    return None

@app.route('/api/audio/sources', methods=['GET'])
def get_audio_sources():
    """Retourne la liste des sources audio disponibles et la source active."""
    app.logger.info("Requête reçue pour GET /api/audio/sources")
    return jsonify({
        "sources": AVAILABLE_AUDIO_SOURCES,
        "current_active_source_id": CURRENT_ACTIVE_SOURCE_ID
    }), 200

@app.route('/api/audio/source/active', methods=['GET'])
def get_active_audio_source():
    """Retourne les détails de la source audio active."""
    app.logger.info("Requête reçue pour GET /api/audio/source/active")
    active_source = get_source_by_id(CURRENT_ACTIVE_SOURCE_ID)
    if active_source:
        return jsonify(active_source), 200
    else:
        app.logger.error(f"Source active ID '{CURRENT_ACTIVE_SOURCE_ID}' non trouvée dans AVAILABLE_AUDIO_SOURCES.")
        return jsonify({"status": "error", "message": "Source active configurée non valide ou introuvable."}), 404


@app.route('/api/audio/source/active', methods=['POST'])
@require_api_key
def set_active_audio_source():
    """Définit la source audio active."""
    global CURRENT_ACTIVE_SOURCE_ID
    app.logger.info("Requête reçue pour POST /api/audio/source/active")
    data = request.get_json()
    if not data or "source_id" not in data:
        return jsonify({"status": "error", "message": "JSON avec 'source_id' requis."}), 400
    
    new_source_id = data["source_id"]
    target_source = get_source_by_id(new_source_id)
    
    if not target_source:
        app.logger.warning(f"Tentative de définition d'une source active inexistante: {new_source_id}")
        return jsonify({"status": "error", "message": f"Source ID '{new_source_id}' non trouvée."}), 400
        
    if target_source.get("status") == "unavailable":
        app.logger.warning(f"Tentative d'activation d'une source non disponible: {new_source_id}")
        return jsonify({"status": "error", "message": f"Source '{new_source_id}' non disponible."}), 400

    CURRENT_ACTIVE_SOURCE_ID = new_source_id
    for src in AVAILABLE_AUDIO_SOURCES:
        if src["id"] == new_source_id:
            src["status"] = "active"
        elif src["status"] == "active": 
             src["status"] = "available"

    app.logger.info(f"Source audio active changée à: {new_source_id}")
    return jsonify({"status": "success", "message": f"Source audio active définie à '{new_source_id}'.", "active_source": target_source}), 200


@app.route('/api/audio/source/<source_id>/config', methods=['GET'])
def get_source_config(source_id: str):
    """Retourne la configuration d'une source audio spécifique."""
    app.logger.info(f"Requête reçue pour GET /api/audio/source/{source_id}/config")
    source = get_source_by_id(source_id)
    if source:
        return jsonify(source.get("config_options", {})), 200
    else:
        return jsonify({"status": "error", "message": f"Source ID '{source_id}' non trouvée."}), 404

@app.route('/api/audio/source/<source_id>/config', methods=['POST'])
@require_api_key
def set_source_config(source_id: str):
    """Met à jour la configuration d'une source audio spécifique (stub)."""
    app.logger.info(f"Requête reçue pour POST /api/audio/source/{source_id}/config")
    source = get_source_by_id(source_id)
    if not source:
        return jsonify({"status": "error", "message": f"Source ID '{source_id}' non trouvée."}), 404
        
    new_config_data = request.get_json()
    if not new_config_data:
        return jsonify({"status": "error", "message": "Données JSON de configuration requises."}), 400
        
    if "config_options" not in source: 
        source["config_options"] = {}
        
    updated_keys = []
    for key, value in new_config_data.items():
        source["config_options"][key] = value 
        updated_keys.append(key)

    if updated_keys:
        app.logger.info(f"Configuration mise à jour pour la source '{source_id}'. Clés modifiées: {', '.join(updated_keys)}. Nouvelle config: {source['config_options']}")
    else:
        app.logger.info(f"Aucune configuration modifiée pour la source '{source_id}'.")
    
    return jsonify({"status": "success", "message": f"Configuration pour '{source_id}' mise à jour.", "updated_source": source}), 200

# === LYRION API ROUTES (STUBS) ===

@app.route('/api/lyrion/status', methods=['GET'])
def lyrion_status():
    app.logger.info("Lyrion status requested (stub)")
    return jsonify({"status": "ok", "lyrion_state": "simulated_idle", "message": "Lyrion status (stub)"}), 200

@app.route('/api/lyrion/command', methods=['POST'])
@require_api_key
def lyrion_command():
    data = request.get_json()
    command = data.get("command", "no_command_specified")
    params = data.get("params", [])
    app.logger.info(f"Lyrion command received (stub): {command}, params: {params}")
    return jsonify({"status": "success", "message": "Lyrion command processed (stub)", "details": {"command_sent": command, "params_received": params}}), 200

# === SQUEEZELITE API ROUTES (STUBS) ===

@app.route('/api/squeezelite/status', methods=['GET'])
def squeezelite_status():
    app.logger.info("Squeezelite status requested (stub)")
    return jsonify({"status": "ok", "squeezelite_state": "simulated_playing", "current_track": "Simulated Song Title", "message": "Squeezelite status (stub)"}), 200

@app.route('/api/squeezelite/command', methods=['POST'])
@require_api_key
def squeezelite_command():
    data = request.get_json()
    command = data.get("command", "no_command_specified")
    value = data.get("value") 
    app.logger.info(f"Squeezelite command received (stub): {command}, value: {value}")
    return jsonify({"status": "success", "message": "Squeezelite command processed (stub)", "details": {"command_sent": command, "value_received": value}}), 200

# === MUSIC LIBRARY API ROUTES (STUBS) ===

@app.route('/api/library/albums', methods=['GET'])
def library_albums():
    app.logger.info("Request for library albums (stub)")
    return jsonify({"albums": [{"id": "album1", "title": "Simulated Album 1", "artist": "Simulated Artist"}], "message": "Album list (stub)"}), 200

@app.route('/api/library/artists', methods=['GET'])
def library_artists():
    app.logger.info("Request for library artists (stub)")
    return jsonify({"artists": [{"id": "artist1", "name": "Simulated Artist"}], "message": "Artist list (stub)"}), 200

@app.route('/api/library/playlists', methods=['GET'])
def library_playlists():
    app.logger.info("Request for library playlists (stub)")
    return jsonify({"playlists": [{"id": "playlist1", "name": "My Simulated Playlist", "track_count": 5}], "message": "Playlist list (stub)"}), 200

@app.route('/api/library/playlist/<playlist_id>', methods=['GET'])
def library_playlist_detail(playlist_id: str):
    app.logger.info(f"Request for specific playlist (stub): {playlist_id}")
    if playlist_id == "playlist1": 
        return jsonify({"id": playlist_id, "name": "My Simulated Playlist", "tracks": [{"title": "Track A - Simulated"}, {"title": "Track B - Simulated"}], "message": f"Playlist details for {playlist_id} (stub)"}), 200
    else: 
        return jsonify({"id": playlist_id, "name": f"Simulated Playlist {playlist_id}", "tracks": [], "message": f"Playlist details for {playlist_id} (stub)"}), 200


# === FONCTIONS UTILITAIRES CD === 

def calculate_disc_id(toc_data: Dict) -> Optional[str]:
    """Calcule le Disc ID MusicBrainz à partir de la TOC"""
    try:
        if not toc_data.get("track_details"):
            return None
        track_count = len(toc_data["track_details"])
        total_length = sum(track.get("duration_sec", 180) for track in toc_data["track_details"])
        disc_data = f"{track_count}:{total_length}"
        return hashlib.sha1(disc_data.encode()).hexdigest()[:28]
    except Exception as e:
        app.logger.error(f"Erreur lors du calcul du Disc ID: {e}")
        return None

def get_musicbrainz_metadata(disc_id: str, track_count: int) -> Dict:
    """Récupère les métadonnées depuis MusicBrainz"""
    default_mb_response = {
        "title": "Album Inconnu", "artist": "Artiste Inconnu", "date": "",
        "tracks": [{"number": i + 1, "title": f"Piste {i + 1}", "artist": "Artiste Inconnu"} for i in range(track_count)]
    }
    try:
        headers = {"User-Agent": MUSICBRAINZ_USER_AGENT}
        if not disc_id:
            url = f"{MUSICBRAINZ_API_BASE}/release"
            params = {"query": f"tracks:{track_count}", "limit": 1, "fmt": "json"}
        else:
            url = f"{MUSICBRAINZ_API_BASE}/discid/{disc_id}"
            params = {"inc": "releases+recordings", "fmt": "json"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status() 
        data = response.json()
            
        if "releases" in data and data["releases"]:
            release = data["releases"][0]
            artist_name = release.get("artist-credit", [{}])[0].get("name", "Artiste Inconnu") if release.get("artist-credit") else "Artiste Inconnu"
            mb_tracks = []
            if release.get("media") and release["media"][0].get("tracks"):
                for i, track_data in enumerate(release["media"][0]["tracks"]):
                    if i < track_count: 
                        title = track_data.get("title", f"Piste {i+1}") 
                        if track_data.get("recording") and track_data["recording"].get("title"):
                            title = track_data["recording"]["title"] 
                        mb_tracks.append({"number": i + 1, "title": title, "artist": artist_name})
            if not mb_tracks: 
                 mb_tracks = default_mb_response["tracks"]

            return {
                "title": release.get("title", "Album Inconnu"),
                "artist": artist_name,
                "date": release.get("date", ""),
                "tracks": mb_tracks
            }
        app.logger.info(f"Aucune release trouvée sur MusicBrainz pour disc_id: {disc_id} / tracks: {track_count}")
        return default_mb_response
    except requests.exceptions.RequestException as e:
        app.logger.warning(f"Erreur API MusicBrainz: {e}")
        return default_mb_response
    except Exception as e:
        app.logger.error(f"Erreur inattendue lors du traitement des données MusicBrainz: {e}", exc_info=True)
        return default_mb_response

def parse_cd_info_output(output: str) -> Dict:
    """Parse la sortie de cd-info pour extraire les informations détaillées"""
    toc_data = {
        "status": "unknown", "tracks": 0, "track_details": [],
        "total_duration_sec": 0, "error": None
    }
    try:
        lines = output.splitlines()
        track_pattern = re.compile(r'^\s*TRACK\s+(\d+)\s+.*?(\d{2}):(\d{2})\.(\d{2})')
        for line in lines:
            if "No medium found" in line or "No disc in drive" in line:
                toc_data["status"] = "no_disc"; return toc_data
            elif "Disc mode is listed as: CD-DA" in line:
                toc_data["status"] = "audio_cd_present"
            elif "ISO 9660" in line or "UDF" in line:
                toc_data["status"] = "data_cd_present"; return toc_data
            
            match = track_pattern.search(line)
            if match:
                track_num, minutes, seconds, frames = map(int, match.groups())
                duration_sec = minutes * 60 + seconds + (frames / 75.0)
                toc_data["track_details"].append({
                    "number": track_num, "duration_sec": duration_sec,
                    "duration_formatted": f"{minutes:02d}:{seconds:02d}",
                    "title": f"Piste {track_num}", "artist": "Artiste Inconnu"
                })
        toc_data["tracks"] = len(toc_data["track_details"])
        toc_data["total_duration_sec"] = sum(t["duration_sec"] for t in toc_data["track_details"])
        if toc_data["tracks"] == 0 and toc_data["status"] == "audio_cd_present":
            toc_data["status"] = "disc_present_unknown_type" 
    except Exception as e:
        app.logger.error(f"Erreur lors du parsing cd-info: {e}"); toc_data["error"] = str(e)
    return toc_data

def get_cd_toc_and_update_globals() -> Dict:
    """Récupère la TOC du CD et met à jour les variables globales"""
    global CD_INFO_CACHE
    current_time = time.time()
    if not (playback_process_cdparanoia or check_ripping_status()) and \
       CD_INFO_CACHE.get("toc") and (current_time - CD_INFO_CACHE.get("last_checked", 0) < CD_INFO_CACHE_TTL):
        app.logger.debug("Retour des données CD depuis le cache.")
        return CD_INFO_CACHE["toc"]
    
    app.logger.info(f"Récupération des informations CD via cd-info pour {CD_DEVICE}")
    command = ['/usr/bin/cd-info', '-C', CD_DEVICE, '--no-header', '--no-ioctl', '--no-cddb', '--no-analyze', '-T']
    toc_data = {}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        output = result.stdout + "\n" + result.stderr 
        app.logger.debug(f"Sortie cd-info (code {result.returncode}):\n{output.strip()}")
        if result.returncode == 0:
            toc_data = parse_cd_info_output(output)
        else:
            toc_data = {"status": "error_reading_disc", "error": result.stderr.strip() or f"Erreur cd-info (code {result.returncode})"}
    except subprocess.TimeoutExpired:
        toc_data = {"status": "error_timeout", "error": "cd-info timeout"}
    except FileNotFoundError:
        toc_data = {"status": "error_missing_dependency", "error": "cd-info non trouvé (libcdio manquant?)"}
    except Exception as e:
        toc_data = {"status": "error_unexpected", "error": str(e)}
    
    toc_data.setdefault("tracks", 0)
    toc_data.setdefault("track_details", [])
    toc_data.setdefault("status", "unknown") 

    CD_INFO_CACHE.update({
        "toc": toc_data, "last_checked": current_time,
        "total_tracks": toc_data["tracks"]
    })
    
    if toc_data.get("status") == "audio_cd_present" and toc_data["tracks"] > 0:
        disc_id = calculate_disc_id(toc_data)
        CD_INFO_CACHE["disc_id"] = disc_id
        if not CD_INFO_CACHE.get("musicbrainz_data") or CD_INFO_CACHE.get("disc_id_for_mb_data") != disc_id:
            app.logger.info(f"Récupération des métadonnées MusicBrainz pour disc_id: {disc_id}")
            mb_data = get_musicbrainz_metadata(disc_id, toc_data["tracks"])
            CD_INFO_CACHE["musicbrainz_data"] = mb_data
            CD_INFO_CACHE["disc_id_for_mb_data"] = disc_id 

            if mb_data and mb_data.get("tracks"):
                mb_track_map = {t["number"]: t for t in mb_data["tracks"]}
                for track_detail in toc_data["track_details"]:
                    mb_track_info = mb_track_map.get(track_detail["number"])
                    if mb_track_info:
                        track_detail["title"] = mb_track_info.get("title", track_detail["title"])
                        track_detail["artist"] = mb_track_info.get("artist", track_detail["artist"])
    else: 
        CD_INFO_CACHE["musicbrainz_data"] = None
        CD_INFO_CACHE["disc_id_for_mb_data"] = None
    return toc_data

def check_ripping_status() -> bool:
    global ripping_process_script, ripping_progress
    if ripping_process_script is None:
        if ripping_progress.get("active"): 
            app.logger.info("Correcting lingering ripping state: process is None but was active.")
            ripping_progress["active"] = False
        return False
    poll_result = ripping_process_script.poll()
    if poll_result is None: return True
    else: 
        app.logger.info(f"Script d'extraction (PID: {ripping_process_script.pid}) terminé avec code: {poll_result}.")
        ripping_process_script = None; ripping_progress["active"] = False
        if poll_result == 0: ripping_progress["percentage"] = 100
        return False

def stop_current_playback(log_info: bool = True) -> bool:
    global playback_process_cdparanoia, playback_process_pwcat, current_playing_track_number, is_playback_paused_flag, playback_start_time, playback_pause_duration
    stopped_something = False
    if playback_process_pwcat:
        pid = playback_process_pwcat.pid 
        try:
            if playback_process_pwcat.poll() is None: 
                if log_info: app.logger.info(f"Arrêt de pw-cat (PID: {pid}).")
                playback_process_pwcat.terminate(); playback_process_pwcat.wait(timeout=1)
        except subprocess.TimeoutExpired:
            if log_info: app.logger.warning(f"pw-cat (PID: {pid}) timeout, kill forcé.")
            if playback_process_pwcat.poll() is None: playback_process_pwcat.kill()
        except Exception as e:
            if log_info: app.logger.error(f"Erreur arrêt pw-cat (PID: {pid}): {e}")
        playback_process_pwcat = None; stopped_something = True
    if playback_process_cdparanoia:
        pid = playback_process_cdparanoia.pid
        try:
            if playback_process_cdparanoia.poll() is None:
                if log_info: app.logger.info(f"Arrêt de cdparanoia (PID: {pid}).")
                playback_process_cdparanoia.terminate(); playback_process_cdparanoia.wait(timeout=1)
        except subprocess.TimeoutExpired:
            if log_info: app.logger.warning(f"cdparanoia (PID: {pid}) timeout, kill forcé.")
            if playback_process_cdparanoia.poll() is None: playback_process_cdparanoia.kill()
        except Exception as e:
            if log_info: app.logger.error(f"Erreur arrêt cdparanoia (PID: {pid}): {e}")
        playback_process_cdparanoia = None; stopped_something = True
    current_playing_track_number = None; is_playback_paused_flag = False
    playback_start_time = None; playback_pause_duration = 0.0
    if stopped_something and log_info: app.logger.info("Processus de lecture arrêtés et état réinitialisé.")
    elif log_info and not stopped_something: app.logger.debug("stop_current_playback appelé, aucun processus actif.")
    return stopped_something

def get_playback_position() -> Dict:
    if not current_playing_track_number or playback_start_time is None:
        return {"position_sec": 0, "position_formatted": "00:00"}
    current_time = time.time()
    if is_playback_paused_flag: elapsed_seconds = playback_pause_duration 
    else: elapsed_seconds = (current_time - playback_start_time)
    elapsed_seconds = max(0, elapsed_seconds)
    minutes = int(elapsed_seconds // 60); seconds = int(elapsed_seconds % 60)
    return {"position_sec": round(elapsed_seconds, 2), "position_formatted": f"{minutes:02d}:{seconds:02d}"}

def _play_track_internal(track_to_play: int) -> Tuple[bool, str]:
    global playback_process_cdparanoia, playback_process_pwcat, current_playing_track_number, is_playback_paused_flag, playback_start_time, playback_pause_duration
    stop_current_playback(log_info=False)
    app.logger.info(f"Lancement lecture piste: {track_to_play}")
    cmd_cdparanoia = ['/usr/bin/cdparanoia', '-d', CD_DEVICE, str(track_to_play), '-']
    cmd_pwcat = ['/usr/bin/pw-cat', '--playback', '--target', PIPEWIRE_TARGET_SINK, '--format', 'S16LE', '--rate', '44100', '--channels', '2', '--latency', '100ms', '--quality', '4', '-']
    try:
        playback_process_cdparanoia = subprocess.Popen(cmd_cdparanoia, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        playback_process_pwcat = subprocess.Popen(cmd_pwcat, stdin=playback_process_cdparanoia.stdout, stderr=subprocess.PIPE)
        if playback_process_cdparanoia.stdout: playback_process_cdparanoia.stdout.close()
        current_playing_track_number = track_to_play; is_playback_paused_flag = False
        playback_start_time = time.time(); playback_pause_duration = 0.0
        app.logger.info(f"Lecture démarrée: cdparanoia PID {playback_process_cdparanoia.pid}, pw-cat PID {playback_process_pwcat.pid}")
        return True, f"Lecture piste {track_to_play} démarrée."
    except Exception as e:
        app.logger.error(f"Erreur lancement lecture piste {track_to_play}: {e}", exc_info=True)
        stop_current_playback(log_info=False); return False, f"Erreur technique démarrage lecture: {e}"

# === ROUTES API CD ===
@app.route('/api/cd/status', methods=['GET'])
def cd_status_route():
    global playback_process_cdparanoia, is_playback_paused_flag, current_playing_track_number, playback_mode, ripping_progress, CD_INFO_CACHE
    ripping_active_status = check_ripping_status(); toc_info = get_cd_toc_and_update_globals()
    is_playing_now = (playback_process_cdparanoia and playback_process_cdparanoia.poll() is None and playback_process_pwcat and playback_process_pwcat.poll() is None and not is_playback_paused_flag)
    is_paused_now = (playback_process_cdparanoia and playback_process_cdparanoia.poll() is None and playback_process_pwcat and playback_process_pwcat.poll() is None and is_playback_paused_flag)
    playback_position = get_playback_position(); current_track_info_obj = None
    if current_playing_track_number and toc_info.get("track_details"):
        for track in toc_info["track_details"]:
            if track["number"] == current_playing_track_number: current_track_info_obj = track; break
    album_info_obj = CD_INFO_CACHE.get("musicbrainz_data", {})
    status_data = {
        "device": CD_DEVICE, "status": toc_info.get("status", "unknown"), "tracks": toc_info.get("tracks", 0),
        "total_duration_sec": toc_info.get("total_duration_sec", 0), "track_details": toc_info.get("track_details", []),
        "album": {"title": album_info_obj.get("title", "Album Inconnu"), "artist": album_info_obj.get("artist", "Artiste Inconnu"), "date": album_info_obj.get("date", ""), "disc_id": CD_INFO_CACHE.get("disc_id")},
        "playback": {"isPlaying": is_playing_now, "isPaused": is_paused_now, "currentTrackNumber": current_playing_track_number, "position": playback_position, "currentTrackInfo": current_track_info_obj, "mode": playback_mode},
        "ripping": {"active": ripping_active_status, "progress": ripping_progress if ripping_active_status else None},
        "error_message": toc_info.get("error")}
    if ripping_active_status and status_data["status"] not in ["no_disc", "drive_not_found", "error_reading_disc"]: status_data["status"] = "ripping_in_progress"
    return jsonify(status_data), 200

@app.route('/api/cd/play', methods=['POST'])
def play_cd_track_route():
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible de lire: extraction en cours"}), 409
    track_number_str = request.args.get('track', default='1', type=str)
    try:
        track_number = int(track_number_str); toc_info = get_cd_toc_and_update_globals(); total_tracks = toc_info.get("tracks", 0)
        if total_tracks == 0 or not (1 <= track_number <= total_tracks): return jsonify({"status": "error", "message": "Numéro de piste invalide ou pas de CD audio"}), 400
    except ValueError: return jsonify({"status": "error", "message": "Le numéro de piste doit être un entier valide"}), 400
    success, message = _play_track_internal(track_number)
    if success: return jsonify({"status": "success", "message": message, "track_number": track_number}), 200
    else: return jsonify({"status": "error", "message": message}), 500

@app.route('/api/cd/stop', methods=['POST'])
def stop_cd_playback_route():
    app.logger.info("Requête reçue pour /api/cd/stop")
    if stop_current_playback(log_info=True): return jsonify({"status": "success", "message": "Lecture arrêtée"}), 200
    else: return jsonify({"status": "success", "message": "Aucune lecture active à arrêter"}), 200

@app.route('/api/cd/pause', methods=['POST'])
def pause_cd_playback_route():
    global playback_process_cdparanoia, playback_process_pwcat, is_playback_paused_flag, playback_start_time, playback_pause_duration
    app.logger.info("Requête reçue pour /api/cd/pause")
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible de mettre en pause: extraction en cours"}), 409
    if playback_process_cdparanoia and playback_process_pwcat and playback_process_cdparanoia.poll() is None and playback_process_pwcat.poll() is None and not is_playback_paused_flag:
        try:
            if playback_start_time: playback_pause_duration = time.time() - playback_start_time 
            os.kill(playback_process_pwcat.pid, signal.SIGSTOP); os.kill(playback_process_cdparanoia.pid, signal.SIGSTOP)
            is_playback_paused_flag = True
            app.logger.info(f"Lecture mise en pause. Durée jouée avant pause: {playback_pause_duration:.2f}s")
            return jsonify({"status": "success", "message": "Lecture mise en pause"}), 200
        except Exception as e: app.logger.error(f"Erreur lors de la mise en pause: {e}"); return jsonify({"status": "error", "message": f"Erreur pause: {e}"}), 500
    elif is_playback_paused_flag: return jsonify({"status": "info", "message": "Lecture déjà en pause"}), 200
    else: return jsonify({"status": "info", "message": "Aucune lecture à mettre en pause"}), 200

@app.route('/api/cd/resume', methods=['POST'])
def resume_cd_playback_route():
    global playback_process_cdparanoia, playback_process_pwcat, is_playback_paused_flag, playback_start_time, playback_pause_duration
    app.logger.info("Requête reçue pour /api/cd/resume")
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible de reprendre: extraction en cours"}), 409
    if playback_process_cdparanoia and playback_process_pwcat and playback_process_cdparanoia.poll() is None and playback_process_pwcat.poll() is None and is_playback_paused_flag:
        try:
            os.kill(playback_process_cdparanoia.pid, signal.SIGCONT); os.kill(playback_process_pwcat.pid, signal.SIGCONT)
            playback_start_time = time.time() - playback_pause_duration 
            is_playback_paused_flag = False
            app.logger.info(f"Lecture reprise. Nouveau temps de départ effectif: {playback_start_time:.2f} (basé sur {playback_pause_duration:.2f}s joués avant pause).")
            playback_pause_duration = 0.0 
            return jsonify({"status": "success", "message": "Lecture reprise"}), 200
        except Exception as e: app.logger.error(f"Erreur lors de la reprise: {e}"); return jsonify({"status": "error", "message": f"Erreur reprise: {e}"}), 500
    elif not is_playback_paused_flag and playback_process_cdparanoia: return jsonify({"status": "info", "message": "Lecture n'est pas en pause"}), 200
    else: return jsonify({"status": "info", "message": "Aucune lecture à reprendre"}), 200

@app.route('/api/cd/next', methods=['POST'])
def next_track_route():
    app.logger.info("Requête reçue pour /api/cd/next")
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible de changer de piste: extraction en cours"}), 409
    if not current_playing_track_number: return jsonify({"status": "info", "message": "Aucune piste en cours."}), 400
    next_track_val = get_next_track()
    if next_track_val is None: return jsonify({"status": "info", "message": "Pas de piste suivante disponible."}), 400
    success, message = _play_track_internal(next_track_val)
    if success: return jsonify({"status": "success", "message": f"Lecture de la piste {next_track_val}", "track_number": next_track_val}), 200
    else: return jsonify({"status": "error", "message": message}), 500

@app.route('/api/cd/previous', methods=['POST'])
def previous_track_route():
    app.logger.info("Requête reçue pour /api/cd/previous")
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible de changer de piste: extraction en cours"}), 409
    if not current_playing_track_number: return jsonify({"status": "info", "message": "Aucune piste en cours."}), 400
    track_to_play = None; position = get_playback_position()
    if position["position_sec"] > 3 and current_playing_track_number is not None: track_to_play = current_playing_track_number
    else: track_to_play = get_previous_track()
    if track_to_play is None: track_to_play = current_playing_track_number 
    if track_to_play is None: return jsonify({"status": "error", "message": "Impossible de déterminer la piste."}), 400
    success, message = _play_track_internal(track_to_play)
    if success: return jsonify({"status": "success", "message": f"Lecture de la piste {track_to_play}", "track_number": track_to_play}), 200
    else: return jsonify({"status": "error", "message": message}), 500

@app.route('/api/cd/mode', methods=['POST'])
def set_playback_mode_route():
    global playback_mode; app.logger.info("Requête reçue pour /api/cd/mode"); data = request.get_json()
    if not data: return jsonify({"status": "error", "message": "Données JSON requises"}), 400
    try:
        updated_modes_log = []
        if "repeat" in data:
            new_val = bool(data["repeat"])
            if playback_mode["repeat"] != new_val: playback_mode["repeat"] = new_val; updated_modes_log.append(f"repeat: {new_val}")
            if new_val: playback_mode["shuffle"] = False; playback_mode["repeat_all"] = False
        if "shuffle" in data: 
            new_val = bool(data["shuffle"])
            if playback_mode["shuffle"] != new_val: playback_mode["shuffle"] = new_val; updated_modes_log.append(f"shuffle: {new_val}")
            if new_val: playback_mode["repeat"] = False
        if "repeat_all" in data: 
            new_val = bool(data["repeat_all"])
            if playback_mode["repeat_all"] != new_val: playback_mode["repeat_all"] = new_val; updated_modes_log.append(f"repeat_all: {new_val}")
            if new_val: playback_mode["repeat"] = False 
        if updated_modes_log: app.logger.info(f"Modes de lecture mis à jour: {', '.join(updated_modes_log)}. État: {playback_mode}")
        else: app.logger.info(f"Aucun changement de mode. État: {playback_mode}")
        return jsonify({"status": "success", "message": f"Modes configurés. Actif: {playback_mode}", "modes": playback_mode}), 200
    except Exception as e: app.logger.error(f"Erreur config modes: {e}"); return jsonify({"status": "error", "message": f"Erreur: {e}"}), 500

@app.route('/api/cd/seek', methods=['POST'])
def seek_track_route():
    global current_playing_track_number, playback_start_time, playback_pause_duration, is_playback_paused_flag
    app.logger.info("Requête reçue pour /api/cd/seek")
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible pendant extraction"}), 409
    if not current_playing_track_number: return jsonify({"status": "error", "message": "Aucune piste en cours"}), 400
    data = request.get_json();
    if not data or "position" not in data: return jsonify({"status": "error", "message": "Position (secondes) requise"}), 400
    try: position_sec = float(data["position"]); position_sec = max(0, position_sec)
    except (ValueError, TypeError): return jsonify({"status": "error", "message": "Position doit être un nombre"}), 400
    try:
        track_to_restart = current_playing_track_number
        stop_current_playback(log_info=False) 
        success, message = _play_track_internal(track_to_restart)
        if success:
            playback_start_time = time.time() - position_sec 
            playback_pause_duration = 0.0; is_playback_paused_flag = False 
            app.logger.info(f"Navigation (simulée) vers {position_sec:.1f}s pour piste {track_to_restart}.")
            return jsonify({"status": "success", "message": f"Navigation vers {position_sec:.1f}s", "track_number": track_to_restart, "requested_position_sec": position_sec}), 200
        else: return jsonify({"status": "error", "message": f"Échec redémarrage piste: {message}"}), 500
    except Exception as e: app.logger.error(f"Erreur seek: {e}"); return jsonify({"status": "error", "message": f"Erreur interne seek: {e}"}), 500

@app.route('/api/cd/rip', methods=['POST'])
@require_api_key
def rip_cd_route():
    global ripping_process_script, ripping_progress, CD_INFO_CACHE
    app.logger.info("Requête reçue pour /api/cd/rip")
    if check_ripping_status(): return jsonify({"status": "error", "message": "Extraction déjà en cours"}), 409
    stop_current_playback()
    toc_info = get_cd_toc_and_update_globals()
    if toc_info.get("status") != "audio_cd_present" or toc_info.get("tracks", 0) == 0:
        return jsonify({"status": "error", "message": "Pas de CD audio détecté ou CD vide"}), 400
    data = request.get_json() or {}; format_type = data.get("format", "flac").lower()
    output_path_base = data.get("output_path", "/tmp/maqam_rips")
    if format_type not in ["flac", "wav"]: return jsonify({"status": "error", "message": "Format non supporté (flac, wav)"}), 400
    if not os.path.exists(RIP_SCRIPT): app.logger.error(f"Script extraction introuvable: {RIP_SCRIPT}"); return jsonify({"status": "error", "message": f"Script introuvable: {RIP_SCRIPT}"}), 500
    try:
        album_info = CD_INFO_CACHE.get("musicbrainz_data", {}); album_name = album_info.get("title", "Album Inconnu"); artist_name = album_info.get("artist", "Artiste Inconnu")
        sane_album = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in album_name)[:50]
        sane_artist = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in artist_name)[:50]
        rip_dir_name = f"{sane_artist} - {sane_album}"; output_path = os.path.join(output_path_base, rip_dir_name)
        os.makedirs(output_path, exist_ok=True)
        metadata_payload = {"album": album_name, "artist": artist_name, "date": album_info.get("date", ""), "tracks": toc_info.get("track_details", [])}
        metadata_file_path = os.path.join(output_path, "metadata.json")
        with open(metadata_file_path, 'w', encoding='utf-8') as f: json.dump(metadata_payload, f, ensure_ascii=False, indent=2)
        rip_command = ['/bin/bash', RIP_SCRIPT, CD_DEVICE, output_path, format_type, str(toc_info["tracks"]), metadata_file_path]
        app.logger.info(f"Lancement extraction: {' '.join(rip_command)}")
        ripping_process_script = subprocess.Popen(rip_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
        ripping_progress.update({"active": True, "current_track": 0, "total_tracks": toc_info["tracks"], "percentage": 0, "current_track_percentage": 0, "estimated_time_remaining": None, "format": format_type, "output_path": output_path, "start_time": time.time()})
        monitor_thread = threading.Thread(target=monitor_ripping_progress, daemon=True); monitor_thread.start()
        return jsonify({"status": "success", "message": f"Extraction démarrée vers {output_path}", "progress": ripping_progress}), 200
    except Exception as e: app.logger.error(f"Erreur démarrage extraction: {e}", exc_info=True); ripping_progress["active"] = False; return jsonify({"status": "error", "message": f"Erreur extraction: {str(e)}"}), 500

@app.route('/api/cd/rip/stop', methods=['POST'])
@require_api_key
def stop_rip_route():
    global ripping_process_script, ripping_progress; app.logger.info("Requête reçue pour /api/cd/rip/stop")
    if not ripping_progress.get("active", False) or ripping_process_script is None: return jsonify({"status": "info", "message": "Aucune extraction à arrêter"}), 200
    try:
        if ripping_process_script.poll() is None:
            app.logger.info(f"Arrêt processus extraction (PID: {ripping_process_script.pid})")
            ripping_process_script.terminate()
            try: ripping_process_script.wait(timeout=5)
            except subprocess.TimeoutExpired: app.logger.warning("Timeout arrêt extraction, kill forcé."); ripping_process_script.kill(); ripping_process_script.wait()
    except Exception as e: app.logger.error(f"Erreur arrêt extraction: {e}", exc_info=True)
    finally: ripping_process_script = None; ripping_progress["active"] = False; ripping_progress["percentage"] = 0; app.logger.info("Extraction marquée inactive.")
    return jsonify({"status": "success", "message": "Demande d'arrêt extraction traitée."}), 200

@app.route('/api/cd/eject', methods=['POST'])
@require_api_key
def eject_cd_route():
    app.logger.info("Requête reçue pour /api/cd/eject"); stop_current_playback()
    if check_ripping_status(): return jsonify({"status": "error", "message": "Impossible d'éjecter: extraction en cours"}), 409
    try:
        result = subprocess.run(['/usr/bin/eject', CD_DEVICE], capture_output=True, text=True, timeout=10, check=False)
        if result.returncode == 0:
            global CD_INFO_CACHE; CD_INFO_CACHE = {"toc": None, "musicbrainz_data": None, "last_checked": 0, "disc_id": None, "total_tracks": 0}
            return jsonify({"status": "success", "message": "CD éjecté"}), 200
        else: error_msg = result.stderr.strip() or f"eject code {result.returncode}"; return jsonify({"status": "error", "message": f"Erreur éjection: {error_msg}"}), 500
    except subprocess.TimeoutExpired: return jsonify({"status": "error", "message": "Timeout éjection"}), 500
    except FileNotFoundError: return jsonify({"status": "error", "message": "Commande eject introuvable."}), 500
    except Exception as e: return jsonify({"status": "error", "message": f"Erreur éjection: {str(e)}"}), 500

@app.route('/api/cd/metadata/refresh', methods=['POST'])
def refresh_metadata_route(): # Not protected as per instructions (can be debated for production)
    global CD_INFO_CACHE; app.logger.info("Requête reçue pour /api/cd/metadata/refresh")
    try:
        CD_INFO_CACHE["musicbrainz_data"] = None; CD_INFO_CACHE["last_checked"] = 0
        toc_info = get_cd_toc_and_update_globals()
        if toc_info.get("status") == "audio_cd_present" and toc_info.get("tracks", 0) > 0:
            return jsonify({"status": "success", "message": "Métadonnées mises à jour.", "album": CD_INFO_CACHE.get("musicbrainz_data", {})}), 200
        elif toc_info.get("status") == "no_disc": return jsonify({"status": "info", "message": "Aucun disque."}), 400
        else: return jsonify({"status": "info", "message": "Pas de CD audio pour màj métadonnées."}), 400
    except Exception as e: return jsonify({"status": "error", "message": f"Erreur interne: {str(e)}"}), 500

# === THREADS DE MONITORING === 

def monitor_playback():
    global current_playing_track_number
    while True:
        try:
            time.sleep(1)
            if (playback_process_cdparanoia and playback_process_cdparanoia.poll() is not None) or \
               (playback_process_pwcat and playback_process_pwcat.poll() is not None):
                if current_playing_track_number is not None:
                    app.logger.info(f"Fin lecture piste {current_playing_track_number} (processus terminé).")
                    track_before = current_playing_track_number
                    stop_current_playback(log_info=False)
                    next_track = get_next_track()
                    if next_track: app.logger.info(f"Auto-passage à piste {next_track} depuis {track_before}."); time.sleep(0.2); _play_track_internal(next_track)
                    else: app.logger.info(f"Fin album ou pas de répétition après {track_before}.")
        except Exception as e: app.logger.error(f"Erreur thread monitor_playback: {e}", exc_info=True); time.sleep(5)

def monitor_ripping_progress():
    global ripping_progress, ripping_process_script
    app.logger.info("Démarrage monitoring extraction.")
    while True:
        if not ripping_progress.get("active") or ripping_process_script is None: break
        try:
            if ripping_process_script.poll() is not None:
                rc = ripping_process_script.returncode; app.logger.info(f"Processus extraction (PID {ripping_process_script.pid}) terminé code {rc}.")
                ripping_progress["active"] = False; ripping_process_script = None
                if rc == 0: ripping_progress["percentage"] = 100; ripping_progress["current_track"] = ripping_progress["total_tracks"]
                break
            if "start_time" in ripping_progress and ripping_progress["start_time"]:
                elapsed = time.time() - ripping_progress["start_time"]; total_tracks = ripping_progress.get("total_tracks", 1) or 1
                estimated_total_time = total_tracks * 120 or 120; progress_pct = min(99, (elapsed / estimated_total_time) * 100)
                ripping_progress["percentage"] = int(progress_pct)
                current_track_calc = min(total_tracks, int((progress_pct / 100) * total_tracks) + 1)
                if ripping_progress["current_track"] != current_track_calc:
                     ripping_progress["current_track"] = current_track_calc; app.logger.info(f"Extraction piste {current_track_calc}/{total_tracks} ({progress_pct:.0f}%)")
                if progress_pct > 1: remaining_time = (estimated_total_time - elapsed); ripping_progress["estimated_time_remaining"] = f"{int(remaining_time//60)}m {int(remaining_time%60)}s" if remaining_time > 0 else "calcul..."
            time.sleep(2)
        except Exception as e: app.logger.error(f"Erreur monitoring extraction: {e}", exc_info=True); ripping_progress["active"] = False; ripping_process_script = None; break
    app.logger.info("Fin monitoring extraction.")

playback_monitor_thread = threading.Thread(target=monitor_playback, daemon=True)
playback_monitor_thread.start()

# === GESTIONNAIRE DE SIGNAUX ===
def signal_handler(signum, frame):
    app.logger.info(f"Signal {signal.Signals(signum).name} reçu, arrêt...")
    stop_current_playback(log_info=False)
    global ripping_process_script
    if ripping_process_script and ripping_process_script.poll() is None:
        try:
            app.logger.info(f"Arrêt extraction (PID {ripping_process_script.pid}) lors de la fermeture.")
            ripping_process_script.terminate(); ripping_process_script.wait(timeout=3)
        except subprocess.TimeoutExpired: app.logger.warning("Timeout arrêt extraction, kill."); ripping_process_script.kill()
        except Exception as e: app.logger.error(f"Erreur arrêt extraction: {e}", exc_info=True)
    app.logger.info("Service MAQAM CD API arrêté."); os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === POINT D'ENTRÉE ===
if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    app.logger.info("=== MAQAM CD API - Démarrage ===")
    app.logger.info(f"Config: CD={CD_DEVICE}, RipScript={RIP_SCRIPT}, Prefs={os.path.abspath(USER_PREFERENCES_FILE)}")
    
    current_prefs = load_preferences(); save_preferences(current_prefs) 
    app.logger.info(f"Préférences initiales: {current_prefs}")
    
    dependencies = [
        ('/usr/bin/cd-info', 'libcdio-utils'), ('/usr/bin/cdparanoia', 'cdparanoia'),
        ('/usr/bin/pw-cat', 'pipewire-bin' if os.path.exists('/usr/bin/apt') else 'pipewire'),
        ('/usr/bin/eject', 'eject' if os.path.exists('/usr/bin/apt') else 'util-linux')
    ]
    missing_deps = [f"{p} (paquet: {pkg})" for p, pkg in dependencies if not os.path.exists(p)]
    if missing_deps:
        app.logger.error("Dépendances manquantes CRITIQUES:\n - " + "\n - ".join(missing_deps))
        app.logger.error("Installer les paquets manquants et redémarrer.")
    
    if not os.path.exists(CD_DEVICE) or not os.access(CD_DEVICE, os.R_OK):
        app.logger.warning(f"Périphérique CD {CD_DEVICE} non trouvé/lisible. Vérifier config/permissions.")
    
    app.logger.info(f"API prête - Écoute sur http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

[end of MAQAM CD API.py]
