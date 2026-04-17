import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import RegisterBody, LoginBody, UsernameBody
from app.database import get_db, get_redis
from app.auth import hash_password, verify_password, create_token, get_current_user, require_admin

router = APIRouter(prefix="/api/users", tags=["users"])


def _log_event(rc, username: str, event: str):
    """Enregistre un événement login/logout dans l'historique Redis."""
    now = datetime.now(timezone.utc).isoformat()
    payload = json.dumps({"username": username, "event": event, "timestamp": now})
    rc.lpush(f"connection_history:{username}", payload)
    rc.ltrim(f"connection_history:{username}", 0, 99)
    rc.lpush("global:connection_log", payload)
    rc.ltrim("global:connection_log", 0, 499)
    rc.hset(f"last_seen:{username}", f"last_{event}", now)


@router.post("/register", status_code=201)
def register(body: RegisterBody):
    """Inscription d'un nouvel utilisateur avec mot de passe."""
    db = get_db()
    redis_client = get_redis()

    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    username = body.username.strip()

    if db.users.find_one({"username": username}):
        raise HTTPException(status_code=409, detail="Ce pseudo est déjà utilisé")

    now = datetime.now(timezone.utc)
    db.users.insert_one({
        "username": username,
        "password": hash_password(body.password),
        "role": "user",
        "created_at": now,
    })

    if redis_client:
        now_iso = now.isoformat()
        redis_client.sadd("online:users", username)
        redis_client.hset(f"session:{username}", mapping={
            "username": username, "logged_in_at": now_iso
        })
        redis_client.expire(f"session:{username}", 1800)
        _log_event(redis_client, username, "login")

    token = create_token(username, "user")
    return {"token": token, "username": username, "role": "user"}


@router.post("/login")
def login(body: LoginBody):
    """Connexion avec vérification du mot de passe, retourne un JWT."""
    db = get_db()
    redis_client = get_redis()

    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    username = body.username.strip()
    user = db.users.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    if not user.get("password"):
        raise HTTPException(
            status_code=401,
            detail="Ce compte n'a pas de mot de passe. Utilisez 'password123' après redémarrage de l'application."
        )

    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    role = user.get("role", "user")

    if redis_client:
        now_iso = datetime.now(timezone.utc).isoformat()
        redis_client.sadd("online:users", username)
        redis_client.hset(f"session:{username}", mapping={
            "username": username, "logged_in_at": now_iso
        })
        redis_client.expire(f"session:{username}", 1800)
        _log_event(redis_client, username, "login")

    token = create_token(username, role)
    return {"token": token, "username": username, "role": role}


@router.post("/logout")
def logout(body: UsernameBody, current_user: dict = Depends(get_current_user)):
    """Déconnexion de l'utilisateur courant."""
    redis_client = get_redis()

    username = body.username.strip()

    # Un utilisateur ne peut se déconnecter que lui-même (sauf admin)
    if current_user.get("sub") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Action non autorisée")

    if redis_client:
        redis_client.srem("online:users", username)
        redis_client.delete(f"session:{username}")
        _log_event(redis_client, username, "logout")

    return {"message": "Déconnecté avec succès"}


@router.get("/online")
def get_online_users(current_user: dict = Depends(get_current_user)):
    """Liste des utilisateurs actuellement connectés."""
    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis non disponible")
    users = list(redis_client.smembers("online:users"))
    return {"users": users}


@router.get("/connection-log")
def get_global_connection_log(
    n: int = Query(default=50, ge=1, le=500),
    admin: dict = Depends(require_admin),
):
    """[Admin] Historique global des connexions/déconnexions."""
    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis non disponible")
    raw = redis_client.lrange("global:connection_log", 0, n - 1)
    return {"events": [json.loads(e) for e in raw]}


@router.get("/{username}/history")
def get_user_history(
    username: str,
    n: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Historique des connexions d'un utilisateur (le sien ou admin)."""
    if current_user.get("sub") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis non disponible")

    raw = redis_client.lrange(f"connection_history:{username}", 0, n - 1)
    return {"username": username, "events": [json.loads(e) for e in raw]}


@router.get("/{username}/last-seen")
def get_last_seen(username: str, current_user: dict = Depends(get_current_user)):
    """Retourne les dates du dernier login/logout d'un utilisateur."""
    redis_client = get_redis()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis non disponible")
    data = redis_client.hgetall(f"last_seen:{username}")
    if not data:
        raise HTTPException(status_code=404, detail="Aucune donnée pour cet utilisateur")
    return {"username": username, **data}


@router.get("/search")
def search_users(query: str, current_user: dict = Depends(get_current_user)):
    """Recherche d'utilisateurs par pseudo."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    if not query.strip():
        return {"users": []}
    users = list(
        db.users.find(
            {"username": {"$regex": query.strip(), "$options": "i"}},
            {"_id": 0, "username": 1}
        ).limit(10)
    )
    return {"users": [u["username"] for u in users]}
