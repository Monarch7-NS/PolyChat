
# PolyChat — Intégration Redis
### Document récapitulatif — Rôle, implémentation et plus-value de Redis
**MBODA NGUENANG Steve — Intégration Redis & Cache**

---

## 1. Pourquoi Redis dans PolyChat ?

PolyChat est une application de messagerie temps réel. MongoDB assure la persistance des données (messages, utilisateurs, conversations). Redis complète cette architecture en prenant en charge tout ce qui est **éphémère, fréquent et temps réel**.

Redis joue deux rôles complémentaires dans l'application :

- **Rôle 1 — Performance :** Délester MongoDB des opérations fréquentes et légères (présence en ligne, sessions)
- **Rôle 2 — Temps réel :** Rendre possible la messagerie instantanée via le mécanisme Pub/Sub

> **MongoDB = mémoire longue** (tout ce qui doit être conservé durablement)
> **Redis = système nerveux** (tout ce qui doit réagir vite et maintenant)

---

## 2. Configuration et connexion

Redis est déployé via Docker Compose avec la **persistance AOF activée**, ce qui garantit que les données survivent aux redémarrages du conteneur.

```yaml
# docker-compose.yml
redis:
  image: redis:7
  command: redis-server --appendonly yes --appendfsync everysec
  volumes:
    - redis_data:/data
```

Deux types de clients Redis sont utilisés côté backend (`database.py`) :

- **`redis.Redis`** — client synchrone pour les routes HTTP classiques (login, logout, stats)
- **`redis.asyncio`** — client asynchrone pour les WebSockets (Pub/Sub temps réel)

---

## 3. Les structures Redis implémentées

### 3.1 Présence en ligne — SET `online:users`

**Fichier :** `backend/app/routers/users.py`

```python
# Connexion
redis_client.sadd("online:users", username)

# Déconnexion
redis_client.srem("online:users", username)

# Lecture — appelée toutes les 10 secondes par le frontend
users = redis_client.smembers("online:users")
```

**Fonctionnement dans l'application :**
1. À la connexion, l'utilisateur est ajouté au SET avec `SADD`
2. À la déconnexion, il est retiré avec `SREM`
3. Le frontend appelle `GET /api/users/online` toutes les **10 secondes**
4. React met à jour les pastilles vertes dans la sidebar

**Pourquoi le SET :**
- Propriété fondamentale : **pas de doublons** — si un utilisateur ouvre deux onglets, son nom n'apparaît qu'une seule fois
- `SADD` et `SREM` sont atomiques — aucun risque de race condition
- `SMEMBERS` retourne tous les membres en O(N), ultra-rapide en mémoire

---

### 3.2 Sessions utilisateurs — HASH avec TTL `session:{username}`

**Fichier :** `backend/app/routers/users.py`

```python
# Création de la session à la connexion
redis_client.hset(f"session:{username}", mapping={
    "username": username,
    "logged_in_at": now
})
redis_client.expire(f"session:{username}", 1800)  # 30 minutes

# Suppression à la déconnexion
redis_client.delete(f"session:{username}")

# Dernière activité
redis_client.hset(f"last_seen:{username}", f"last_{event}", now)
```

**Fonctionnement dans l'application :**
1. À la connexion, un hash est créé avec le nom d'utilisateur et l'heure de connexion
2. Redis supprime automatiquement la clé après **30 minutes d'inactivité** (`EXPIRE`)
3. `last_seen:{username}` enregistre la date du dernier login et du dernier logout
4. Consultable via `GET /api/users/{username}/last-seen`

**Pourquoi le HASH avec TTL :**
- Plusieurs champs d'un même objet regroupés sous une seule clé — lecture efficace
- L'expiration automatique évite d'écrire du code de nettoyage — Redis gère seul
- Simule une vraie gestion de session sans surcharger MongoDB

---

### 3.3 Historique des connexions — LIST bornée

**Fichier :** `backend/app/routers/users.py` — fonction `_log_event()`

```python
def _log_event(rc, username, event):
    payload = json.dumps({"username": username, "event": event, "timestamp": now})

    # Historique personnel — 100 événements max
    rc.lpush(f"connection_history:{username}", payload)
    rc.ltrim(f"connection_history:{username}", 0, 99)

    # Journal global — 500 événements max
    rc.lpush("global:connection_log", payload)
    rc.ltrim("global:connection_log", 0, 499)
```

**Fonctionnement dans l'application :**
1. À chaque login et logout, `_log_event()` est appelée automatiquement
2. `LPUSH` insère en tête — les événements les plus récents sont toujours en premier
3. `LTRIM` coupe la queue automatiquement quand la limite est dépassée
4. `GET /api/users/connection-log` fait un `LRANGE global:connection_log 0 49`
5. Le résultat est affiché dans la modal **"Historique des Connexions"** du dashboard

**Pourquoi la LIST :**
- File d'attente bornée — `LPUSH` + `LTRIM` en deux commandes, Redis gère la suppression
- Pas besoin de vérifier la taille ni de supprimer manuellement les anciens événements
- `LRANGE` permet une pagination efficace (10 derniers, 50 derniers, etc.)

---

## 4. Messagerie temps réel — Pub/Sub

