from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.database import get_db

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/{username}")
def get_conversations(username: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    convs = list(
        db.conversations.find({"participants": username}).sort("updated_at", -1)
    )

    result = []
    for conv in convs:
        other_user = next((p for p in conv["participants"] if p != username), None)
        if not other_user:
            continue
        unread_count = db.messages.count_documents(
            {"from": other_user, "to": username, "read": False}
        )
        result.append({
            "other_user": other_user,
            "last_message": conv.get("last_message", ""),
            "updated_at": conv.get("updated_at", datetime.utcnow()).isoformat(),
            "unread_count": unread_count,
        })

    return {"conversations": result}


@router.put("/read")
def mark_as_read(from_user: str, to_user: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")

    db.messages.update_many(
        {"from": from_user, "to": to_user, "read": False},
        {"$set": {"read": True}},
    )
    return {"message": "Messages marqués comme lus"}
