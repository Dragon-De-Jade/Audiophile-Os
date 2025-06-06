﻿**Lecteur MAQAM** 



**Tâche 1-Mettre en place la structure initiale du projet et l'environnement de développement** 

***Description :***

Créer la structure de base du projet pour l'application web MAQAM Player, y compris l'organisation des répertoires, les fichiers de configuration et la configuration des dépendances. Cette tâche comprend la configuration de Vue 3 avec l'API de composition comme framework frontend, la configuration d'un environnement de développement à l'aide de Vite comme outil de build et l'établissement du pipeline de build. L'application prendra en charge les langues française et anglaise avec la possibilité de changement de langue.



***Critères de succès :***    

1\. La structure des répertoires du projet est créée et organisée logiquement.    

2\. Tous les fichiers de configuration nécessaires sont en place.    

3\. L'environnement de développement peut être démarré avec une seule commande.    

4\. Toutes les dépendances sont correctement installées et versionnées.    

5\. Le processus de build est configuré et opérationnel.    

6\. Vue 3 avec l'API de composition est correctement configuré.    

7\. Vite est configuré pour un développement rapide et des builds de production optimisés.    

8\. Les performances initiales respectent les métriques cibles (chargement < 2s, interactions < 100ms).    

9\. L'infrastructure de support multilingue est en place.



***Plan de vérification :*** 

1\. Exécuter un script qui vérifie l'existence de tous les répertoires et fichiers requis.    

2\. Exécuter la commande de démarrage de l'environnement de développement et vérifier qu'elle s'exécute sans erreurs.    

3\. Exécuter un build de test et vérifier que la sortie est générée correctement.    

4\. Vérifier que toutes les dépendances peuvent être installées à partir de zéro sur un nouveau système.    

5\. Tester la fonctionnalité de remplacement de module à chaud en développement.    

6\. Vérifier que le changement de langue fonctionne entre le français et l'anglais.



**Tâche 2-Développer l'API backend pour la communication avec Lyrion et Squeezelite (1dépendance)** 

***Description :***

Créer un service API RESTful qui s'interface avec Lyrion et Squeezelite pour contrôler la lecture audio, gérer les bibliothèques musicales et gérer les fonctions système. L'API sera construite à l'aide de Node.js avec Express et fournira des points de terminaison pour toutes les fonctionnalités requises. L'API utilisera une authentification simple par clé API pour une protection de base et communiquera directement avec les API Lyrion et Squeezelite lorsqu'elles seront disponibles. Les préférences et paramètres utilisateur seront stockés dans des fichiers de configuration sur le système plutôt que dans le navigateur.



***Critères de succès :*** 

1\. Tous les points de terminaison de l'API sont implémentés et fonctionnent correctement.    

2\. L'API peut communiquer avec Lyrion et Squeezelite.    

3\. L'API renvoie les codes d'état et les messages d'erreur appropriés.    

4\. Les réponses de l'API sont cohérentes et bien formatées.    

5\. Les performances de l'API répondent aux exigences (temps de réponse < 100 ms).    

6\. Toutes les fonctionnalités requises par le frontend sont prises en charge par l'API.    

7\. L'authentification simple par clé API est implémentée.    

8\. Les fichiers de configuration sont correctement gérés pour les paramètres utilisateur.    

9\. Une connexion réseau est requise - pas de prise en charge hors ligne. 

***Plan de vérification :*** 

1\. Créer des tests automatisés pour chaque point de terminaison de l'API à l'aide d'outils comme Mocha/Jest.    

2\. Tester l'intégration de l'API avec Lyrion et Squeezelite dans un environnement de test.    

3\. Tester la charge de l'API avec un outil comme Artillery pour vérifier les performances.    

4\. Créer un script de test qui vérifie toutes les fonctionnalités requises pour chaque onglet de l'interface.    

5\. Vérifier manuellement la fonctionnalité d'extraction et de lecture de CD.    

6\. Tester que l'authentification par clé API fonctionne correctement.    

7\. Vérifier que les fichiers de configuration système sont correctement créés et lus.



***Dépendance :*** 

\*Mettre en place la structure initiale du projet et l'environnement de développement



**Tâche 3-Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs (1 dépendance)**
\***


***Description :*** 

