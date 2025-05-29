MAQAM OS est un système d’exploitation audiophile bit-perfect gapless optimisé pour un rendu audiophile sans altération du signal basé sur Arch Linux et Lyrion Music Server incluant l’optimisation du noyau (noyau RT), la gestion des services audio (une configuration fine d’ALSA, PipeWire…etc), Interface web et démarrage automatiquement de Lyrion Music Server et la réduction des interférences pour un rendu sonore pur. Pour optimiser davantage, une configuration du système pour utiliser l'option threadirqs du noyau sera une étape non négligeable. Pour garantir des performances constantes, il serait judicieux de configurer le gouverneur CPU en mode "performance". Il faudra alors un service systemd pour appliquer ce réglage automatiquement au démarrage.ALSA (Advanced Linux Sound Architecture) est la couche audio de base dans Linux. Pour une sortie bit-perfect, ALSA sera configurer pour accéder directement au DAC sans mixage. Par ailleurs, PipeWire est devenu le système audio préféré pour de nombreuses distributions Linux modernes. Lyrion Music Server intégrera PipeWire pour un rendu audiophile optimal. PipeWire sera bien sûr configuré pour une lecture bit-perfect. WirePlumber est le gestionnaire de session pour PipeWire. Le moniteur ALSA de WirePlumber est responsable de la création des périphériques et des nœuds PipeWire pour toutes les cartes ALSA disponibles sur le système. La configuration de ce moniteur pourra se faire dans le fichier de configuration de WirePlumber. L’ajoute de règles pour configurer les périphériques ALSA spécifiques, en désactivant le resampling et en garantissant une transmission bit-perfect sera un plus. Pour réduire les interférences, désactivation des services non essentiels et l’utilisation d’un système minimal est primordial tout comme configurer également la priorité temps réel pour les processus audio. Il faudra aussi une optimisation de l’installation de Lyrion Music Server.

MAQAM Player est l’interface web tactile optimisée conçue pour le système audiophile MAQAM OS basé sur Arch Linux avec Lyrion/Squeezelite. Voici un résumé des principales caractéristiques et fonctionnalités de l'interface :

