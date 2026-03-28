# Progression du groupe — PolyChat
> Projet INFO834 — Mini-projet NoSQL (MongoDB + Redis)
> Dernière mise à jour : 28/03/2026

---

## Équipe
| Membre | GitHub |
|---|---|
| Anas mohamed Draoui | `anas`, `Monarch7-NS`|
| Houssam Eddine Syouti | `Houssam365` |
| Stevens | `stevens237-hub` |


---

## Historique des séances

### Séance 1 — 16/03/2026
**Auteur :** Monarch7-NS-anas

- Premier commit du projet (`bbdf972`)
- Mise en place de la structure de base du dépôt Git

---

### Séance 2 — 24/03/2026
**Auteurs :** Houssam365, stevens237-hub

| Membre | Travail effectué |
|---|---|
| **Houssam** | Ajout de la structure des répertoires (`557f410`), configuration complète de l'architecture PolyChat (`6ba7a9b`), merge et gestion des conflits (`e366f41`) |
| **Stevens** | Mise à jour du README (plan du projet, fonctionnalités), correction du formatage, ajout des noms des membres de l'équipe |

**Résultat :** Structure du projet posée, Docker Compose initial, README documenté.

---

### Séance 3 — 27/03/2026 (journée principale — Anas)

> Cette séance représente la journée de travail la plus dense du projet. Le travail d'Anas est détaillé ci-dessous.

---

## Travail d'Anas — 27/03/2026

### 1. Migration Flask → FastAPI (`commit 2349ae2` — 14h02)

Le backend existant était basé sur **Flask**. Anas a effectué une migration complète vers **FastAPI**.

**Fichiers modifiés :**
- `backend/app.py` — réécriture complète (Flask → FastAPI, Pydantic models, async lifespan)
- `backend/requirements.txt` — remplacement des dépendances Flask par FastAPI + uvicorn + pydantic
- `backend/Dockerfile` — changement de la commande de lancement :
  ```dockerfile
  # Avant (Flask)
  CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

  # Après (FastAPI)
  CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
  ```
- `docker-compose.yml` — reconfiguration complète des services
- `frontend/Dockerfile` — mise à jour

**Pourquoi FastAPI plutôt que Flask ?**

| Critère | Flask | FastAPI |
|---|---|---|
| Validation des données | manuelle | automatique via Pydantic |
| Support async/await | limité | natif |
| WebSocket | extension externe | intégré |
| Documentation API | non incluse | Swagger auto-généré (`/docs`) |
| Performance | moyenne | haute (Starlette + uvicorn) |

---

### 2. Initialisation MongoDB + Docker Compose (`commit 85c64b2` — 15h18)

**Création de `database/init-mongo.sh` :**

Script bash qui s'exécute automatiquement au démarrage via un conteneur `mongo-init` dédié. Il :
1. Attend que `mongo1` soit prêt
2. Initialise le ReplicaSet `rs0` avec 3 nœuds (`mongo1:27017`, `mongo2:27017`, `mongo3:27017`)
3. Attend l'élection du Primary
4. Crée les collections et indexes sur la base `polychat` :

| Collection | Index créé | Raison |
|---|---|---|
| `users` | `username` unique | éviter les doublons |
| `messages` | `(from, to, timestamp)` + `timestamp DESC` | requêtes de conversation efficaces |
| `conversations` | `participants` unique + `updated_at DESC` | liste des conversations triée par récence |

