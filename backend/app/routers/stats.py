from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from app.database import get_db, get_redis

router = APIRouter(prefix="/api/stats", tags=["stats"])


def _get_top(redis_client, key: str):
    """Retourne le membre avec le score le plus élevé d'un Sorted Set."""
    result = redis_client.zrevrange(key, 0, 0, withscores=True)
    if not result:
        return None
    username, score = result[0]
    return {"username": username, "message_count": int(score)}


@router.get("/top-sender")
def get_top_sender():
    rc = get_redis()
    if rc is not None:
        top = _get_top(rc, "leaderboard:senders")
        if top:
            return top

    # Fallback MongoDB si Redis vide
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Services non disponibles")
    result = list(db.messages.aggregate([
        {"$group": {"_id": "$from", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1},
    ]))
    if not result:
        raise HTTPException(status_code=404, detail="Aucun message trouvé")
    return {"username": result[0]["_id"], "message_count": result[0]["count"]}


@router.get("/top-receiver")
def get_top_receiver():
    rc = get_redis()
    if rc is not None:
        top = _get_top(rc, "leaderboard:receivers")
        if top:
            return top

    # Fallback MongoDB si Redis vide
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Services non disponibles")
    result = list(db.messages.aggregate([
        {"$group": {"_id": "$to", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1},
    ]))
    if not result:
        raise HTTPException(status_code=404, detail="Aucun message trouvé")
    return {"username": result[0]["_id"], "message_count": result[0]["count"]}


@router.get("/daily-activity")
def get_daily_activity():
    rc = get_redis()
    if rc is not None:
        raw = rc.hgetall("daily:activity")
        if raw:
            # Trier et garder les 7 derniers jours
            today = datetime.utcnow().date()
            last_7 = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
            activity = [
                {"date": d, "messages": int(raw.get(d, 0))}
                for d in last_7
                if d in raw
            ]
            activity.sort(key=lambda x: x["date"], reverse=True)
            return {"activity": activity, "source": "redis"}

    # Fallback MongoDB
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Services non disponibles")
    result = list(db.messages.aggregate([
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 7}
    ]))
    return {"activity": [{"date": r["_id"], "messages": r["count"]} for r in result]}


@router.get("/user-activity/{username}")
def get_user_activity(username: str):
    rc = get_redis()
    sent, received = 0, 0

    if rc is not None:
        sent = int(rc.zscore("leaderboard:senders", username) or 0)
        received = int(rc.zscore("leaderboard:receivers", username) or 0)

    # Si Redis vide, fallback MongoDB
    if sent == 0 and received == 0:
        db = get_db()
        if db is None:
            raise HTTPException(status_code=503, detail="Services non disponibles")
        sent = db.messages.count_documents({"from": username})
        received = db.messages.count_documents({"to": username})

    # Top contact toujours depuis MongoDB (pas dans Redis)
    db = get_db()
    top_contact = None
    if db is not None:
        top = list(db.messages.aggregate([
            {"$match": {"$or": [{"from": username}, {"to": username}]}},
            {"$project": {"contact": {"$cond": [{"$eq": ["$from", username]}, "$to", "$from"]}}},
            {"$group": {"_id": "$contact", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))
        top_contact = top[0]["_id"] if top else None

    return {
        "username": username,
        "messages_sent": sent,
        "messages_received": received,
        "total_messages": sent + received,
        "top_contact": top_contact
    }
