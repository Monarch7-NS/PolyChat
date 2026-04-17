from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.ws_manager import handle_websocket
from app.auth import decode_token

router = APIRouter()


@router.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    token: str = Query(...),
):
    """WebSocket protégé par JWT (token passé en query param)."""
    try:
        payload = decode_token(token)
        if payload.get("sub") != username:
            await websocket.close(code=4001, reason="Token ne correspond pas à l'utilisateur")
            return
    except Exception:
        await websocket.close(code=4001, reason="Token invalide")
        return

    await handle_websocket(websocket, username)
