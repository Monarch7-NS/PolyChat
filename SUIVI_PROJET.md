# Suivi du Projet PolyChat

Ce document suit l'avancement du projet PolyChat (INFO834 - Mini-projet BD NoSQL MongoDB, Redis) pour tous les membres de l'équipe. Il est mis à jour après chaque séance avec les contributions individuelles et collectives.

## Équipe
- SYOUTI HOUSSAM EDDINE
- Steve MBODA NGUENANG
- Islam HACHIMI
-

## Sessions

### Séance du 27/03/2026 (13:15 - 17:15)
**Objectifs de la séance :** Mise en place de l'architecture de base

**Contributions :**
- **SYOUTI HOUSSAM EDDINE :**
  - Gestion des conflits : Résolution des conflits de merge et mise en place de stratégies de gestion des branches
  - Réalisation des fichiers Docker Compose : Configuration du ReplicaSet MongoDB (3 nœuds), Redis, et services backend/frontend
  - Schéma de modèle des données : Définition des collections MongoDB (messages, conversations, users) et structures Redis (sessions, utilisateurs en ligne)
  - Connexion entre MongoDB et la base de données : Implémentation de la connexion PyMongo avec support ReplicaSet, gestion des erreurs de connexion, et intégration dans FastAPI
 
- **Steve MBODA :**
  - Réalisation des fichiers Docker Compose : Configuration du ReplicaSet MongoDB (3 nœuds), Redis, et services backend/frontend
  - Tests de fonctionnement de nos replicatsets (tests de la réplication des données, tests de la tolérance aux pannes: le replicaset élit automatiquement un nouveau PRIMARY, test de resynchronisation).
  - Tests de nos routes API
  - Connexion à Redis, gestion des utilisateurs connectés, des sessions utilisateurs
  

**Avancement global :**
- ✅ Architecture Docker mise en place
- ✅ Connexions DB établies
- ✅ Modèles de données définis
- 🔄 Routes API à implémenter



---

### Séance du 01/04/2026 (08:00 - 18:00)
**Objectifs de la séance :** Complétion de la partie Redis, correction du bug de démarrage du backend, tests de l'application

**Contributions :**
- **Steve MBODA :**
  - Complétion du fichier `redis_utils.py` : ajout des fonctions d'historique des connexions (`log_login`, `log_logout`, `get_connection_history`, `get_global_connection_log`, `get_last_seen`) avec les structures de données Redis adaptées (LIST avec `LPUSH`/`LTRIM`, HASH `last_seen`)
  - Intégration de l'historique dans `routers/users.py` : appel de `_log_event()` à chaque login et logout pour alimenter les clés Redis `connection_history:<user>` et `global:connection_log`
  - Ajout de 3 nouvelles routes API : `GET /api/users/{username}/history`, `GET /api/users/{username}/last-seen`, `GET /api/users/connection-log`
  - Tests complets de l'application : vérification du backend (`/api/health`), tests Redis via `redis-cli` (`SMEMBERS`, `LRANGE`, `HGETALL`, `PUBSUB`), tests MongoDB (`countDocuments`, `find`, `aggregate`, `getIndexes`), tests ReplicaSet (`rs.status()`, `rs.isMaster()`, tolérance aux pannes par arrêt du PRIMARY)

- **Islam HACHIMI :**
  - Débogage et résolution de l'erreur OCI runtime/mount Docker : correction du conflit de montage pour le script `init-mongo.sh`
  - Optimisation du `docker-compose.yml` : modification des points de montage et de l'entrypoint pour une structure plus robuste
  - Monitoring et validation du bon démarrage de l'ensemble des services (ReplicaSet MongoDB, Redis, API Backend, Frontend)


**Avancement global :**
- ✅ Historique des connexions Redis implémenté et exposé via API
- ✅ Toutes les exigences Redis du sujet couvertes (présence en ligne, sessions, historique, pub/sub)
- ✅ ReplicaSet MongoDB testé (failover, resynchronisation)
- ✅ Tests des routes API validés



---

### Séance du 15/04/2026
**Objectifs de la séance :** Professionnalisation de l'application — authentification, rôles, dashboard admin, persistance des données

**Contributions :**
- **Steve MBODA :** (travail sur une nouvelle brance feat/auth-and-admin avant de merge avec le main)
  - **Authentification sécurisée :** Implémentation de l'inscription et de la connexion avec hachage de mot de passe 
  - **Sécurisation des routes API :** Toutes les routes (`/messages`, `/conversations`, `/users`, `/stats`, WebSocket) protégées par token JWT. Vérification que l'utilisateur ne peut accéder qu'à ses propres données (sauf admin)
  - **Dashboard Admin :** Création du dashboard avec 4 onglets : Vue générale (stats globales), Utilisateurs (tableau avec messages envoyés/reçus), Activité (graphique en barres par jour), Connexions (historique Redis). Accès réservé au rôle admin
  - **Page de connexion repensée :** Refonte de `Login.js` avec deux onglets (Connexion / Inscription), validation des champs, affichage des erreurs, hint des identifiants de démo
  - **Persistance Redis :** Activation de l'AOF (`--appendonly yes --appendfsync everysec`) avec volume Docker nommé `redis_data` pour conserver l'historique des connexions entre redémarrages
  - **Export / Import de la base MongoDB :** Ajout des commandes `db-export` et `db-import` dans le Makefile pour partager les données entre membres de l'équipe
  - **Seed amélioré :** `seed.py` crée/met à jour l'utilisateur admin indépendamment de l'état de la base, et migre les anciens comptes sans mot de passe

**Avancement global :**
- ✅ Authentification complète (inscription, connexion, JWT, rôles)
- ✅ Dashboard admin avec statistiques persistantes
- ✅ Toutes les routes API sécurisées
- ✅ Persistance Redis entre redémarrages
- ✅ Export/Import MongoDB pour partage entre membres
- ✅ Import automatique de la base au démarrage du projet
- ✅ ReplicaSet : démarrage fiable avec attente du PRIMARY avant import

---

### Séance du [JJ/MM/AAAA] ([HH:MM] - [HH:MM])
**Objectifs de la séance :**




