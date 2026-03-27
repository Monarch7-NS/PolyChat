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
