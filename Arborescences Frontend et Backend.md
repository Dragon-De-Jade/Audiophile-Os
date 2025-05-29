1. Frontend : maqam-player-frontend/ (Vue.js avec Vite & TypeScript)

\# Variables d'environnement pour le frontend

maqam-player-frontend/

├── .env

(VITE\_\*)

├── .editorconfig

├── .eslintrc.cjs

JavaScript/TypeScript/Vue

├── .gitignore

├── .prettierrc.json

├── coverage/

(généré par Vitest)

│   └── vitest/

├── dist/

(généré par `npm run build`)

├── index.html

├── node\_modules/

├── package.json

├── package-lock.json

├── playwright.config.ts

├── postcss.config.cjs

├── public/

│   └── favicon.ico

├── src/

│   ├── App.vue

principal, layout)

│   ├── main.ts

Pinia, Router, i18n)

│   ├── env.d.ts

d'environnement Vite

│   ├── shims-vue.d.ts

│   ├── assets/

(CSS, images, polices)

│   │   └── styles/

\# Configuration de style de code pour les éditeurs

\# Configuration ESLint pour le linting

\# Fichiers et dossiers à ignorer par Git

\# Configuration Prettier pour le formatage du code

\# Répertoire des rapports de couverture de tests

\# Répertoire de sortie du build de production

\# Point d'entrée HTML de l'application SPA

\# Dépendances du projet (géré par npm/yarn)

\# Manifeste du projet : scripts, dépendances, etc.

\# Verrouillage des versions des dépendances

\# Configuration pour les tests E2E Playwright

\# Configuration PostCSS (si utilisé)

\# Assets statiques copiés tels quels dans `dist/`

\# Icône de l'application

\# Code source de l'application Vue.js

\# Composant racine de l'application (shell

\# Point d'entrée de l'application (initialise Vue,

\# Déclarations de types pour les variables

\# Shims de type pour les fichiers .vue en TypeScript

\# Ressources statiques utilisées par l'application

│   │       ├── global.css    # Styles globaux de base, variables CSS

│   │       ├── main.css

\# Fichier principal important les autres CSS (reset,

global, utilities)

│   │       ├── reset.css     # Reset CSS pour normaliser les styles navigateur

│   │       └── utilities.css # Classes utilitaires CUBE CSS

│   ├── components/

\# Composants Vue réutilisables

│   │   ├── common/

\# Composants communs à plusieurs vues

│   │   │   ├── BaseButton.vue

│   │   │   ├── ConfirmationModal.vue

│   │   │   └── \_\_tests\_\_/

│   │   │       └── BaseButton.spec.ts # Test unitaire pour BaseButton

│   │   ├── bibliotheque/

\# Composants spécifiques à la vue Bibliothèque

│   │   │   ├── MiniPlayer.vue

│   │   │   ├── SearchBar.vue

│   │   │   └── sousVues/     # Composants pour les sous-onglets de la

bibliothèque

│   │   │       ├── AlbumsView.vue

│   │   │       ├── ArtistsView.vue

│   │   │       ├── FavoritesView.vue

│   │   │       ├── PlaylistsView.vue

│   │   │       └── TracksListView.vue

│   │   ├── extraction/

\# Composants spécifiques à la vue Extraction

│   │   │   ├── EditableMetadataField.vue

│   │   │   └── TrackMetadataRow.vue

│   │   ├── lecture/

\# Composants spécifiques à la vue Lecture

│   │   │   ├── AlbumArt.vue

│   │   │   ├── NextTrackDisplay.vue

│   │   │   ├── PlaybackControls.vue

│   │   │   ├── ProgressBar.vue

│   │   │   ├── TrackDetailsModal.vue

│   │   │   ├── TrackInfoDisplay.vue

│   │   │   └── VolumeControl.vue

│   │   └── system/

\# Composants spécifiques à la vue Système

│   │       ├── ResourceMonitor.vue

│   │       └── ServiceStatusCard.vue

│   ├── locales/

\# Fichiers de traduction pour Vue I18n

│   │   ├── en.json

│   │   └── fr.json

│   ├── router/

│   │   └── index.ts

│   ├── services/

│   │   └── apiClient.ts

(Node.js, CD Python)

│   ├── store/

│   │   ├── \_\_tests\_\_/

\# Traductions anglaises

\# Traductions françaises

\# Configuration de Vue Router

\# Définition des routes de l'application

\# Logique pour interagir avec les APIs backend

\# Client HTTP (Axios) configuré pour les API

\# Stores Pinia pour la gestion de l'état global

\# Tests pour les stores Pinia

│   │   │   └── ui.spec.ts    # Test unitaire pour uiStore

│   │   ├── index.ts

