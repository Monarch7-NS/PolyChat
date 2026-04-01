from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models import UsernameBody
from app.database import get_db, get_redis

router = APIRouter(prefix="/api/users", tags=["users"])


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
            "$setOnInsert": {"created_at": datetime.utcnow()},
            "$set": {"username": username},
        },
        upsert=True,
    )

    redis_client.sadd("online:users", username)
    redis_client.hset(
        f"session:{username}",
        mapping={"username": username, "logged_in_at": datetime.utcnow().isoformat()},
    )
    redis_client.expire(f"session:{username}", 1800)

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
    return {"message": "Déconnecté avec succès"}


@router.get("/online")
def get_online_users():
    redis_client = get_redis()

    if redis_client is None:
        raise HTTPException(status_code=503, detail="Service Redis non disponible")

    users = list(redis_client.smembers("online:users"))
    return {"users": users}


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
