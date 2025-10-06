***/bin/rip_cd.sh***

#!/bin/bash

LOGFILE="/tmp/rip_cd.log"
OUTPUT_BASE="/data/music/extracted"
CD_DEVICE="/dev/sr1" # Notre lecteur dans la VM

RIP_FORMAT=$1 # Attendre "flac" ou "wav" comme premier argument

echo "=== Lancement extraction directe CD ($(date)) par $(whoami) ===" | tee -a "$LOGFILE"
echo "Format demandé: $RIP_FORMAT" | tee -a "$LOGFILE"

if [ ! -d "$OUTPUT_BASE" ] || [ ! -w "$OUTPUT_BASE" ] || [ ! -x "$OUTPUT_BASE" ]; then
     echo "### ERREUR: Dossier $OUTPUT_BASE non accessible en écriture/parcours pour $(whoami) ###" | tee -a "$LOGFILE"
     exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="${OUTPUT_BASE}/${TIMESTAMP}_direct_rip"
echo "Création du dossier de sortie : $OUTPUT_DIR" | tee -a "$LOGFILE"
mkdir -p "$OUTPUT_DIR"
if [ $? -ne 0 ]; then
  echo "### ERREUR: Impossible de créer le dossier de sortie $OUTPUT_DIR ###" | tee -a "$LOGFILE"
  exit 1
fi
chmod g+rws "$OUTPUT_DIR"

echo "Extraction vers : $OUTPUT_DIR" | tee -a "$LOGFILE"
echo "Lancement de cdparanoia..." | tee -a "$LOGFILE"

# Se placer dans le dossier de sortie pour que cdparanoia y écrive directement
cd "$OUTPUT_DIR"
if [ $? -ne 0 ]; then
  echo "### ERREUR: Impossible de se déplacer vers le dossier de sortie $OUTPUT_DIR ###" | tee -a "$LOGFILE"
  exit 1
fi

# Extraire toutes les pistes en WAV dans le répertoire courant ($OUTPUT_DIR)
/usr/bin/cdparanoia -d "$CD_DEVICE" -B 2>&1 | tee -a "$LOGFILE"
EXIT_CODE_CDPARANOIA=${PIPESTATUS[0]}

# Revenir au répertoire précédent
cd - > /dev/null

if [ $EXIT_CODE_CDPARANOIA -ne 0 ]; then
    echo "### ERREUR lors de l'extraction avec cdparanoia (Code: $EXIT_CODE_CDPARANOIA) $(date) ###" | tee -a "$LOGFILE"    # Optionnel: supprimer le dossier de sortie si l'extraction échoue ?
  # rm -rf "$OUTPUT_DIR"
    exit $EXIT_CODE_CDPARANOIA
fi

if [ "$RIP_FORMAT" == "flac" ]; then
    echo "Encodage en FLAC..." | tee -a "$LOGFILE"
    # Version plus sûre avec find, mais flac peut aussi opérer sur *.wav si on est dans le bon dossier
    # cd "$OUTPUT_DIR" # On est déjà dans OUTPUT_DIR si on veut que flac *.wav fonctionne
    # /usr/bin/flac --best --verify *.wav 2>&1 | tee -a "$LOGFILE"
    # EXIT_CODE_FLAC=${PIPESTATUS[0]}
    # if [ $EXIT_CODE_FLAC -eq 0 ]; then
    #    echo "Suppression des fichiers WAV sources..." | tee -a "$LOGFILE"
    #    rm -f *.wav
    # fi
    # cd - > /dev/null

    # Utiliser find est plus robuste si on ne veut pas dépendre du répertoire courant pour flac
    find "$OUTPUT_DIR" -name '*.wav' -exec /usr/bin/flac --best --verify {} \; 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE_FLAC=$? # $? capture le code de sortie de la dernière commande (find)
    if [ $EXIT_CODE_FLAC -eq 0 ]; then # Si find réussit (ce qui signifie que flac a réussi pour tous les fichiers)
        echo "Suppression des fichiers WAV sources..." | tee -a "$LOGFILE"
        find "$OUTPUT_DIR" -name '*.wav' -delete
    else
        echo "### ERREUR lors de l'encodage FLAC (Code: $EXIT_CODE_FLAC probable du dernier flac) ###" | tee -a "$LOGFILE"
        # Ne pas quitter ici, au moins les WAV sont extraits
    fi
elif [ "$RIP_FORMAT" == "wav" ]; then
    echo "Extraction en WAV terminée." | tee -a "$LOGFILE"
else
    echo "### ERREUR: Format '$RIP_FORMAT' non supporté par ce script. Utilisez 'flac' ou 'wav'. ###" | tee -a "$LOGFILE"
    # rm -rf "$OUTPUT_DIR" # Supprimer le dossier si format invalide
    exit 1
fi

echo "=== Extraction directe terminée (Code final: $EXIT_CODE_CDPARANOIA) $(date) ===" | tee -a "$LOGFILE"
exit $EXIT_CODE_CDPARANOIA # Retourner le code de cdparanoia comme code principal