\# Fichier d'initialisation de Pinia (souvent vide,

fait dans main.ts)

│   │   ├── auth.ts

│   │   ├── cd.ts

│   │   ├── library.ts

(LMS)

│   │   ├── player.ts

(LMS/Squeezelite)

│   │   ├── sources.ts

│   │   └── ui.ts

(onglet actif, etc.)

│   └── views/

principales (pages)

│

├── \_\_tests\_\_/

│

\# Store pour l'authentification (clé API)

\# Store pour l'état et les opérations CD

\# Store pour les données de la bibliothèque musicale

\# Store pour l'état du lecteur audio

\# Store pour la gestion des sources audio

\# Store pour l'état de l'interface utilisateur

\# Composants Vue correspondant aux routes

\# Tests pour les vues

│   └── SourcesView.spec.ts # Test d'intégration pour SourcesView

│

│

│

├── BibliothequeView.vue

├── ExtractionView.vue

├── HomeView.vue

réutilisée)

│

├── LectureView.vue

│

│

├── SourcesView.vue

└── SystemeView.vue

├── tests/

│   ├── e2e/

\# Vue d'accueil initiale (pourrait être retirée ou

\# Répertoire principal pour les tests Playwright

\# Tests de bout en bout (End-to-End)

│   │   ├── navigation.spec.ts

│   │   └── player\_controls.spec.ts

│   └── (autres fichiers de support Playwright générés par `npx playwright init`)

├── tsconfig.json

\# Configuration TypeScript pour le projet

├── tsconfig.node.json

Node.js (vite.config, etc.)

└── vitest.setup.ts

\# Configuration TypeScript pour les fichiers liés à

\# Fichier de configuration global pour les tests

Vitest (mocks, etc.)


1. Backend : maqam-node-api/ (API Node.js avec Express & TypeScript)

maqam-node-api/

├── .env                      # Variables d'environnement pour l'API Node.js

(PORT, API\_KEY, LMS\_URL)

├── .eslintrc.json            # Configuration ESLint

├── .gitignore                # Fichiers à ignorer par Git

├── .prettierrc.json          # Configuration Prettier

├── coverage/                 # Répertoire des rapports de couverture de tests

(généré par Jest)

│   └── jest/

├── dist/                     # Répertoire de sortie du build TypeScript (généré

par `npm run build`)

├── node\_modules/             # Dépendances du projet

├── package.json              # Manifeste du projet Node.js

├── package-lock.json         # Verrouillage des versions

├── jest.config.js            # Configuration Jest pour les tests

├── tsconfig.json             # Configuration TypeScript pour le projet backend

└── src/                      # Code source de l'API Node.js

├── app.ts                # Configuration principale de l'application Express

(middlewares, routes)

├── server.ts             # Point d'entrée du serveur HTTP (lance

l'application Express)

├── config/               # Configuration de l'application

│   ├── index.ts          # Charge et exporte la configuration (depuis .env)

│   └── userPreferences.json # Fichier pour stocker les préférences

utilisateur (gestion basique)

├── api/                  # Contient toute la logique liée à l'API (routes,

contrôleurs, middlewares)

│   ├── controllers/      # Logique de gestion des requêtes, interaction avec

les services

│   │   ├── lmsController.ts    # Contrôleur pour les fonctionnalités LMS

│   │   └── systemController.ts # Contrôleur pour les fonctionnalités système

(préférences, infos, etc.)

│   ├── middleware/       # Middlewares Express

│   │   └── authMiddleware.ts # Middleware pour l'authentification par clé API

│   └── routes/           # Définition des routes de l'API

│       ├── \_\_tests\_\_/    # Tests d'intégration pour les routes

│       │   └── lmsRoutes.integration.spec.ts # Test pour les routes LMS

│       ├── lmsRoutes.ts        # Routes pour les fonctionnalités LMS

│       ├── musicbrainzRoutes.ts # (À créer) Routes pour le proxy MusicBrainz

│       └── systemRoutes.ts     # Routes pour les fonctionnalités système

├── services/             # Logique métier et interaction avec des services

externes

│   ├── \_\_tests\_\_/        # Tests unitaires pour les services

│   │   └── lmsApiService.spec.ts # Test pour le service LMS

│   ├── lmsApiService.ts    # Service pour interagir avec l'API de Lyrion

Music Server

│   └── musicbrainzService.ts # (À créer) Service pour interagir avec l'API

MusicBrainz

└── utils/                # Fonctions utilitaires

├── \_\_tests\_\_/        # Tests pour les utilitaires

│   └── formatters.spec.ts # Exemple de test pour un formateur

└── formatters.ts     # Exemple de fichier pour des fonctions de formatage