- Interface web conviviale pour écrans tactiles
- API pour communiquer avec Lyrion et Squeezelite
- Un serveur léger (lighttpd) pour héberger l'interface
- Des configurations i3 (mode kiosk) spécifiques pour une utilisation tactile et une intégration complète
- Un script de démarrage coordonné pour tous les composants
- Un script de vérification pour s'assurer que tout fonctionne correctement
- Des règles udev pour la reconnaissance des écrans tactiles. Caractéristiques Principales • Performance et Réactivité :  pour une interface fluide. • Qualité Audio Bit-Perfect : Préservation de la qualité audio. • Expérience Utilisateur Intuitive : Adaptée aux écrans tactiles de 5-7 pouces en format paysage. • Design Minimaliste : Contrôles tactiles de grande taille et interface sombre pour un environnement d'écoute optimal. 
- Interface Principale :                                                                                           L'interface est divisée en cinq onglets accessibles via une barre de navigation en haut :
1. Lecture : Lecteur audio principal. Lecteur de fichiers audio et lecteur CD (avec le transport CD ROSE RSA 780).
1. Bibliothèque : Accès à la collection musicale.
1. Extraction : Commandes et propriétés d’extraction au format Flac ou WAV avec le transport CD ROSE RSA 780
1. Sources : Configuration des sources audio.
1. Système : Informations et contrôles système. 

   **Détails :**

   **-Onglet "Lecture" :**

   Mode Plein Écran (Reader Mode) : 

   • Disposition horizontale (format paysage) avec pochette d'album à gauche et informations détaillées sur le morceau à droite 

   - \*\*Contrôles de lecture\*\*:

   - Éjecter CD: Permet d'éjecter un CD physique

   - Shuffle: Active/désactive la lecture aléatoire (s'illumine en orange quand actif)

   - Précédent: Passe au morceau précédent

   - Lecture/Pause: Démarre ou met en pause la lecture

   - Suivant: Passe au morceau suivant

   - Répéter: Active/désactive la répétition (s'illumine en orange quand actif)

   - Stop: Arrête complètement la lecture

   - \*\*Slider de durée\*\*: affichage du temps écoulé/restant et navigation temporelle (permet de contrôler la progression du morceau)

   - \*\*Contrôle du volume\*\*: ON(100%) / MUTE(0%)

   - \*\*Bouton Favoris\*\*: Permet d'ajouter le morceau aux favoris (s'illumine en rouge quand actif)

   - \*\*Bouton Détails\*\*: Ouvre une fenêtre modale avec des informations techniques sur le format audio

   (Titre, Album, Artiste). 

   Les <a name="_hlk199334265"></a>botons de contrôles : Lecture/Pause (même bouton pour les deux), Précédent, Suivant, Shuffle, Repeat, Stop et Éjecter CD sont essentiels donc indispensables. Ces botons de contrôles sont centrés à droite sous les informations détaillées du morceau. Le slider de durée est lui sous les boutons de contrôle de lecture. Un bouton contrôle du volume (On 100% / Mute <a name="_hlk199334077"></a>0%), un bouton « Détails » (informations supplémentaires : Format, Qualité, etc..) et un bouton « Favoris » tous alignés sous le slider de durée. 

   • Affichage du prochain titre (si pas de prochain titre, animation défilement : « Fin de lecture »).

`           `**-Onglet "Bibliothèque" :**

`            `**Permet de parcourir et d'accéder à la collection musicale**

`          `• Barre de Recherche : pour filtrer le contenu. 

`          `• Mini Lecteur :  en bas sur toute largeur de la fenêtre avec les boutons de commande principaux et album-cover (miniature) , track  info( titre, album, artist). 

`          `• Quatre Sous-Onglets :

1. Albums : Affiche une grille de pochettes d'albums avec titre, artiste et nombre de pistes (avec possibilité de lancer la lecture de l’album par double-tap).
1. Artistes : Liste des artistes avec genre et nombre d'albums.
1. Playlists : Liste des playlists avec nombre de pistes et bouton de lecture rapide 

4\.   Favoris : Listes des favoris avec miniature cover (avec possibilité de lancer la lecture par   double-tap). Bouton Favoris à côté du titre permet de retirer le morceau des favoris

`  `**-Onglet "Extraction" :**

` `• Choix du format d'extraction (FLAC ou WAV). 

<a name="_hlk199335379"></a>• Options de qualité (16bit/44.1kHz à 24bit/192kHz

• Choix de destination (stockage local, NAS, USB)

• Options avancées (préservation des métadonnées, normalisation audio). 

• Bouton pour démarrer l'extraction avec simulation de progression. 

**-Onglet "Sources" :**

` `• Liste des sources audio disponibles (DAC USB, S/PDIF Out, NAS Music). 

• Indication de l'état de connexion pour chaque source. 

• Bouton de configuration avancée pour sélectionner le périphérique ALSA 

• Activation/désactivation du mode exclusif. 

**-Onglet "Système" :**

`        `• Informations CPU : utilisation, température, gouverneur

`      `• Informations mémoire : utilisation RAM et stockage

`      `• Informations système : version du noyau Linux, temps de fonctionnement

• État des services critiques :

- lyrion-server
- squeezelite
- pipewire
- wireplumber
- alsa 

• Bouton d'extinction avec confirmation pour arrêter le système en toute sécurité. 

**Informations importantes :** 

• Optimisations Tactiles : Grands boutons, désactivation du zoom sur double-tap, propriété touch-action optimisée. 

• Logo et titre MAQAM Player en haut à gauche

• Thème et Design : Thème sombre, couleur principale orange (#ff9800), contraste élevé, design responsive.

**La disposition des éléments de l’onglet « Lecture » (boutons de commande, slider de** 

`     `**durée, album-cover, ect.) devra être la même que sur l’image en pièce jointe (Vue    Lecture).**