Implémenter l'infrastructure frontend Vue.js de base, y compris le shell de l'application, le système de navigation, la gestion de l'état et les composants réutilisables. Cette tâche se concentre sur la création de la base qui prendra en charge toutes les vues et fonctionnalités. L'implémentation utilisera TypeScript pour une meilleure maintenabilité et expérience développeur, et la méthodologie CUBE CSS pour le style. L'interface utilisateur sera optimisée pour les écrans tactiles paysage de 5 à 7 pouces avec un design réactif, et prendra en charge les langues française et anglaise.



***Critères de succès :***    

1\. Le shell de l'application s'affiche correctement avec la navigation par onglets.    

2\. Le store Vuex est correctement configuré avec tous les modules requis.    

3\. Tous les composants communs sont implémentés et réutilisables.    

4\. Le routage fonctionne correctement pour toutes les vues.    

5\. La couche de service API communique avec succès avec le backend.    

6\. Le thème est appliqué de manière cohérente avec un fond sombre et des accents orange.    

7\. L'interface utilisateur est réactive et optimisée pour les écrans tactiles.    

8\. TypeScript est correctement configuré avec les types appropriés.    

9\. La méthodologie CUBE CSS est implémentée de manière cohérente.    

10\. Les performances respectent les métriques cibles (interactions < 100ms).    

11\. Le changement de langue entre le français et l'anglais fonctionne correctement.    

***Plan de vérification :*** 

1\. Créer des tests unitaires pour tous les composants communs.    

2\. Créer des tests unitaires pour les modules du store Vuex.    

3\. Tester la navigation entre toutes les routes.    

4\. Vérifier la couche de service API avec un backend simulé.    

5\. Tester la réactivité sur différentes tailles d'écran (paysage 5-7 pouces).    

6\. Vérifier l'optimisation tactile sur les appareils tactiles réels.    

7\. Effectuer des tests d'accessibilité pour le contraste des couleurs et les cibles tactiles.    

8\. Vérifier que la vérification de type TypeScript passe sans erreurs.    

9\. Tester que le changement de langue fonctionne correctement dans toute l'application.



***Dépendance :*** 

\*Mettre en place la structure initiale du projet et l'environnement de développement 



**Tâche 4-Implémenter l'intégration avec le transport CD ROSE RSA 780 pour la lecture et l’extraction (1 dépendance)**
\***


***Description :*** 

Développer la couche d'intégration matérielle qui communique avec le transport CD ROSE RSA 780 pour la lecture et l'extraction de CD à l'aide de l'interface de contrôle USB. Cette tâche implique la création des pilotes nécessaires, des protocoles de communication et de la gestion des erreurs pour assurer un fonctionnement fiable avec le transport CD. La lecture de CD se fera en streaming directement depuis le disque sans mise en cache pour maintenir une qualité audio bit-perfect.



***Critères de succès :***    

1\. Le système peut détecter lorsqu'un CD est inséré.    

2\. Les commandes de lecture, pause, arrêt, piste suivante, piste précédente, répétition de la piste (en cours de lecture), lecture aléatoire, éjection et navigation de piste fonctionnent correctement.    

3\. Les métadonnées du CD sont correctement récupérées et affichées via MusicBrainz.    

4\. La fonctionnalité d'extraction fonctionne de manière fiable.    

5\. La gestion des erreurs est robuste pour les problèmes courants de CD (rayures, disques illisibles).    

6\. Les performances sont optimales avec une latence minimale.    

7\. L'intégration fonctionne de manière cohérente après les redémarrages du système.    

8\. L'audio bit-perfect est maintenu grâce au streaming direct.    

***Plan de vérification :*** 

1\. Tester la détection de CD avec divers CD.    

2\. Vérifier que toutes les commandes de lecture fonctionnent correctement.    

3\. Tester l'extraction avec divers CD.    

4\. Tester la gestion des erreurs avec des CD endommagés ou problématiques.    

5\. Vérifier que les performances répondent aux exigences.    

6\. Tester le système à travers plusieurs cycles de redémarrage.    

7\. Mener des tests de lecture prolongés pour la stabilité.    

8\. Vérifier la lecture bit-perfect à l'aide d'outils d'analyse audio.    

***Dépendance :*** 

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite\* 



**Tâche 5-Implémenter la vue Sources pour la gestion et la configuration des sources audio (2 dépendances)**



***Description :*** 

