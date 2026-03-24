# Plan de travail — Mini-projet Tchat NoSQL (INFO834)

---

## 1. Contexte et objectif

### Fonctionnalités premières

- Afficher les utilisateurs connectés (via Redis)
- Stocker tous les messages dans MongoDB
- Mettre en place un ReplicaSet MongoDB à 3 nœuds
- Afficher l'historique d'une conversation entre deux utilisateurs

### Fonctionnalités supplémentaires

- Statistiques : utilisateur qui envoie le plus de messages
- Statistiques : utilisateur le plus sollicité (le plus de messages reçus)
- Messages non lus
- Recherche dans l'historique par mot-clé (index texte MongoDB)
- Historique des connexions/déconnexions avec horodatage

---

## 2. Décisions prises

### Technologies utilisées

- **Frontend :** ReactJS
- **Backend :** Flask

### Schéma des collections

**users**

```json
{
  "_id"        : "ObjectId (auto)",
  "username"   : "string — unique",
  "created_at" : "datetime"
}
```

**messages**

```json
{
  "_id"       : "ObjectId (auto)",
  "from"      : "string — username expéditeur",
  "to"        : "string — username destinataire",
  "content"   : "string",
  "timestamp" : "datetime",
  "read"      : "bool — false par défaut"
}
```

**conversations**

```json
{
  "_id"          : "ObjectId (auto)",
  "participants" : ["string", "string"],
  "last_message" : "string",
  "updated_at"   : "datetime"
}
```

---

## 3. Infrastructure Docker et ReplicaSet

### Tâches

- Écrire le `docker-compose.yml` complet
- Écrire les `Dockerfile` pour le backend et le frontend
- Lancer `docker compose up` et vérifier avec `rs.status()`
- Vérifier les 3 nœuds
- **Test de bascule** : `docker stop mongo1` → vérifier qu'un SECONDARY devient PRIMARY automatiquement
- Committer le `docker-compose.yml` sur `main` pour que toute l'équipe puisse l'utiliser

---

## 4. Développement

### Backend : serveur et gestion des messages

- Mettre en place le serveur (Flask)
- Connexion au ReplicaSet MongoDB
- Événement / route : connexion utilisateur → enregistrement MongoDB + Redis
- Événement / route : envoi d'un message → insertion dans `messages`
- Route : récupérer l'historique d'une conversation entre deux utilisateurs
- Route : déconnexion utilisateur → retrait de Redis
- Tester avec Postman ou `curl` sans le frontend

### Redis & requêtes avancées MongoDB

- Implémenter `online:users` (SET Redis) : `SADD` à la connexion, `SREM` à la déconnexion
- Implémenter `session:{username}` (HASH Redis) avec TTL de 30 min
- Route : retourner la liste des utilisateurs connectés
- Requête MongoDB : utilisateur qui envoie le plus de messages
- Requête MongoDB : utilisateur le plus sollicité (le plus de messages reçus)
- Requête MongoDB : messages non lus pour un utilisateur donné

### Frontend & interface client

- Écran de connexion : champ username, bouton rejoindre
- Liste des utilisateurs connectés (mise à jour en temps réel)
- Fenêtre de conversation : affichage des messages, champ d'envoi
- Historique : afficher les messages précédents au chargement d'une conversation
- Utiliser des données mockées tant que le backend n'est pas disponible
- Commencer à prendre des captures d'écran pour le rapport

---

## 5. Intégration et tests

### Tâches

- Merger toutes les branches sur `main` — résoudre les conflits ensemble
- Tester `docker compose up` depuis zéro sur la machine de chaque membre
- Vérifier le flux complet : frontend → backend → MongoDB → Redis

---

## 6. Structure du dépôt git

```
PolyChat/
├── docker-compose.yml       ← toute l'infra en un fichier
├── schema.md                ← schéma des collections
├── protocol.md              ← format des messages frontend ↔ backend
├── README.md                ← instructions pour lancer le projet
├── .gitignore
│
├── frontend/                ← React
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    └── src/
        ├── server.py        ← point d'entrée serveur
        ├── mongo.py         ← connexion et requêtes MongoDB
        └── redis.py         ← connexion et opérations Redis
```
