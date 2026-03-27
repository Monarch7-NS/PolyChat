import asyncio
import json
import redis.asyncio as aioredis
from fastapi import WebSocket
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB


async def handle_websocket(websocket: WebSocket, username: str):
    await websocket.accept()

    r = aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )
    pubsub = r.pubsub()
    await pubsub.subscribe(f"chat:{username}")

    stop_event = asyncio.Event()

    async def redis_listener():
        try:
            async for message in pubsub.listen():
                if stop_event.is_set():
                    break
                if message["type"] == "message":
                    try:
                        await websocket.send_text(message["data"])
                    except Exception:
                        stop_event.set()
                        break
        except Exception:
            stop_event.set()

    listener_task = asyncio.create_task(redis_listener())

    try:
        while not stop_event.is_set():
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=25)
                try:
                    data = json.loads(raw)
                    msg_type = data.get("type")
                    if msg_type in ("typing", "stop_typing"):
                        to_user = data.get("to")
                        if to_user:
                            payload = json.dumps({"type": msg_type, "from": username})
                            await r.publish(f"chat:{to_user}", payload)
                except (json.JSONDecodeError, Exception):
                    pass
            except asyncio.TimeoutError:
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    break
            except Exception:
                break
    finally:
        stop_event.set()
        listener_task.cancel()
        try:
            await pubsub.unsubscribe(f"chat:{username}")
            await r.aclose()
        except Exception:
            pass