Développer l'interface des sources audio (onglet Sources) qui permet aux utilisateurs de visualiser, sélectionner et configurer diverses sources audio. Cette vue doit fournir une indication claire de l'état de la connexion et un accès aux options de configuration pour chaque source. Lorsqu'une source précédemment configurée devient indisponible, le système invitera l'utilisateur à sélectionner une nouvelle source ou à réessayer la connexion. Toutes les options de configuration ALSA seront exposées à l'utilisateur, mais organisées dans une section 'avancée' distincte pour garder l'interface principale claire.  

***Critères de succès:***    

1\. Toutes les sources audio sont affichées avec le statut correct.    

2\. La sélection de la source modifie la sortie audio active.    

3\. Les options de configuration sont appropriées pour chaque type de source.    

4\. La sélection du périphérique ALSA fonctionne correctement.    

5\. Le basculement du mode exclusif fonctionne correctement.    

6\. Les sources réseau peuvent être configurées et accessibles.    

7\. Les périphériques USB sont correctement détectés et configurables.    

8\. Les modifications apportées aux paramètres sont persistantes et appliquées immédiatement.    

9\. L'interface fournit un retour clair sur l'état de la configuration.    

10\. Une invite utilisateur apparaît lorsqu'une source devient indisponible.    

11\. La section de configuration ALSA avancée contient toutes les options.    

12\. Les paramètres sont enregistrés dans les fichiers de configuration système.    

***Plan de vérification :*** 

1\. Tester la sélection de source avec divers périphériques audio.    

2\. Vérifier la sélection du périphérique ALSA avec différentes options de sortie.    

3\. Tester la fonctionnalité du mode exclusif.    

4\. Vérifier la configuration et la connexion de la source réseau.    

5\. Tester la détection de périphériques USB avec divers périphériques.    

6\. Vérifier la persistance des paramètres lors des redémarrages de l'application.    

7\. Tester la gestion des erreurs pour les sources déconnectées ou indisponibles.    

8\. Vérifier que la sortie audio change réellement lorsque les sources sont changées.    

9\. Tester la fonctionnalité d'invite lorsque les sources deviennent indisponibles.    

10\. Vérifier que toutes les options ALSA fonctionnent correctement dans la section avancée.
\***


***Dépendances :*** 

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs    

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite



**Tâche 6-Implémenter la vue Système pour afficher les informations et les contrôles du système (2 dépendances)**    

***Description :*** 

Développer l'interface d'information et de contrôle du système (onglet Système) qui affiche l'état du système, la santé des services et fournit des fonctions de contrôle du système comme l'arrêt. Cette vue doit donner aux utilisateurs un aperçu clair de la santé et des performances du système. Les informations sur l'état du système seront rafraîchies toutes les 1-2 secondes pour une surveillance en temps réel. L'interface fournira des contrôles avancés, y compris les mises à jour du système dans le cadre du système de mise à jour automatique avec notifications utilisateur.  

***Critères de succès :***    

1\. Les informations système sont précises et complètes.    

2\. Les indicateurs d'état des services reflètent correctement l'état réel des services.    

3\. Le bouton d'arrêt fonctionne correctement avec une confirmation appropriée.    

4\. La surveillance des ressources affiche des informations précises et en temps réel avec un taux de rafraîchissement de 1 à 2 secondes.    

5\. Les fonctions de redémarrage des services fonctionnent comme prévu.    

6\. Toutes les informations sont présentées dans un format clair et lisible.    

7\. Les informations de diagnostic sont utiles et accessibles.    

8\. La fonctionnalité de mise à jour du système est implémentée avec des notifications utilisateur.    

9\. Le système de mise à jour automatique fonctionne correctement.    

***Plan de vérification :*** 

1\. Vérifier l'exactitude des informations système par rapport aux spécifications réelles du système.    

2\. Tester l'état du service en arrêtant/démarrant manuellement les services.    

3\. Tester la fonctionnalité d'arrêt dans un environnement sûr.    

4\. Vérifier la précision de la surveillance des ressources avec différentes charges système.    

5\. Tester la fonctionnalité de redémarrage des services.    

6\. Vérifier l'accès aux journaux et aux informations de diagnostic.    

7\. Tester la fonctionnalité de vérification des mises à jour et de notification.    

8\. Vérifier que les informations se rafraîchissent toutes les 1-2 secondes.    

