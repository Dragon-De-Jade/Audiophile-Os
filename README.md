# Audiophile-Os
#Compte rendu détaillé du projet MAQAM Player

Le projet MAQAM Player est une interface web tactile optimisée pour les systèmes audiophiles basés sur Arch Linux avec Lyrion/Squeezelite. L'interface est conçue pour fonctionner sur des écrans tactiles de 5-7 pouces(format paysage), avec un accent particulier sur:

\- La performance et la réactivité (le framewok Vue.js sera privilégié)

\- La préservation de la qualité audio bit-perfect

\- Une expérience utilisateur intuitive et adaptée aux écrans tactiles

\- Un design minimaliste avec des contrôles tactiles de grande taille

\- Une interface sombre adaptée à l'environnement d'écoute

**Interface principale**

L'interface principale est divisée en cinq onglets principaux, accessibles via une barre de navigation en haut:

1\. \*\*Lecture\*\*: Lecteur audio principal

2\. \*\*Bibliothèque\*\*: Accès à la collection musicale

3\.\*\*Extraction\*\* : Accès aux commande et propriétés d’extraction au format Flac ou WAV

3\. \*\*Sources\*\*: Configuration des sources audio

4\. \*\*Système\*\*: Informations et contrôles système


En haut à gauche se trouve le logo MAQAM avec le texte « MAQAM Player Bit-Perfect » en orange**(#ff9800)**, établissant l'identité visuelle de l'application dans toutes les fenêtres.

**Onglet "Lecture"**

C'est l'onglet principal qui permet de contrôler la lecture audio. Il existe en deux modes:

**Mode normal (compact)**

\- \*\*Affichage de la pochette d'album\*\* 

\- \*\*Informations sur le morceau\*\*: titre, artiste, album

\- \*\*Contrôles de lecture\*\*:

\- Éjecter CD: Permet d'éjecter un CD physique

\- Shuffle: Active/désactive la lecture aléatoire (s'illumine en orange quand actif)

\- Précédent: Passe au morceau précédent

\- Lecture/Pause: Démarre ou met en pause la lecture

\- Suivant: Passe au morceau suivant

\- Répéter: Active/désactive la répétition (s'illumine en orange quand actif)

\- Stop: Arrête complètement la lecture



\- \*\*Slider de durée\*\*: Affiche et permet de contrôler la progression du morceau

\- \*\*Contrôle du volume\*\*: ON(100%) / OFF(sourdine)

\- \*\*Bouton Favoris\*\*: Permet d'ajouter le morceau aux favoris (s'illumine en rouge quand actif)

\- \*\*Bouton Détails\*\*: Ouvre une fenêtre modale avec des informations techniques sur le format audio

-\*\*Affichage du prochain titre(titre, artiste, album)\*\*

-\*\*Affichage du titre précédant(titre, artiste, album )\*\*

\- \*\*Bouton plein écran\*\*: Permet de passer en mode plein écran


**Mode plein écran (reader mode)**

\- \*\*Logo et titre MAQAM Player\*\* en haut à gauche

\- \*\*Disposition horizontale\*\* avec:

\- \*\*Pochette d'album\*\* à gauche 

\- \*\*Informations détaillées\*\* à droite: titre (plus grand), artiste, album, format



\- \*\*Contrôles de lecture\*\* centrés sous la pochette d'album

\- \*\*Slider de durée\*\* placé à droite sous les boutons "Favoris" et "Détails"

\- \*\*Contrôle du volume\*\* en haut à droite permettant ON(100%) / OFF(sourdine)

\- \*\*Bouton de réduction\*\* pour revenir au mode normal

\- \*\*Masquage automatique\*\* des onglets et du titre principal pour maximiser l'espace d'affichage

-\*\* Masquage automatique\*\* titre suivant, titre précédent…ect.


**Onglet "Bibliothèque"**

Permet de parcourir et d'accéder à la collection musicale:

\- \*\*Barre de recherche\*\* en haut pour filtrer le contenu

-\*\*Mini lecteur en bas sur toute largeur de la fenêtre avec tous les boutons de commande(à l’exception des boutons repeat, shuffle, favoris et information), album-cover, track info( titre, album, artist), slider de durée\*\*

\- \*\*Quates sous-onglets\*\*:

1\. \*\*Albums\*\*: Affiche une grille de pochettes d'albums avec titre, artiste et nombre de pistes (avec possibilité de lancer la lecture de l’album par double-tap).

2\. \*\*Artistes\*\*: Liste des artistes avec leur genre et nombre d'albums

3\. \*\*Playlists\*\*: Liste des playlists avec nombre de pistes et bouton de lecture rapide

4\.\*\*Favoris\*\* : Listes des favoris avec miniature cover (avec possibilité de lancer la lecture par double-tap). Bouton Favoris à côté du titre permet de retirer le morceau des favoris




\- \*\*Bouton d'historique d'écoute\*\* en bas pour accéder à l'historique

**Onglet "Extraction"**

Choix du format d'extraction (FLAC ou WAV)

Options de qualité (16bit/44.1kHz à 24bit/192kHz)

Choix de destination (stockage local, NAS, USB)

Options avancées (préservation des métadonnées, normalisation audio)

Bouton pour démarrer l'extraction avec simulation de progression

**Onglet "Sources"**

Permet de configurer les sources audio:

\- \*\*Liste des sources audio disponibles\*\*:

\- DAC USB

\- S/PDIF Out

\- NAS Music

\- \*\*Indication de l'état de connexion\*\* pour chaque source

\*\*Bouton de configuration avancée\*\* qui ouvre une fenêtre modale avec:

\- Sélection du périphérique ALSA

\- Activation/désactivation du mode exclusif





**Onglet "Système"**

Fournit des informations sur l'état du système et des contrôles :

\- \*\*Informations CPU\*\*: utilisation, température, gouverneur

\- \*\*Informations mémoire\*\*: utilisation RAM et stockage

\- \*\*Informations système\*\*: version du noyau Linux, temps de fonctionnement

\- \*\*État des services critiques\*\*:

\- lyrion-server

\- squeezelite

\- pipewire

\- wireplumber

\- alsa



\- \*\*Bouton d'extinction\*\* avec confirmation pour arrêter le système en toute sécurité

Fonctionnalités et interactions

**Contrôles de lecture**

\- \*\*Lecture/Pause\*\*: Démarre ou met en pause la lecture du morceau actuel

\- \*\*Stop\*\*: Arrête complètement la lecture et réinitialise la position

\- \*\*Précédent/Suivant\*\*: Navigation entre les morceaux

\- \*\*Shuffle\*\*: Active la lecture aléatoire des morceaux

\- \*\*Repeat\*\*: Active la répétition du morceau actuel ou de la playlist

\- \*\*Éjecter CD\*\*: permet l'éjection du CD 



**Navigation temporelle**

\- \*\*Slider de durée\*\*: Permet de naviguer dans le morceau

\- \*\*Affichage du temps écoulé/restant\*\*: Format minutes:secondes


**Favoris et informations**

\- \*\*Bouton Favoris\*\*: Ajoute/retire le morceau des favoris

\- \*\*Bouton Détails\*\*: Affiche des informations techniques sur le format audio, le mode de lecture, etc.


**Changement de mode d'affichage**

\- \*\*Bouton plein écran/réduction\*\*: Bascule entre le mode normal et le mode plein écran

\- \*\*Masquage automatique\*\* des éléments d'interface non essentiels en mode plein écran



**Optimisations tactiles**

\- \*\*Grands boutons\*\*: Facilement accessibles sur petit écran tactile

\- \*\*Désactivation du zoom sur double-tap\*\*: Pour éviter les interactions accidentelles

\- \*\*Propriété touch-action\*\*: Optimisée pour les interactions tactiles


**Thème et design**

\- \*\*Thème sombre\*\*: Adapté à l'environnement d'écoute

\- \*\*Couleur principale\*\*: Orange (`#ff9800`) pour les éléments actifs et importants

\- \*\*Contraste élevé\*\*: Pour une meilleure lisibilité sur petit écran

\- \*\*Design responsive\*\*: S'adapte à différentes tailles d'écran
