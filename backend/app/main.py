from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import database
from app.routers import users, messages, stats, conversations, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.connect()
    yield


app = FastAPI(title="PolyChat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(messages.router)
app.include_router(stats.router)
app.include_router(conversations.router)
app.include_router(ws.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mongodb": "connected" if database.get_db() else "disconnected",
        "redis": "connected" if database.get_redis() else "disconnected",
    }