9\. Tester le système de mise à jour automatique avec notification utilisateur.    

***Dépendances :*** 

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs    

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite



**Tâche 7-Configurer le serveur web lighttpd pour héberger l'interface MAQAM Player (1 dépendance)** 

***Description :*** 

Mettre en place et configurer le serveur web lighttpd pour héberger l'interface web MAQAM Player. Cela inclut l'optimisation des performances, la configuration du routage approprié pour la prise en charge des applications monopages et la configuration des paramètres de sécurité. Le serveur fonctionnera sur le port alternatif 8080 pour éviter les conflits avec d'autres services, et ne sera accessible que sur le réseau local pour des raisons de sécurité.  

***Critères de succès :***    

1\. Le serveur Lighttpd héberge avec succès l'interface MAQAM Player sur le port 

8080\.    

2\. Le routage SPA fonctionne correctement pour toutes les routes frontend.    

3\. Les ressources statiques sont servies efficacement avec une mise en cache appropriée.    

4\. Le serveur fonctionne bien avec une utilisation minimale des ressources.    

5\. Les paramètres de sécurité restreignent l'accès au réseau local uniquement.    

6\. Le serveur démarre automatiquement avec le système.    

7\. La journalisation est correctement configurée.    

***Plan de vérification :***

1\. Tester le démarrage et l'accessibilité du serveur sur le port 8080.    

2\. Vérifier que toutes les routes frontend fonctionnent correctly.    

3\. Tester les performances avec des outils comme Lighthouse ou WebPageTest.    

4\. Vérifier la mise en cache correcte des ressources statiques.    

5\. Tester le redémarrage et la récupération du serveur.    

6\. Vérifier le démarrage automatique avec le démarrage du système.    

7\. Vérifier la création et la rotation des journaux.    

8\. Mener des tests de sécurité de base, y compris des tentatives d'accès depuis l'extérieur du réseau local.    

***Dépendance :*** 

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs 

**Tâche 8-Implémenter la vue Lecture avec lecteur plein écran et contrôles de lecture (3 dépendances)** 

***Description :*** 

Développer l'interface de lecture principale (onglet Lecture) qui affiche les informations sur la piste en cours, la pochette de l'album et les commandes de lecture. Cette vue sera l'interface principale pour lire et contrôler la lecture de musique. Le lecteur prendra en charge l'orientation paysage uniquement comme spécifié dans les exigences. Pour les pochettes d'album manquantes ou de faible qualité, le système générera un dégradé coloré basé sur le nom de l'album.  

***Critères de succès*** :    

1\. La disposition de l'interface utilisateur correspond précisément à l'image de référence.    

2\. Toutes les commandes de lecture fonctionnent correctement.    

3\. La pochette de l'album s'affiche correctement en haute qualité. 

4\. La pochette d'album manquante est remplacée par un dégradé coloré basé sur le nom de l'album.    

5\. Les informations sur la piste sont affichées avec précision.    

6\. Tous les boutons et contrôles sont optimisés pour le toucher.    

7\. La position de lecture se met à jour en temps réel.    

8\. Les informations sur la piste suivante sont affichées.    

9\. Le contrôle du volume bascule entre 100% et muet.    

10\. Les boutons Détails et Favoris fonctionnent correctement.    

11\. L'interface fonctionne correctement sur les écrans paysage de 5 à 7 pouces.    

***Plan de vérification :*** 

1\. Comparer l'implémentation à l'image de référence pour la fidélité visuelle.    

2\. Tester toutes les commandes de lecture avec une lecture audio réelle.    

3\. Tester la réactivité sur les tailles d'écran cibles (écrans 5-7 pouces).    

4\. Vérifier les mises à jour en temps réel de la position de lecture.    

5\. Tester les interactions tactiles sur les appareils tactiles réels.    

6\. Vérifier l'affichage correct des informations sur la piste avec diverses métadonnées.    

7\. Tester la fonctionnalité de contrôle du volume.    

8\. Vérifier que les dégradés générés pour les pochettes d'album manquantes sont visuellement agréables.    

***Dépendances :*** 

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs    

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite    

\*Implémenter l'intégration avec le transport CD ROSE RSA 780 pour la lecture et l'extraction    

**Tâche 9-Implémenter la vue Bibliothèque avec la navigation par albums, artistes, playlists et favoris (3 dépendances)** 

