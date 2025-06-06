﻿maqam-audio-iso/                 # Répertoire racine du processus de build

Archiso

├── README.md                   # Documentation principale du processus de build

(comment construire l'ISO)

├── build.sh                    # Script de build principal Archiso (généralement

`mkarchiso`)

├── packages.x86\_64             # Liste principale des paquets pour l'image (peut

inclure des méta-paquets)

├── profiledef.sh               # Définition du profil Archiso (variables,

fonctions de build)

├── pacman.conf                 # Configuration Pacman spécifique au build de

l'ISO

│

├── etc/                        # Fichiers de configuration et scripts utilisés

PENDANT le build

│   ├── fstab.template          # Modèle pour /etc/fstab dans le système final (si

nécessaire)

│   ├── packages/               # Organisation des listes de paquets pour plus de

clarté

│   │   ├── 00\_base.txt         # Paquets système de base (ex: base, linux-rt,

systemd)

│   │   ├── 01\_audio\_core.txt   # Paquets audio (pipewire, wireplumber, alsa

utils, rtkit)

│   │   ├── 02\_services.txt     # Paquets pour les services (lms, squeezelite,

lighttpd, nodejs, python-flask)

│   │   ├── 03\_ui\_kiosk.txt     # Paquets pour l'interface (i3, chromium, xorg)

│   │   ├── 04\_cd\_tools.txt     # Paquets pour les opérations CD (cdparanoia,

flac, abcde, etc.)

│   │   ├── 05\_devtools.txt     # Outils de développement (git, base-devel, yay si

buildé ici)

│   │   └── 99\_custom.txt       # Autres paquets spécifiques au projet

│   └── scripts/                # Scripts utilitaires pour le processus de build

│       ├── 10\_prepare\_iso.sh   # Scripts pour préparer l'airootfs avant la

création de l'ISO (ex: copier les sources des API, le frontend buildé)

│       ├── 20\_install\_aur\_packages.sh # Script pour cloner et builder les paquets

AUR dans le chroot (si pas géré par yay au firstboot)

│       └── (autres scripts de build si nécessaire, ex: create\_persistence.sh,

create\_data\_partition.sh si ce n'est pas fait manuellement)

│

└── airootfs/                   # Structure RACINE du système d'exploitation

installé ou démarré en live

├── boot/

│   └── loader/             # Configuration systemd-boot

│       ├── entries/

│       │   └── maqam-rt.conf # Entrée de démarrage pour le noyau RT MAQAM OS

│       └── loader.conf     # Configuration principale du bootloader systemd

boot

├── data/                   # Point de montage pour la partition de données

persistantes

│   └── music/              # Données musicales

│       └── extracted/      # Cible par défaut pour les CD extraits par

rip\_cd.sh

├── etc/                    # Fichiers de configuration système

│   ├── abcde.conf          # Configuration globale pour abcde

│   ├── hostname            # Nom d'hôte du système (ex: maqam-audio-os)

│   ├── hosts               # Fichier hosts standard

│   ├── i3/

│   │   └── config          # Configuration i3 globale (si pas uniquement par

utilisateur)

│   ├── lighttpd/

│   │   └── lighttpd.conf   # Configuration du serveur web Lighttpd pour MAQAM

Player UI

│   ├── locale.conf         # Configuration de la langue système (ex:

LANG="fr\_FR.UTF-8")

│   ├── locale.gen          # Locales à générer

│   ├── motd                # Message du jour à la connexion console

│   ├── pipewire/

│   │   ├── pipewire.conf.d/

│   │   │   └── 99-maqam-bitperfect.conf # Configuration PipeWire spécifique

pour le bit-perfect

│   │   └── pipewire-pulse.conf.d/

│   │       └── 99-maqam-disable-resampling.conf # Configuration PipeWire

Pulse (désactiver resampling si souhaité)

│   ├── profile             # Script exécuté au login (peut définir des

variables d'environnement globales)

│   ├── shells              # Liste des shells valides

