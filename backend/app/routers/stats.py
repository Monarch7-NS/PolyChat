from fastapi import APIRouter, HTTPException
from app.database import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/top-sender")
def get_top_sender():
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
def get_top_receiver():
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
def get_daily_activity():
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


@router.get("/user-activity/{username}")
def get_user_activity(username: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    # Messages envoyés
    sent = db.messages.count_documents({"from": username})
    
    # Messages reçus
    received = db.messages.count_documents({"to": username})
    
    # Avec qui l'utilisateur parle le plus
    top_contact = list(
        db.messages.aggregate([
            {"$match": {"$or": [{"from": username}, {"to": username}]}},
            {
                "$project": {
                    "contact": {
                        "$cond": [{"$eq": ["$from", username]}, "$to", "$from"]
                    }
                }
            },
            {"$group": {"_id": "$contact", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ])
    )

    top_contact_name = top_contact[0]["_id"] if top_contact else None

    return {
        "username": username,
        "messages_sent": sent,
        "messages_received": received,
        "total_messages": sent + received,
        "top_contact": top_contact_name
    }
