from fastapi import APIRouter, WebSocket
from app.ws_manager import handle_websocket

router = APIRouter()


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await handle_websocket(websocket, username)
