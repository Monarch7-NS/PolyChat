import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import redis
from dotenv import load_dotenv

load_dotenv()

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'polychat')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

db = None
redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, redis_client

    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
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

    yield


app = FastAPI(title="PolyChat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== MODÈLES ==============

class UsernameBody(BaseModel):
    username: str

class MessageBody(BaseModel):
    from_user: str
    to_user: str
    content: str

    class Config:
        # Allow "from" as an alias since it's a Python keyword
        populate_by_name = True


# ============== ROUTES UTILISATEURS ==============

@app.post('/api/users/login')
def login(body: UsernameBody):
    """Enregistre un utilisateur comme connecté"""
    if db is None or redis_client is None:
        raise HTTPException(status_code=503, detail='Services non disponibles')

    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur requis")

    db.users.update_one(
        {'username': username},
        {
            '$setOnInsert': {'created_at': datetime.utcnow()},
            '$set': {'username': username}
        },
        upsert=True
    )

    redis_client.sadd('online:users', username)
    redis_client.hset(f'session:{username}', mapping={
        'username': username,
        'logged_in_at': datetime.utcnow().isoformat()
    })
    redis_client.expire(f'session:{username}', 1800)  # TTL 30 min

    return {'message': 'Connecté avec succès', 'username': username}


@app.post('/api/users/logout')
def logout(body: UsernameBody):
    """Déconnecte un utilisateur"""
    if redis_client is None:
        raise HTTPException(status_code=503, detail='Service Redis non disponible')

    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur requis")

    redis_client.srem('online:users', username)
    redis_client.delete(f'session:{username}')
    return {'message': 'Déconnecté avec succès'}


@app.get('/api/users/online')
def get_online_users():
    """Retourne la liste des utilisateurs actuellement en ligne"""
    if redis_client is None:
        raise HTTPException(status_code=503, detail='Service Redis non disponible')

    users = list(redis_client.smembers('online:users'))
    return {'users': users}


# ============== ROUTES MESSAGES ==============

@app.post('/api/messages/send', status_code=201)
def send_message(body: MessageBody):
    """Envoie un message d'un utilisateur à un autre"""
    if db is None:
        raise HTTPException(status_code=503, detail='MongoDB non disponible')

    from_user = body.from_user.strip()
    to_user = body.to_user.strip()
    content = body.content.strip()

    if not all([from_user, to_user, content]):
        raise HTTPException(status_code=400, detail='Paramètres manquants (from_user, to_user, content)')

    now = datetime.utcnow()
    message = {
        'from': from_user,
        'to': to_user,
        'content': content,
        'timestamp': now,
        'read': False
    }

    result = db.messages.insert_one(message)

    db.conversations.update_one(
        {'participants': sorted([from_user, to_user])},
        {
            '$set': {
                'last_message': content,
                'updated_at': now
            },
            '$setOnInsert': {
                'participants': sorted([from_user, to_user])
            }
        },
        upsert=True
    )

    return {'message': 'Message envoyé avec succès', 'id': str(result.inserted_id)}


@app.get('/api/messages/conversation')
def get_conversation(user1: str, user2: str):
    """Récupère l'historique entre deux utilisateurs"""
    if db is None:
        raise HTTPException(status_code=503, detail='MongoDB non disponible')

    user1 = user1.strip()
    user2 = user2.strip()
    if not user1 or not user2:
        raise HTTPException(status_code=400, detail='Paramètres user1 et user2 requis')

    messages = list(db.messages.find({
        '$or': [
            {'from': user1, 'to': user2},
            {'from': user2, 'to': user1}
        ]
    }).sort('timestamp', 1))

    for msg in messages:
        msg['_id'] = str(msg['_id'])
        msg['timestamp'] = msg['timestamp'].isoformat()

    return {'messages': messages}


# ============== ROUTES STATISTIQUES ==============

@app.get('/api/stats/top-sender')
def get_top_sender():
    """Retourne l'utilisateur qui envoie le plus de messages"""
    if db is None:
        raise HTTPException(status_code=503, detail='MongoDB non disponible')

    result = list(db.messages.aggregate([
        {'$group': {'_id': '$from', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 1}
    ]))

    if not result:
        raise HTTPException(status_code=404, detail='Aucun message trouvé')

    return {'username': result[0]['_id'], 'message_count': result[0]['count']}


@app.get('/api/stats/top-receiver')
def get_top_receiver():
    """Retourne l'utilisateur qui reçoit le plus de messages"""
    if db is None:
        raise HTTPException(status_code=503, detail='MongoDB non disponible')

    result = list(db.messages.aggregate([
        {'$group': {'_id': '$to', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 1}
    ]))

    if not result:
        raise HTTPException(status_code=404, detail='Aucun message trouvé')

    return {'username': result[0]['_id'], 'message_count': result[0]['count']}


# ============== ROUTE DE SANTÉ ==============

@app.get('/api/health')
def health():
    return {
        'status': 'ok',
        'mongodb': 'connected' if db else 'disconnected',
        'redis': 'connected' if redis_client else 'disconnected'
    }