│   ├── skel/               # Squelette pour les nouveaux répertoires

utilisateurs

│   │   ├── .bash\_profile   # Script pour l'utilisateur 'charly' pour démarrer

startx en autologin

│   │   ├── .xinitrc        # Script pour lancer la session X (i3,

configuration xset)

│   │   └── .config/

│   │       └── i3/

│   │           └── config  # Configuration i3 spécifique à l'utilisateur

'charly' (prioritaire sur /etc/i3/config)

│   ├── sudoers.d/          # Fichiers pour la configuration fine de sudo (ex:

pour l'utilisateur de l'API Node.js)

│   │   └── 10-maqam-api    # Ex: autoriser l'utilisateur de l'API Node à

lancer systemctl/pacman sans mdp

│   ├── systemd/

│   │   ├── system/         # Unités Systemd système

│   │   │   ├── boot-update.path    # Unité path pour surveiller les mises à

jour du noyau

│   │   │   ├── boot-update.service # Service pour mettre à jour systemd-boot

après MàJ noyau

│   │   │   ├── cpu-governor-performance.service # Service pour régler le

gouverneur CPU sur performance

│   │   │   ├── lyrionmusicserver.service        # Service pour Lyrion Music

Server

│   │   │   ├── maqam-cd-api.service           # Service pour l'API CD Python

│   │   │   ├── maqam-firstboot.service        # Service exécuté une seule

fois au premier démarrage

│   │   │   ├── maqam-node-api.service         # Service pour l'API Backend

Node.js

│   │   │   ├── lighttpd.service               # (Généralement fourni par le

paquet, peut être surchargé ici si besoin)

│   │   │   └── multi-user.target.wants/     # Liens symboliques pour les

services à démarrer

│   │   │       ├── cpu-governor-performance.service -> ../cpu-governor

performance.service

│   │   │       ├── lyrionmusicserver.service        ->

../lyrionmusicserver.service

│   │   │       ├── maqam-cd-api.service           -> ../maqam-cd-api.service

│   │   │       ├── maqam-firstboot.service        -> ../maqam

firstboot.service

│   │   │       └── maqam-node-api.service         -> ../maqam-node

api.service

│   │   └── user/           # Unités Systemd utilisateur (seront liées pour

l'utilisateur 'charly')

│   │       └── squeezelite.service # Service Squeezelite pour l'utilisateur

'charly'

│   ├── udev/

│   │   └── rules.d/        # Règles udev

│   │       ├── 60-persistent-cdrom-rsa780.rules # Règle pour le lecteur CD

ROSE RSA780

│   │       ├── 61-khadas-tone2-pro.rules        # Règle spécifique pour le

DAC Khadas (ex: priorités)

│   │       └── 90-touchscreen.rules             # Règle générique pour les

écrans tactiles (permissions)

│   └── wireplumber/        # Configuration WirePlumber

│       └── main.lua.d/

│           └── 99-khadas-tone2-pro-bitperfect.lua # Script Lua pour

configurer le DAC Khadas

├── home/                   # Répertoires des utilisateurs

│   └── charly/             # Répertoire de l'utilisateur principal (autologin

pour i3)

│       │                   # (Contenu initialisé depuis /etc/skel/)

│       └── .cache/         # Cache utilisateur (ex: pour Chromium)

│           └── (autres fichiers de cache...)

├── opt/                    # Applications et scripts optionnels/tiers

│   ├── lyrionmusicserver/  # Installation de Lyrion Music Server

│   │   └── slimserver.pl   # Exécutable principal LMS

│   │   └── (autres fichiers LMS...)

│   ├── maqam\_api/          # API CD Python

│   │   ├── maqam\_cd\_api.py # Script principal de l'API

│   │   └── requirements.txt # Dépendances Python (si installées dans un venv

│   ├── maqam-node-api/     # API Backend Node.js (build de production et

node\_modules)

│   │   ├── dist/           # Code transpilé JavaScript

│   │   ├── node\_modules/   # Dépendances Node.js de production