**Mise à jour du `docker-compose.yml` :**
- Ajout du service `mongo-init` avec `restart: "no"` (s'exécute une seule fois)
- `mongo-init` attend la healthcheck de `mongo1`, `mongo2`, `mongo3` avant de démarrer
- Ajout de Redis (`redis:7`) pour la gestion des sessions et utilisateurs en ligne

---

### 3. Résolution de conflits Git

Lors du merge de la branche `anas` avec `origin/main`, un conflit est survenu dans `backend/Dockerfile` sur la commande CMD :

```
<<<<<<< HEAD (anas)
CMD ["python", "-m", "uvicorn", "app:app", ...]
=======
CMD ["python", "-m", "uvicorn", "src/server.py:app", ...]
>>>>>>> origin/main
```

**Résolution :** La version `app:app` a été conservée car le fichier `app.py` se trouve à la racine du backend (il n'y a pas de `src/server.py`). Merge finalisé avec succès (`commit c7ee760`).

---

### 4. Refactorisation du backend en architecture FastAPI modulaire (`commit 35481ae` — 16h21)

Le backend `app.py` (~250 lignes) a été découpé en plusieurs fichiers suivant la **convention officielle FastAPI** pour les applications de taille moyenne ("Bigger Applications").

**Avant :**
```
backend/
└── app.py   ← tout dans un seul fichier
```

**Après :**
```
backend/
└── app/
    ├── __init__.py
    ├── main.py          ← instance FastAPI, lifespan, inclusion des routers
    ├── config.py        ← variables d'environnement (MONGO_URI, REDIS_HOST, etc.)
    ├── database.py      ← connexions MongoDB et Redis (get_db / get_redis)
    ├── models.py        ← modèles Pydantic (UsernameBody, MessageBody)
    ├── ws_manager.py    ← gestionnaire WebSocket + Redis pub/sub
    └── routers/
        ├── __init__.py
        ├── users.py         ← POST /api/users/login|logout, GET /api/users/online
        ├── messages.py      ← POST /api/messages/send, GET /api/messages/conversation|search
        ├── conversations.py ← GET /api/conversations/{username}, PUT /api/conversations/read
        ├── stats.py         ← GET /api/stats/top-sender|top-receiver
        └── ws.py            ← WebSocket /ws/{username}
```

**Principe :** chaque router possède un préfixe et un domaine métier clair. `main.py` ne fait qu'assembler les pièces via `app.include_router(...)`.

---

### 5. Nouvelles fonctionnalités backend ajoutées

#### WebSocket temps réel (`ws_manager.py` + `routers/ws.py`)

Remplacement du système de polling (requêtes HTTP toutes les 5 secondes) par une connexion **WebSocket persistante**.

**Fonctionnement :**
1. À la connexion, l'utilisateur s'abonne à son canal Redis : `chat:{username}`
2. Quand un message est envoyé via `POST /api/messages/send`, le backend publie dans `chat:{to_user}`
3. Le WebSocket écoute le canal Redis et transmet le message au client instantanément
4. Les indicateurs de frappe (`typing` / `stop_typing`) transitent aussi par le WebSocket → Redis pub/sub

```
[Client A] --POST /api/messages/send--> [Backend]
                                              |
                                     redis.publish("chat:B", msg)
                                              |
                              [Redis] --------+
                                              |
                              [WS Manager B] ← pubsub.listen()
                                              |
                                       [Client B] ← websocket.send(msg)
```

**Avantage :** latence quasi nulle, pas de charge réseau inutile.

#### Conversations avec compteur de messages non lus (`routers/conversations.py`)

- `GET /api/conversations/{username}` : retourne toutes les conversations de l'utilisateur triées par date, avec le dernier message et le nombre de messages non lus
- `PUT /api/conversations/read?from_user=X&to_user=Y` : marque les messages comme lus dans MongoDB

#### Recherche de messages (`routers/messages.py`)

- `GET /api/messages/search?username=X&query=Y` : recherche dans tous les messages de l'utilisateur via regex MongoDB (insensible à la casse, limite 50 résultats)

---

### 6. Refonte complète du frontend React

**Avant :** un seul `App.js` (~170 lignes), interface basique.

**Après :** architecture en composants, dark theme moderne.

**Nouveaux fichiers :**

| Fichier | Rôle |
|---|---|
| `components/Avatar.js` | Bulle colorée avec initiale du pseudo (couleur dérivée du nom) |
| `components/Login.js` | Page de connexion (carte centrée, dark) |
| `components/Sidebar.js` | Barre latérale : liste des conversations, badges non lus, points de présence, recherche |
| `components/ChatPanel.js` | Zone de chat : bulles de messages, séparateurs de date, indicateur de frappe animé, formulaire d'envoi |

**`App.js` réécrit :**
- Connexion WebSocket établie à la connexion, fermée à la déconnexion
- Mise à jour optimiste des messages (affichage immédiat sans attendre la réponse serveur)
- Gestion des indicateurs de frappe via timeout de 2 secondes
- Liste des utilisateurs en ligne rafraîchie toutes les 10 secondes (au lieu de 5s)

**Design (`App.css`) :**
- Thème sombre : `#13131f` (fond chat), `#1a1a2e` (sidebar/header), `#1e1e2e` (login)
- Bulles envoyées : dégradé violet `#6366f1 → #8b5cf6`
- Bulles reçues : gris foncé `#252535`
- Animation typing dots (3 points qui rebondissent)

---

## Récapitulatif des commits du 27/03/2026

| Heure | Commit | Auteur | Description |
|---|---|---|---|
| 14h02 | `2349ae2` | **Anas** | Migration Flask → FastAPI, Dockerfile, requirements |
| 15h18 | `85c64b2` | **Anas** | Script init MongoDB, docker-compose avec Redis + mongo-init |
| ~15h30 | `79666a7` | Houssam | Modification backend (sa version) |
| ~15h45 | `c7ee760` | **Anas** | Merge réussi, résolution du conflit Dockerfile |
| ~16h00 | `68036b1` | **Anas** | Adaptation du docker-compose de Houssam |
| 16h21 | `35481ae` | **Anas** | Refactorisation architecture FastAPI + WebSocket + frontend redesign |
| 17h11 | `869220d` | Stevens | Implémentation fonctionnalités Redis (`redis.py`) |

---

## État du projet au 28/03/2026

### Routes API disponibles

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/users/login` | Connexion / création utilisateur |
| `POST` | `/api/users/logout` | Déconnexion |
| `GET` | `/api/users/online` | Liste des utilisateurs en ligne (Redis) |
| `POST` | `/api/messages/send` | Envoi d'un message (MongoDB + Redis pub/sub) |
| `GET` | `/api/messages/conversation` | Historique entre deux utilisateurs |
| `GET` | `/api/messages/search` | Recherche de messages par mot-clé |
| `GET` | `/api/conversations/{username}` | Liste des conversations avec compteurs non lus |
| `PUT` | `/api/conversations/read` | Marquer messages comme lus |
| `GET` | `/api/stats/top-sender` | Utilisateur qui envoie le plus |
| `GET` | `/api/stats/top-receiver` | Utilisateur qui reçoit le plus |
| `GET` | `/api/health` | Santé du service (MongoDB + Redis) |
| `WS` | `/ws/{username}` | WebSocket temps réel |

### Infrastructure Docker

```
docker-compose up --build
       │
       ├── mongo1 (27017)  ─┐
       ├── mongo2           ├── ReplicaSet rs0
       ├── mongo3          ─┘
       │
       ├── mongo-init  ←── exécute database/init-mongo.sh
       │
       ├── redis (6379)
       │
       ├── backend (5000) ←── FastAPI + uvicorn
       │
       └── frontend (3000) ←── React
```

### Fonctionnalités implémentées

- [x] Connexion / déconnexion avec pseudo
- [x] Liste des utilisateurs en ligne (Redis)
- [x] Envoi et réception de messages (MongoDB)
- [x] Historique des conversations
- [x] Messagerie temps réel (WebSocket + Redis pub/sub)
- [x] Indicateur de frappe animé
- [x] Compteur de messages non lus par conversation
- [x] Marquage automatique comme lu à l'ouverture
- [x] Recherche de messages (regex MongoDB)
- [x] Stats (top sender / top receiver)
- [x] ReplicaSet MongoDB 3 nœuds
- [x] Interface dark theme avec composants React
- [ ] Authentification sécurisée (hors scope)
- [ ] Groupes / salons (hors scope)