***Description :***

Développer l'interface de la bibliothèque (onglet Bibliothèque) qui permet aux utilisateurs de parcourir et de rechercher leur collection de musique à travers diverses vues organisationnelles. Cette vue doit fournir une navigation facile des albums, artistes, playlists et favoris avec des commandes optimisées pour le toucher. Le nombre d'éléments affichés dans les vues grille/liste sera dynamique en fonction de la taille et de la résolution de l'écran pour garantir une utilisation optimale des écrans de 5 à 7 pouces. Les playlists prendront en charge le réordonnancement par glisser-déposer, mais uniquement dans une vue d'édition de playlist dédiée pour garder l'interface principale claire.  

***Critères de succès :***    

1\. Les quatre sous-onglets (Albums, Artistes, Playlists, Favoris) sont implémentés et fonctionnels.    

2\. La fonctionnalité de recherche filtre le contenu dans toutes les catégories.    

3\. Le mini-lecteur affiche la piste en cours et les commandes de base.    

4\. Les albums s'affichent sous forme de grille avec les pochettes.    

5\. Les artistes s'affichent sous forme de liste avec le genre et le nombre d'albums.    

6\. Les playlists s'affichent sous forme de liste avec le nombre de pistes.    

8\. Les favoris s'affichent avec les vignettes d'album.    

9\. Le bouton Historique ouvre l'historique d'écoute.    

10\. Toutes les interactions sont optimisées pour le toucher.    

11\. Les performances sont fluides lors de la navigation dans de grandes bibliothèques.    

12\. Le nombre d'éléments grille/liste s'adapte dynamiquement à la taille de l'écran.    

13\. Un éditeur de playlist dédié avec réordonnancement par glisser-déposer est implémenté.    

***Plan de vérification :***

1\. Tester la navigation entre tous les sous-onglets.    

2\. Tester la fonctionnalité de recherche avec diverses requêtes.    

3\. Vérifier que la grille d'albums s'affiche correctement avec diverses pochettes.    

4\. Tester la liste des artistes avec le tri et le filtrage.    

5\. Tester la création, l'édition et la lecture de playlists.    

6\. Vérifier que les favoris peuvent être ajoutés et supprimés.    

7\. Tester les commandes du mini-lecteur.    

8\. Tester les performances avec une grande bibliothèque musicale (plus de 1000 albums).    

9\. Vérifier les interactions tactiles sur les appareils cibles.    

10\. Tester l'adaptation dynamique de la grille/liste sur différentes résolutions d'écran.    

11\. Vérifier que la fonctionnalité de glisser-déposer de l'éditeur de playlist fonctionne correctement.    

***Dépendances :***

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs    

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite    

\*Implémenter l'intégration avec le transport CD ROSE RSA 780 pour la lecture et l'extraction    

**Tâche 10-Implémenter la vue Extraction pour la fonctionnalité d'extraction de CD avec le transport ROSE RSA 780 (3 dépendances)** 

***Description :*** 

Développer l'interface d'extraction de CD (onglet Extraction) qui permet aux utilisateurs d'extraire des CD aux formats FLAC ou WAV à l'aide du transport CD ROSE RSA 780. Cette vue doit fournir des options pour la qualité d'extraction, la destination et les paramètres avancés. Les métadonnées du CD proviendront de l'API MusicBrainz pour des métadonnées complètes. L'interface comprendra un bouton de sélection pour les paramètres de qualité d'extraction plutôt que des valeurs par défaut prédéfinies.  

***Critères de succès :***    

1\. La sélection du format entre FLAC et WAV fonctionne correctement.    

2\. Les options de qualité sont appropriées pour chaque format et peuvent être sélectionnées via un bouton dédié.    

3\. La sélection de la destination permet de choisir des emplacements de stockage valides.    

4\. Les options avancées sont correctement implémentées.    

5\. Le processus d'extraction affiche une progression précise.    

6\. Les informations du CD sont affichées et modifiables.    

7\. L'intégration de l'API MusicBrainz pour la récupération des métadonnées fonctionne correctement.    

8\. L'interface communique avec le transport CD ROSE RSA 780.    

9\. Les fichiers extraits sont correctement nommés et organisés.    

10\. La gestion des erreurs est robuste avec un retour utilisateur clair.    