│   │   ├── package.json

│   │   └── (autres fichiers nécessaires au runtime)

│   └── maqam\_scripts/      # Scripts utilitaires spécifiques au projet MAQAM

│       ├── update\_system.sh # Script pour lancer les mises à jour système

(appelé par l'API Node.js)

│       └── backup\_config.sh # Script pour sauvegarder la configuration (si

pertinent)

├── root/                   # Répertoire home de l'utilisateur root

│   └── .automated\_script.sh # Script de configuration exécuté au premier

démarrage par maqam-firstboot.service

├── srv/                    # Données servies par le système

│   └── http/

│       └── maqam-player/   # Racine des documents pour Lighttpd (contient le

frontend Vue.js buildé)

│           ├── assets/     # Assets JS/CSS du frontend

│           ├── index.html  # Point d'entrée du frontend

│           └── favicon.ico

├── usr/

│   ├── local/

│   │   └── bin/            # Exécutables locaux

│   │       ├── cd\_handler    # Script udev pour la gestion des CD

│   │       ├── check-maqam-system.sh # Script de vérification du système

│   │       ├── rip\_cd.sh     # Script d'extraction CD

│   │       └── start-maqam-player.sh # Script pour lancer Chromium en mode

kiosque

│   └── share/

│       ├── backgrounds/    # Fonds d'écran (si i3 en utilise un avant que

Chromium se lance)

│       │   └── maqam\_default\_bg.png

│       └── doc/

│           └── maqam/      # Documentation spécifique au projet MAQAM OS

│               ├── README.md         # Documentation principale installée

│               ├── HARDWARE.md       # Notes sur la compatibilité matérielle

│               └── (autres fichiers de doc pertinents pour le système

installé)

└── var/                    # Données variables

├── cache/

│   └── lyrionmusicserver/ # Cache pour LMS (géré par LMS lui-même)

├── lib/

│   ├── lyrionmusicserver/ # Données persistantes de LMS (base de données,

préférences)

│   └── maqam-firstboot-completed # Fichier indicateur créé par maqam

firstboot.service après succès

└── log/

├── lyrionmusicserver/ # Logs de Lyrion Music Server

├── lighttpd/         # Logs de Lighttpd (access.log, error.log)

├── maqam-firstboot.log # Log du script de premier démarrage

├── maqam-system-check.log # Log du script de vérification

└── (journaux systemd via `journalctl`)

Changements et Justifications :

Organisation des packages et scripts de build : Adoptée de votre proposition

pour une meilleure clarté dans le processus de build.

Placement des API et du frontend buildé : L'API Node.js et le frontend sont

copiés dans airootfs/opt/ et airootfs/srv/http/ respectivement. Cela sépare bien les

applications des configurations système.

Configuration utilisateur i3 : airootfs/etc/skel/.config/i3/config est la méthode

standard pour fournir une configuration i3 par défaut à l'utilisateur charly.

Services Systemd : J'ai listé les services que nous avons discutés, y compris les

nouveaux pour les API. Leurs liens dans multi-user.target.wants/ assurent leur

démarrage. lighttpd.service sera généralement fourni par son paquet.

Préférences LMS : Déplacées de /home/charly/ vers /var/lib/lyrionmusicserver/ car

c'est ce que le service système lyrionmusicserver utilise (via --prefsdir).

Scripts update\_system.sh et backup\_config.sh : Placés dans

/opt/maqam\_scripts/ comme suggéré, car ils sont spécifiques au projet mais

peuvent être appelés par des services ou des API.

Documentation Installée : Une section /usr/share/doc/maqam/ pour la

documentation essentielle directement sur le système est une bonne pratique.

Fichier indicateur maqam-firstboot-completed : Confirmé comme un fichier, pas

un répertoire.

Cette arborescence fusionnée est, je pense, robuste, respecte les conventions, et intègre

tous les éléments que nous avons développés conceptuellement. Elle fournit une base

solide pour la construction de l'image MAQAM Audio OS.
