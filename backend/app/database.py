import redis
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config import MONGO_URI, MONGO_DB, REDIS_HOST, REDIS_PORT, REDIS_DB

db = None
redis_client = None


def connect():
    global db, redis_client

    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command("ping")
        db = mongo_client[MONGO_DB]
        print("✓ Connecté à MongoDB")
    except ServerSelectionTimeoutError:
        print("✗ Impossible de se connecter à MongoDB")

    try:
        redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
        redis_client.ping()
        print("✓ Connecté à Redis")
    except Exception as e:
        print(f"✗ Impossible de se connecter à Redis: {e}")


def get_db():
    return db


def get_redis():
    return redis_client