***Plan de vérification :*** 

1\. Tester la sélection du format et vérifier que le format correct est utilisé.    

2\. Tester les options de qualité et vérifier que la sortie correspond aux sélections.    

3\. Tester la sélection de destination avec diverses options de stockage.    

4\. Vérifier l'édition et la préservation des métadonnées.    

5\. Tester le processus d'extraction avec des CD réels.    

6\. Vérifier la précision du rapport de progression.    

7\. Tester les conditions d'erreur (CD rayé, espace insuffisant).    

8\. Vérifier l'intégration du ROSE RSA 780.    

9\. Vérifier les fichiers résultants pour le format, la qualité et les métadonnées corrects.    

10\. Vérifier l'intégration de l'API MusicBrainz pour récupérer les métadonnées du CD.    

***Dépendances :***

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs    

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite.    

\*Implémenter l'intégration avec le transport CD ROSE RSA 780 pour la lecture et l'extraction.   

**Tâche 11-Configurer le gestionnaire de fenêtres i3 en mode kiosque pour l'interface MAQAM Player (1 dépendance).**    

***Description :***

Mettre en place et configurer le gestionnaire de fenêtres i3 pour fonctionner en mode kiosque, offrant un environnement plein écran optimisé pour le toucher pour l'interface MAQAM Player. Cela implique la création de configurations et de scripts i3 spécialisés pour créer une expérience utilisateur transparente. Le navigateur Chromium sera utilisé pour un meilleur support du mode kiosque et de meilleures performances. Les mises à jour système seront gérées automatiquement pendant les fenêtres de maintenance planifiées dans le cadre du système de mise à jour automatique avec notifications utilisateur.  

***Critères de succès :***    

1\. i3 démarre automatiquement en mode kiosque.    

2\. Le navigateur Chromium se lance en plein écran sans éléments d'interface utilisateur.    

3\. L'interface MAQAM Player se charge automatiquement.    

4\. L'entrée tactile fonctionne correctement sans interférence du système.    

5\. Le système est sécurisé contre les tentatives de l'utilisateur de quitter le mode kiosque.    

6\. L'écran reste allumé sans s'éteindre ni entrer en mode économiseur d'écran.    

7\. Le système récupère automatiquement après les plantages du navigateur.    

8\. Les mises à jour système sont installées automatiquement pendant les fenêtres de maintenance planifiées.    

***Plan de vérification :*** 

1\. Tester le démarrage automatique d'i3 en mode kiosque.    

2\. Vérifier que le navigateur Chromium se lance correctement en plein écran.    

3\. Tester la fonctionnalité d'entrée tactile.    

4\. Tenter de sortir du mode kiosque à l'aide des raccourcis clavier.    

5\. Tester la prévention de l'extinction de l'écran.    

6\. Simuler un plantage du navigateur et vérifier la récupération.    

7\. Tester avec différents matériels d'écran tactile.    

8\. Vérifier la mise à l'échelle appropriée sur l'affichage cible.    

9\. Tester le système de mise à jour automatique pendant les fenêtres de maintenance.    

***Dépendance :*** 

\*Configurer le serveur web lighttpd pour héberger l'interface MAQAM Player    

**Tâche 12-Implémenter des tests complets et une assurance qualité pour le MAQAM Player (5 dépendances)** 

***Description :*** 

Développer et exécuter une stratégie de test complète pour le MAQAM Player afin d'assurer la fonctionnalité, les performances et la fiabilité. Cela comprend les tests unitaires, les tests d'intégration, les tests de bout en bout et les tests d'acceptation utilisateur sur tous les composants. Les tests se concentreront sur les chemins critiques avec une couverture élevée 

(90%+) et utiliseront une approche équilibrée avec à la fois des tests unitaires et des tests d'intégration/E2E pour assurer une vérification complète du système.  

***Critères de succès :***    

1\. Les chemins critiques ont une couverture de test d'au moins 90%.    

2\. Tous les points de terminaison de l'API ont des tests d'intégration.    

3\. Tous les composants de l'interface utilisateur ont des tests unitaires et d'intégration.    

4\. Les tests de bout en bout couvrent tous les flux utilisateur critiques.    

