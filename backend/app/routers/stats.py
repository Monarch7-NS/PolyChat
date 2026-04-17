from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/top-sender")
def get_top_sender(admin: dict = Depends(require_admin)):
    """[Admin] Utilisateur ayant envoyé le plus de messages."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    result = list(
        db.messages.aggregate([
            {"$group": {"_id": "$from", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1},
        ])
    )
    if not result:
        raise HTTPException(status_code=404, detail="Aucun message trouvé")
    return {"username": result[0]["_id"], "message_count": result[0]["count"]}


@router.get("/top-receiver")
def get_top_receiver(admin: dict = Depends(require_admin)):
    """[Admin] Utilisateur ayant reçu le plus de messages."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    result = list(
        db.messages.aggregate([
            {"$group": {"_id": "$to", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1},
        ])
    )
    if not result:
        raise HTTPException(status_code=404, detail="Aucun message trouvé")
    return {"username": result[0]["_id"], "message_count": result[0]["count"]}


@router.get("/daily-activity")
def get_daily_activity(admin: dict = Depends(require_admin)):
    """[Admin] Nombre de messages par jour sur les 7 derniers jours."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    result = list(
        db.messages.aggregate([
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}},
            {"$limit": 7}
        ])
    )
    return {"activity": [{"date": r["_id"], "messages": r["count"]} for r in result]}


@router.get("/overview")
def get_overview(admin: dict = Depends(require_admin)):
    """[Admin] Vue d'ensemble : totaux utilisateurs, messages, conversations."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    return {
        "total_users": db.users.count_documents({}),
        "total_messages": db.messages.count_documents({}),
        "total_conversations": db.conversations.count_documents({}),
    }


@router.get("/all-users")
def get_all_users_stats(admin: dict = Depends(require_admin)):
    """[Admin] Stats de tous les utilisateurs (envoyés, reçus)."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    users = list(db.users.find({}, {"_id": 0, "username": 1, "role": 1, "created_at": 1}))
    result = []
    for u in users:
        username = u["username"]
        sent = db.messages.count_documents({"from": username})
        received = db.messages.count_documents({"to": username})
        result.append({
            "username": username,
            "role": u.get("role", "user"),
            "created_at": u.get("created_at", "").isoformat() if u.get("created_at") else "",
            "messages_sent": sent,
            "messages_received": received,
        })
    result.sort(key=lambda x: x["messages_sent"] + x["messages_received"], reverse=True)
    return {"users": result}


@router.get("/user-activity/{username}")
def get_user_activity(username: str, current_user: dict = Depends(get_current_user)):
    """Stats d'activité d'un utilisateur (accessible à tout utilisateur authentifié)."""

    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    sent = db.messages.count_documents({"from": username})
    received = db.messages.count_documents({"to": username})
    top_contact = list(
        db.messages.aggregate([
            {"$match": {"$or": [{"from": username}, {"to": username}]}},
            {"$project": {"contact": {"$cond": [{"$eq": ["$from", username]}, "$to", "$from"]}}},
            {"$group": {"_id": "$contact", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ])
    )
    return {
        "username": username,
        "messages_sent": sent,
        "messages_received": received,
        "total_messages": sent + received,
        "top_contact": top_contact[0]["_id"] if top_contact else None,
    }
