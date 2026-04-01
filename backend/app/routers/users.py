import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from app.models import UsernameBody
from app.database import get_db, get_redis

router = APIRouter(prefix="/api/users", tags=["users"])


def _log_event(rc, username: str, event: str):
    """Enregistre un événement login/logout dans l'historique Redis."""
    now = datetime.now(timezone.utc).isoformat()
    payload = json.dumps({"username": username, "event": event, "timestamp": now})
    rc.lpush(f"connection_history:{username}", payload)
    rc.ltrim(f"connection_history:{username}", 0, 99)   # 100 derniers max
    rc.lpush("global:connection_log", payload)
    rc.ltrim("global:connection_log", 0, 499)            # 500 derniers max
    rc.hset(f"last_seen:{username}", f"last_{event}", now)


@router.post("/login")
def login(body: UsernameBody):
    db = get_db()
    redis_client = get_redis()

    if db is None or redis_client is None:
        raise HTTPException(status_code=503, detail="Services non disponibles")

    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur requis")

    db.users.update_one(
        {"username": username},
        {
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
            "$set": {"username": username},
        },
        upsert=True,
    )

    now = datetime.now(timezone.utc).isoformat()
    redis_client.sadd("online:users", username)
    redis_client.hset(
        f"session:{username}",
        mapping={"username": username, "logged_in_at": now},
    )
    redis_client.expire(f"session:{username}", 1800)
    _log_event(redis_client, username, "login")

    return {"message": "Connecté avec succès", "username": username}


@router.post("/logout")
def logout(body: UsernameBody):
    redis_client = get_redis()

    if redis_client is None:
        raise HTTPException(status_code=503, detail="Service Redis non disponible")

    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur requis")

    redis_client.srem("online:users", username)
    redis_client.delete(f"session:{username}")
    _log_event(redis_client, username, "logout")
    return {"message": "Déconnecté avec succès"}


@router.get("/online")
def get_online_users():
    redis_client = get_redis()

    if redis_client is None:
        raise HTTPException(status_code=503, detail="Service Redis non disponible")

    users = list(redis_client.smembers("online:users"))
    return {"users": users}


@router.get("/connection-log")
def get_global_connection_log(n: int = Query(default=50, ge=1, le=500)):
    """Historique global des connexions/déconnexions (tous utilisateurs)."""
    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Service Redis non disponible")

    raw = redis_client.lrange("global:connection_log", 0, n - 1)
    return {"events": [json.loads(e) for e in raw]}


@router.get("/{username}/history")
def get_user_history(username: str, n: int = Query(default=50, ge=1, le=100)):
    """Historique des connexions/déconnexions d'un utilisateur spécifique."""
    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Service Redis non disponible")

    raw = redis_client.lrange(f"connection_history:{username}", 0, n - 1)
    return {"username": username, "events": [json.loads(e) for e in raw]}


@router.get("/{username}/last-seen")
def get_last_seen(username: str):
    """Retourne la date du dernier login et dernier logout d'un utilisateur."""
    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Service Redis non disponible")

    data = redis_client.hgetall(f"last_seen:{username}")
    if not data:
        raise HTTPException(status_code=404, detail="Aucune donnée pour cet utilisateur")
    return {"username": username, **data}


@router.get("/search")
def search_users(query: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    if not query.strip():
        return {"users": []}

    # Search in all users, excluding a potential "admin" or just finding matches
    users = list(
        db.users.find(
            {"username": {"$regex": query.strip(), "$options": "i"}},
            {"_id": 0, "username": 1}
        ).limit(10)
    )
    return {"users": [u["username"] for u in users]}
