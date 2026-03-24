# PolyChat - Guide de démarrage rapide

Ce repository contient une application de messagerie instantanée complète avec un frontend React, un backend Flask, et une base de données MongoDB avec ReplicaSet.

## 📋 Architecture du projet

```
PolyChat/
├── frontend/          # Application React
├── backend/           # API Flask
├── database/          # Configuration MongoDB
├── docker-compose.yml # Orchestration Docker
├── SETUP.md          # Guide de démarrage
├── GIT_GUIDE.md      # Guide Git et collaboration
├── Makefile          # Commandes raccourcis
└── README.md         # Documentation détaillée
```

## 🚀 Démarrage rapide avec Docker

### Prérequis

- Docker et Docker Compose installés

### Lancement

```bash
# Cloner le repository
git clone <url>
cd PolyChat

# Lancer toute l'infrastructure
docker compose up -d

# Vérifier que tous les services sont actifs
docker compose ps
```

Les services seront disponibles à :
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:5000
- **MongoDB** :
  - mongo1 : localhost:27017
  - mongo2 : localhost:27018
  - mongo3 : localhost:27019
- **Redis** : localhost:6379

### Vérification du ReplicaSet MongoDB

```bash
# Accéder au shell MongoDB
docker exec -it mongo1 mongosh -u admin -p password --authenticationDatabase admin

# Vérifier le statut du ReplicaSet
rs.status()

# Voir la configuration
rs.conf()
```

### Arrêt

```bash
docker compose down
```

---

## 💻 Développement local (sans Docker)

### Frontend React

```bash
cd frontend
npm install
npm start
```

L'app sera sur http://localhost:3000

**Configuration** : Modifiez `frontend/src/App.js` pour pointer vers votre API backend

### Backend Flask

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Le serveur sera sur http://localhost:5000

**Configuration** : Modifiez `backend/.env` avec vos credentials MongoDB et Redis

### Base de données

Assurez-vous que MongoDB et Redis sont en cours d'exécution localement, ou lancez-les via Docker :

```bash
docker compose up mongo1 mongo2 mongo3 redis
```

---

## 📚 Documentation

- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)

---

## 🏗️ Fonctionnalités implémentées

### Phase 1 (MVP)
- ✅ Afficher les utilisateurs connectés (Redis)
- ✅ Stocker tous les messages (MongoDB)
- ✅ ReplicaSet MongoDB à 3 nœuds
- ✅ Historique de conversation

### Phase 2 (Avancé)
- ✅ Statistiques : utilisateur avec le plus de messages envoyés
- ✅ Statistiques : utilisateur le plus sollicité
- Routes pour messages non lus (implémentables)
- Recherche par mot-clé (implémentable avec index texte)
- Historique connexions/déconnexions (implémentable)

---

## 🔧 Commandes utiles

### Docker

```bash
# Voir les logs
docker compose logs -f [service]

# Redémarrer un service
docker compose restart [service]

# Reconstruire les images
docker compose build

# Nettoyer les volumes
docker compose down -v
```

### MongoDB

```bash
# Accéder au shell
docker exec -it mongo1 mongosh -u admin -p password --authenticationDatabase admin

# Voir les bases de données
show dbs

# Sélectionner une base
use polychat

# Voir les collections
show collections

# Voir les documents
db.messages.find().pretty()
db.users.find().pretty()
db.conversations.find().pretty()
```

### Redis

```bash
# Accéder au CLI Redis
docker exec -it redis redis-cli

# Voir les utilisateurs en ligne
SMEMBERS online:users

# Voir une session
HGETALL session:username
```

---

## 🛠️ Dépannage

### MongoDB ne démarre pas
- Vérifier les logs : `docker compose logs mongo1`
- Vérifier l'espace disque
- Supprimer les volumes : `docker compose down -v`

### Frontend ne se connecte pas au backend
- Vérifier que le backend est accessible : `curl http://localhost:5000/api/health`
- Vérifier la variable d'environnement `REACT_APP_API_URL`
- Vérifier le CORS dans `backend/app.py`

### Erreurs MongoDB ReplicaSet
- Attendre quelques secondes après le démarrage
- Vérifier avec `rs.status()` que les 3 nœuds sont en bon état
- Relancer le conteneur mongo-init si nécessaire

---

## 📝 Notes pour l'équipe

- Tous les services sont configurés pour fonctionner en développement
- Les données MongoDB et Redis sont persistées dans des volumes Docker
- Les fichiers sont montés en volumes pour un développement chaud (hot reload)
- Lire les READMEs individuels pour plus de détails sur chaque service

---

## 👥 Collaboration et Git

### Synchroniser votre travail avec l'équipe

```bash
# Pull sécurisé (préserve votre travail local)
make git-pull
# ou
bash do-pull.sh

# Push de vos changements
make git-push

# Voir l'historique
git log --oneline
```

**⚠️ Toujours faire un pull avant de commencer à travailler!**

Pour des détails sur la gestion des conflits et les bonnes pratiques Git, consultez [GIT_GUIDE.md](./GIT_GUIDE.md).

---

## 🛠️ Commandes pratiques

### Avec Make (recommandé)

```bash
make help          # Voir toutes les commandes
make install       # Installer les dépendances
make docker-up     # Démarrer l'infrastructure
make docker-down   # Arrêter l'infrastructure
make logs          # Voir les logs
make git-pull      # Pull sécurisé
make git-push      # Push des changements
```

### Git

```bash
git status                    # Voir l'état
git add .                     # Ajouter les changements
git commit -m "Description"   # Valider
git push origin main          # Pousser
```

---

## 👥 Contribution

1. Tirez les derniers changements : `make git-pull`
2. Créez une branche si nécessaire : `git checkout -b ma-feature`
3. Committez régulièrement : `git commit -m "..."`
4. Poussez votre branche : `git push origin ma-feature` (ou `make git-push`)
5. Signalez à votre équipe les modifications

---

**Bonne développement ! 🎉**

Pour plus d'aide, voir [GIT_GUIDE.md](./GIT_GUIDE.md) et les READMEs des services.

