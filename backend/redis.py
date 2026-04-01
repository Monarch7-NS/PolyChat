import os
from datetime import datetime
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


# ─── Utilisateurs connectés ───────────────────────

def user_connect(username: str):
    """Ajouter un utilisateur à la liste des connectés"""
    if r is None:
        return
    r.sadd('online:users', username)
    r.hset(f'session:{username}', mapping={
        'username': username,
        'logged_in_at': datetime.utcnow().isoformat()
    })
    r.expire(f'session:{username}', 1800)  # TTL 30 min


def user_disconnect(username: str):
    """Retirer un utilisateur de la liste des connectés"""
    if r is None:
        return
    r.srem('online:users', username)
    r.delete(f'session:{username}')


def get_online_users() -> list:
    """Retourner la liste des utilisateurs connectés"""
    if r is None:
        return []
    return list(r.smembers('online:users'))


def get_session(username: str) -> dict:
    """Retourner les infos de session d'un utilisateur"""
    if r is None:
        return {}
    return r.hgetall(f'session:{username}')


def refresh_session(username: str):
    """Remettre le TTL à 30 min (à appeler à chaque message envoyé)"""
    if r is None:
        return
    r.expire(f'session:{username}', 1800)