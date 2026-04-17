import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.models import MessageBody
from app.database import get_db, get_redis
from app.auth import get_current_user

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/send", status_code=201)
def send_message(body: MessageBody, current_user: dict = Depends(get_current_user)):
    db = get_db()
    redis_client = get_redis()

    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    from_user = body.from_user.strip()
    to_user = body.to_user.strip()
    content = body.content.strip()

    if current_user.get("sub") != from_user:
        raise HTTPException(status_code=403, detail="Vous ne pouvez envoyer des messages qu'en votre nom")

    if not all([from_user, to_user, content]):
        raise HTTPException(status_code=400, detail="Paramètres manquants")

    now = datetime.utcnow()
    message = {"from": from_user, "to": to_user, "content": content, "timestamp": now, "read": False}
    result = db.messages.insert_one(message)

    db.conversations.update_one(
        {"participants": sorted([from_user, to_user])},
        {
            "$set": {"last_message": content, "updated_at": now},
            "$setOnInsert": {"participants": sorted([from_user, to_user])},
        },
        upsert=True,
    )

    if redis_client:
        payload = json.dumps({
            "type": "new_message",
            "id": str(result.inserted_id),
            "from": from_user,
            "to": to_user,
            "content": content,
            "timestamp": now.isoformat(),
            "read": False,
        })
        redis_client.publish(f"chat:{to_user}", payload)

    return {"message": "Message envoyé avec succès", "id": str(result.inserted_id)}


@router.get("/conversation")
def get_conversation(user1: str, user2: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    user1 = user1.strip()
    user2 = user2.strip()

    if current_user.get("sub") not in (user1, user2) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    messages = list(
        db.messages.find(
            {"$or": [{"from": user1, "to": user2}, {"from": user2, "to": user1}]}
        ).sort("timestamp", 1)
    )
    for msg in messages:
        msg["_id"] = str(msg["_id"])
        msg["timestamp"] = msg["timestamp"].isoformat()

    return {"messages": messages}


@router.get("/search")
def search_messages(username: str, query: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    if current_user.get("sub") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    if not query.strip():
        raise HTTPException(status_code=400, detail="Paramètre query requis")

    messages = list(
        db.messages.find({
            "$and": [
                {"$or": [{"from": username}, {"to": username}]},
                {"content": {"$regex": query.strip(), "$options": "i"}},
            ]
        }).sort("timestamp", -1).limit(50)
    )
    for msg in messages:
        msg["_id"] = str(msg["_id"])
        msg["timestamp"] = msg["timestamp"].isoformat()

    return {"messages": messages}