5\. Les performances répondent aux exigences cibles (réponse de l'interface utilisateur <100 ms, chargement initial <2 s).    

6\. Mélange équilibré de tests unitaires et de tests d'intégration/E2E.    

7\. Tous les principaux navigateurs et appareils sont testés.    

8\. La conformité à l'accessibilité est vérifiée.    

9\. Les tests d'acceptation utilisateur sont terminés avec succès.    

10\. Les interfaces française et anglaise sont testées de manière approfondie.    

***Plan de vérification :*** 

1\. Exécuter la suite de tests automatisée et vérifier les métriques de couverture pour les chemins critiques.    

2\. Effectuer des tests manuels de tous les composants et vues de l'interface utilisateur.    

3\. Effectuer des tests de charge pour vérifier les performances sous contrainte.    

4\. Tester sur le matériel cible réel (écrans tactiles de 5 à 7 pouces).    

5\. Vérifier la compatibilité des navigateurs.    

6\. Exécuter des audits d'accessibilité.    

7\. Mener des tests d'acceptation utilisateur avec des utilisateurs réels.    

8\. Documenter tous les résultats des tests et les problèmes résolus.    

9\. Vérifier que la fonctionnalité de changement de langue fonctionne correctement.    

10\. Assurer l'équilibre entre les tests unitaires et les tests d'intégration/E2E.    

***Dépendances :***  

\*Implémenter la vue Lecture avec lecteur plein écran et contrôles de lecture  

\*Implémenter la vue Bibliothèque avec la navigation par albums, artistes, playlists et favoris 

\*Implémenter la vue Extraction pour la fonctionnalité d'extraction de CD avec le transport 

ROSE RSA 780  

\*Implémenter la vue Sources pour la gestion et la configuration des sources audio 

\*Implémenter la vue Système pour afficher les informations et les contrôles du système  

**Tâche 13-Implémenter la prise en charge de l'écran tactile et les règles udev pour les appareils tactiles (2 dépendances)**  

***Description :*** 

Développer la configuration et le code nécessaires pour assurer une intégration optimale de l'écran tactile pour l'interface MAQAM Player. Cela comprend la création de règles udev appropriées pour la détection des périphériques, les outils d'étalonnage et les modèles d'interaction optimisés pour le toucher. Le système prendra en charge n'importe quel écran tactile avec des pilotes Linux standard pour maximiser la compatibilité. Seuls les gestes multi

touch de base (taper, glisser, pincer-zoomer) seront implémentés pour garder l'interface intuitive et réactive.



***Critères de succès :***    

1\. Les écrans tactiles sont automatiquement détectés et configurés.    

2\. L'entrée tactile est précise et réactive.    

3\. Des règles udev appropriées sont en place pour divers modèles d'écrans tactiles avec des pilotes Linux standard.    

4\. Des outils d'étalonnage sont disponibles si nécessaire.    

5\. Les gestes multi-touch de base (taper, glisser, pincer-zoomer) fonctionnent correctement.    

6\. Les interactions tactiles sont cohérentes dans toute l'application.    

7\. Un retour visuel est fourni pour les interactions tactiles.    

8\. Le système fonctionne avec des écrans tactiles de 5 à 7 pouces comme spécifié.  

***Plan de vérification :***    

1\. Tester avec plusieurs modèles d'écrans tactiles utilisant des pilotes Linux standard.    

2\. Vérifier la précision tactile sur tout l'écran.    

3\. Tester toutes les interactions tactiles dans toute l'application.    

4\. Vérifier que les règles udev identifient correctement les périphériques tactiles.    

5\. Tester les gestes multi-touch de base (taper, glisser, pincer-zoomer).    

6\. Vérifier le retour visuel sur toutes les interactions tactiles.    

7\. Tester les cas limites comme les touches multiples rapides.    

8\. Vérifier que le système fonctionne après la déconnexion et la reconnexion des périphériques.



***Dépendances :***  

\*Développer l'infrastructure frontend de base, y compris le routage, la gestion de l'état et les composants communs. 

\*Configurer le gestionnaire de fenêtres i3 en mode kiosque pour l'interface MAQAM Player.   

**Tâche 14-Développer des scripts système pour l'installation, le démarrage et la vérification (4 dépendances)**
**


***Description :***  

Créer un ensemble de scripts système pour gérer l'installation, la coordination du démarrage et la vérification du système pour le MAQAM Player. Ces scripts assureront une intégration correcte avec le système Arch Linux et un fonctionnement fiable de tous les composants. L'installation fournira deux modes : express (automatisé) et avancé (interactif) pour répondre aux différents besoins des utilisateurs. En cas d'échec de la détection du matériel, le système entrera dans un mode de dépannage interactif pour guider l'utilisateur dans la résolution.



***Critères de succès :***    

1\. Le script d'installation installe avec succès tous les composants requis.    

2\. Le mode d'installation express fournit une configuration automatisée.    

3\. Le mode d'installation avancé permet la personnalisation par l'utilisateur.    

4\. Le script de démarrage coordonne la séquence de démarrage correcte de tous les services.    

5\. Le script de vérification identifie correctement les problèmes système.    

6\. Les règles udev reconnaissent correctement les écrans tactiles.    

7\. Tous les scripts gèrent les conditions d'erreur avec élégance.    

8\. Le mode de dépannage interactif aide à résoudre les échecs de détection du matériel.    

9\. Les scripts s'exécutent efficacement sans utilisation excessive des ressources.    

10\. Les scripts fournissent un retour et une journalisation clairs.    

11\. La documentation est fournie en français et en anglais. 

***Plan de vérification*** :    

1\. Tester le script d'installation sur un système Arch Linux frais en modes express et avancé.    

2\. Vérifier que le script de démarrage démarre correctement tous les composants dans le bon ordre.    

3\. Tester le script de vérification avec diverses conditions d'erreur simulées.    

4\. Tester les règles udev avec différents matériels d'écran tactile.    

5\. Vérifier que la sortie du journal est claire et utile pour le débogage.    

6\. Tester la récupération après des conditions d'erreur courantes.    

7\. Vérifier que les scripts fonctionnent après les redémarrages du système.    

8\. Tester le mode de dépannage interactif avec des pannes matérielles simulées.    

9\. Vérifier que la documentation française et anglaise est exacte et complète.  

***Dépendances :***  

\*Développer l'API backend pour la communication avec Lyrion et Squeezelite  

\*Configurer le serveur web lighttpd pour héberger l'interface MAQAM Player  

\*Configurer le gestionnaire de fenêtres i3 en mode kiosque pour l'interface MAQAM Player 

\*Implémenter la prise en charge de l'écran tactile et les règles udev pour les appareils tactiles  

**Tâche 15-Créer le package de déploiement et la documentation pour le MAQAM Player (2 dépendances)**
**


***Description :***  

Préparer le package de déploiement final et la documentation complète pour le MAQAM 

Player. Cela comprend la création de guides d'installation, de manuels d'utilisation et de documentation technique pour prendre en charge le déploiement, l'utilisation et la maintenance du système. Toute la documentation sera disponible en français et en anglais pour une accessibilité plus large. La documentation se concentrera uniquement sur les supports écrits sans tutoriels vidéo.  

***Critères de succès :***    

1\. Package d'installation complet avec tous les composants requis.    

2\. Guide d'installation clair et complet en français et en anglais.    

3\. Manuel d'utilisation avec des instructions pour toutes les fonctionnalités dans les deux langues.    

4\. Documentation technique pour la maintenance du système dans les deux langues.    

5\. Guide de dépannage pour les problèmes courants.    

6\. Documentation de l'API pour les extensions futures.    

7\. Documentation du code source pour les développeurs.    

8\. Le processus de déploiement est testé et vérifié.    

9\. Toute la documentation prend en charge le système de mise à jour automatique avec notifications utilisateur.  

***Plan de vérification :***    

1\. Effectuer une installation de test en utilisant uniquement le package d'installation et la documentation.    

2\. Faire examiner le manuel d'utilisation par un utilisateur non technique pour en vérifier la clarté dans les deux langues.    

3\. Faire examiner la documentation technique par un utilisateur technique.    

4\. Vérifier que tous les documents sont complets et exacts.    

5\. Tester le guide de dépannage par rapport à des problèmes simulés.    

6\. S'assurer que toute la documentation est disponible aux formats PDF et HTML.    

7\. Vérifier la documentation de l'API avec des appels API de test.    

8\. Vérifier que la documentation décrit correctement le mécanisme de mise à jour.  

***Dépendances :***  

\*Implémenter des tests complets et une assurance qualité pour le MAQAM Player 

\*Développer des scripts système pour l'installation, le démarrage et la vérification 
