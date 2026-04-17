import redis
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config import MONGO_URI, MONGO_DB, REDIS_HOST, REDIS_PORT, REDIS_DB

db = None
redis_client = None


import time

def connect():
    global db, redis_client

    # Retry temporisé pour s'assurer que le ReplicaSet est bien initié par MongoDB
    max_retries = 10
    for i in range(max_retries):
        try:
            mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            mongo_client.admin.command("ping")
            db = mongo_client[MONGO_DB]
            print("✓ Connecté à MongoDB")
            
            # Création des index (Optimisation des performances)
            db.messages.create_index([("from", 1), ("to", 1)])
            db.messages.create_index([("timestamp", -1)])
            db.conversations.create_index([("participants", 1)])
            print("✓ Index MongoDB vérifiés/créés")
            break
        except Exception as e:
            print(f"✗ Impossible de se connecter à MongoDB (Essai {i+1}/{max_retries}): {e}")
            time.sleep(3)

    try:
        redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
        redis_client.ping()
        print("✓ Connecté à Redis")
    except Exception as e:
        print(f"✗ Impossible de se connecter à Redis: {e}")

    # Auto-remplissage de la BDD si elle est vide
    if db is not None and redis_client is not None:
        try:
            from app.seed import seed_database
            seed_database(db, redis_client)
        except Exception as e:
            print("Erreur pendant le seeding :", e)


def get_db():
    if db is None:
        connect()
    return db


def get_redis():
    if redis_client is None:
        connect()
    return redis_client
