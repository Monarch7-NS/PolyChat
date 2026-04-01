import os
import json
from datetime import datetime, timezone
import redis

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB   = int(os.getenv('REDIS_DB', 0))

r = None


def connect_redis():
    global r
    try:
        r = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
        r.ping()
        print("✓ Connecté à Redis")
    except Exception as e:
        print(f"✗ Impossible de se connecter à Redis: {e}")


def get_redis():
    return r


# ─── Utilisateurs connectés (état instantané) ─────────────────────────────────

def user_connect(username: str, client=None):
    """Ajouter un utilisateur à la liste des connectés + logger la connexion"""
    rc = client or r
    if rc is None:
        return
    rc.sadd('online:users', username)
    rc.hset(f'session:{username}', mapping={
        'username': username,
        'logged_in_at': datetime.now(timezone.utc).isoformat()
    })
    rc.expire(f'session:{username}', 1800)  # TTL 30 min
    # Historique
    log_login(username, rc)


def user_disconnect(username: str, client=None):
    """Retirer un utilisateur de la liste des connectés + logger la déconnexion"""
    rc = client or r
    if rc is None:
        return
    rc.srem('online:users', username)
    rc.delete(f'session:{username}')
    # Historique
    log_logout(username, rc)


def get_online_users(client=None) -> list:
    """Retourner la liste des utilisateurs actuellement connectés"""
    rc = client or r
    if rc is None:
        return []
    return list(rc.smembers('online:users'))


def get_session(username: str, client=None) -> dict:
    """Retourner les infos de session active d'un utilisateur"""
    rc = client or r
    if rc is None:
        return {}
    return rc.hgetall(f'session:{username}')


def refresh_session(username: str, client=None):
    """Remettre le TTL à 30 min (à appeler à chaque message envoyé)"""
    rc = client or r
    if rc is None:
        return
    rc.expire(f'session:{username}', 1800)


# ─── Historique des connexions ────────────────────────────────────────────────
#
# Structures utilisées :
#   connection_history:<username>  LIST  — événements du user (login/logout), 100 max
#   global:connection_log          LIST  — log global tous users, 500 max
#   last_seen:<username>           HASH  — derniers login_at et logout_at du user
#
# Chaque événement est un JSON : {"username": "...", "event": "login|logout", "timestamp": "ISO"}

def log_login(username: str, client=None):
    """Enregistre un événement login dans l'historique Redis"""
    rc = client or r
    if rc is None:
        return
    now = datetime.now(timezone.utc).isoformat()
    event = json.dumps({"username": username, "event": "login", "timestamp": now})
    rc.lpush(f"connection_history:{username}", event)
    rc.ltrim(f"connection_history:{username}", 0, 99)   # garde les 100 derniers
    rc.lpush("global:connection_log", event)
    rc.ltrim("global:connection_log", 0, 499)            # garde les 500 derniers
    rc.hset(f"last_seen:{username}", "last_login", now)


def log_logout(username: str, client=None):
    """Enregistre un événement logout dans l'historique Redis"""
    rc = client or r
    if rc is None:
        return
    now = datetime.now(timezone.utc).isoformat()
    event = json.dumps({"username": username, "event": "logout", "timestamp": now})
    rc.lpush(f"connection_history:{username}", event)
    rc.ltrim(f"connection_history:{username}", 0, 99)
    rc.lpush("global:connection_log", event)
    rc.ltrim("global:connection_log", 0, 499)
    rc.hset(f"last_seen:{username}", "last_logout", now)


def get_connection_history(username: str, n: int = 50, client=None) -> list:
    """Retourne les n derniers événements de connexion d'un utilisateur (login + logout)"""
    rc = client or r
    if rc is None:
        return []
    raw = rc.lrange(f"connection_history:{username}", 0, n - 1)
    return [json.loads(e) for e in raw]


def get_global_connection_log(n: int = 50, client=None) -> list:
    """Retourne les n derniers événements de connexion toutes personnes confondues"""
    rc = client or r
    if rc is None:
        return []
    raw = rc.lrange("global:connection_log", 0, n - 1)
    return [json.loads(e) for e in raw]


def get_last_seen(username: str, client=None) -> dict:
    """Retourne la date du dernier login et dernier logout d'un utilisateur"""
    rc = client or r
    if rc is None:
        return {}
    return rc.hgetall(f"last_seen:{username}")