**Fichiers :** `backend/app/ws_manager.py` et `backend/app/routers/messages.py`

```python
# ws_manager.py — abonnement au canal à la connexion WebSocket
pubsub = r.pubsub()
await pubsub.subscribe(f"chat:{username}")

# Écoute continue des messages Redis
async for message in pubsub.listen():
    await websocket.send_text(message["data"])

# messages.py — publication à l'envoi d'un message
redis_client.publish(f"chat:{to_user}", payload)

# Indicateurs de frappe
await r.publish(f"chat:{to_user}", json.dumps({"type": "typing", "from": username}))
```

**Flux complet d'un message :**

```
Steve envoie "Bonjour" à Anas
        ↓
1. FastAPI sauvegarde dans MongoDB          (persistance)
        ↓
2. FastAPI publie sur "chat:Anas"           (Redis Pub/Sub)
        ↓
3. ws_manager écoute le canal et reçoit    (abonné)
        ↓
4. ws_manager envoie au WebSocket d'Anas   (push)
        ↓
5. Message apparaît chez Anas instantanément ✅
```

**Les indicateurs de frappe suivent le même flux :**
1. Steve tape → frontend envoie `{"type": "typing", "to": "Anas"}` via WebSocket
2. `ws_manager` publie sur `"chat:Anas"`
3. Anas reçoit l'événement → *"Steve est en train d'écrire..."* s'affiche pendant 3 secondes

**Pourquoi Pub/Sub :**
- **Sans Pub/Sub :** polling — chaque client demande "ai-je des messages ?" toutes les secondes → lent, coûteux, non scalable
- **Avec Pub/Sub :** livraison **push** — Redis notifie instantanément tous les abonnés d'un canal dès qu'un message est publié
- Un canal par utilisateur (`"chat:Anas"`) — isolation parfaite, chaque utilisateur ne reçoit que ses messages

---

## 5. Redis et le dashboard analytique

Dans le dashboard admin, les données proviennent de deux sources :

| Donnée affichée | Source |
|---|---|
| Historique des connexions | **Redis** — `LRANGE global:connection_log` |
| Pastilles vertes (en ligne) | **Redis** — `SMEMBERS online:users` |
| Top expéditeur / destinataire | MongoDB — agrégation `$group + $sort` |
| Activité journalière (messages/jour) | MongoDB — agrégation `$dateToString` |

### Pourquoi ne pas avoir mis les stats de messages dans Redis ?

Redis dispose des **Sorted Sets (ZSET)** parfaits pour des classements en temps réel. On aurait pu faire :

```python
# À chaque message envoyé
ZINCRBY leaderboard:senders 1 "Steve"
ZINCRBY leaderboard:receivers 1 "Anas"

# Lecture du top
ZREVRANGE leaderboard:senders 0 9 WITHSCORES
# → [("Steve", 412), ("Alice", 298), ...]
```

Ce choix aurait été pertinent si :
- Il y avait des **milliers de messages par seconde** (agrégations MongoDB trop lentes)
- Le leaderboard devait se **mettre à jour en direct** sous les yeux des utilisateurs
- La collection contenait des **millions de documents**

À l'échelle de ce projet, les agrégations MongoDB sont suffisamment performantes. La décision a été d'utiliser Redis uniquement là où il est **indispensable** : le temps réel et les données éphémères. C'est un **choix technique justifié**, pas une limitation.

---

## 6. Plus-value globale de Redis dans PolyChat

### Comparatif Sans Redis vs Avec Redis

| Sans Redis | Avec Redis |
|---|---|
| Polling toutes les X secondes pour savoir qui est en ligne | SET mis à jour en temps réel à chaque connexion/déconnexion |
| Requête MongoDB pour chaque nouveau message reçu | Pub/Sub push instantané — zéro polling |
| Pas d'historique de connexions léger et auto-géré | LIST bornée LPUSH/LTRIM, auto-nettoyée par Redis |
| Sessions gérées en base de données (lent, persistant inutilement) | HASH avec TTL — expiration automatique, aucun nettoyage manuel |

### Synthèse de toutes les clés Redis utilisées

| Clé Redis | Type | Usage |
|---|---|---|
| `online:users` | SET | Utilisateurs connectés en temps réel |
| `session:{username}` | HASH + TTL | Session active, expire après 30 min |
| `last_seen:{username}` | HASH | Date du dernier login/logout |
| `global:connection_log` | LIST bornée | Journal global des 500 dernières connexions |
| `connection_history:{u}` | LIST bornée | Historique personnel des 100 dernières connexions |
| `chat:{username}` | Pub/Sub canal | Diffusion des messages et indicateurs de frappe |

---

## Conclusion

Redis n'est pas utilisé dans PolyChat pour **remplacer** MongoDB, mais pour le **compléter**. Chaque technologie fait ce qu'elle fait de mieux :

- **MongoDB** persiste les données métier de manière fiable et interrogeable
- **Redis** gère la vélocité — les données qui changent à chaque seconde, les notifications instantanées, les sessions temporaires

Cette séparation des responsabilités est un **pattern architectural reconnu** dans les applications temps réel modernes. Elle permet à PolyChat d'être réactif pour les utilisateurs tout en restant fiable et structuré pour les données.
