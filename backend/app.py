import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import redis
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'polychat')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Connexions aux bases de données
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    db = mongo_client[MONGO_DB]
    print("✓ Connecté à MongoDB")
except ServerSelectionTimeoutError:
    print("✗ Impossible de se connecter à MongoDB")
    db = None

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
    print("✓ Connecté à Redis")
except Exception as e:
    print(f"✗ Impossible de se connecter à Redis: {e}")
    redis_client = None


# ============== ROUTES UTILISATEURS ==============

@app.route('/api/users/login', methods=['POST'])
def login():
    """Enregistre un utilisateur comme connecté"""
    if not db or not redis_client:
        return jsonify({'error': 'Services non disponibles'}), 503
    
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Nom d\'utilisateur requis'}), 400
    
    try:
        # Insérer ou mettre à jour l'utilisateur dans MongoDB
        db.users.update_one(
            {'username': username},
            {'$set': {'username': username, 'created_at': datetime.utcnow()}},
            upsert=True
        )
        
        # Ajouter à Redis (ensemble des utilisateurs en ligne)
        redis_client.sadd('online:users', username)
        redis_client.hset(f'session:{username}', mapping={
            'username': username,
            'logged_in_at': datetime.utcnow().isoformat()
        })
        redis_client.expire(f'session:{username}', 1800)  # TTL 30 min
        
        return jsonify({'message': 'Connecté avec succès', 'username': username}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/logout', methods=['POST'])
def logout():
    """Déconnecte un utilisateur"""
    if not redis_client:
        return jsonify({'error': 'Service Redis non disponible'}), 503
    
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Nom d\'utilisateur requis'}), 400
    
    try:
        redis_client.srem('online:users', username)
        redis_client.delete(f'session:{username}')
        return jsonify({'message': 'Déconnecté avec succès'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/online', methods=['GET'])
def get_online_users():
    """Retourne la liste des utilisateurs actuellement en ligne"""
    if not redis_client:
        return jsonify({'error': 'Service Redis non disponible'}), 503
    
    try:
        users = list(redis_client.smembers('online:users'))
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== ROUTES MESSAGES ==============

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Envoie un message d'un utilisateur à un autre"""
    if not db:
        return jsonify({'error': 'MongoDB non disponible'}), 503
    
    data = request.json
    from_user = data.get('from', '').strip()
    to_user = data.get('to', '').strip()
    content = data.get('content', '').strip()
    
    if not all([from_user, to_user, content]):
        return jsonify({'error': 'Paramètres manquants (from, to, content)'}), 400
    
    try:
        message = {
            'from': from_user,
            'to': to_user,
            'content': content,
            'timestamp': datetime.utcnow(),
            'read': False
        }
        
        result = db.messages.insert_one(message)
        
        # Mettre à jour la conversation
        db.conversations.update_one(
            {'participants': {'$all': [from_user, to_user]}},
            {
                '$set': {
                    'last_message': content,
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Si pas d'ensemble participants défini, en ajouter
        db.conversations.update_one(
            {'_id': result.inserted_id},
            {'$set': {'participants': sorted([from_user, to_user])}}
        )
        
        return jsonify({
            'message': 'Message envoyé avec succès',
            'id': str(result.inserted_id)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/messages/conversation', methods=['GET'])
def get_conversation():
    """Récupère l'historique entre deux utilisateurs"""
    if not db:
        return jsonify({'error': 'MongoDB non disponible'}), 503
    
    user1 = request.args.get('user1', '').strip()
    user2 = request.args.get('user2', '').strip()
    
    if not user1 or not user2:
        return jsonify({'error': 'Paramètres user1 et user2 requis'}), 400
    
    try:
        messages = list(db.messages.find({
            '$or': [
                {'from': user1, 'to': user2},
                {'from': user2, 'to': user1}
            ]
        }).sort('timestamp', 1))
        
        # Convertir les ObjectId et datetime en strings
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat()
        
        return jsonify({'messages': messages}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== ROUTES STATISTIQUES ==============

@app.route('/api/stats/top-sender', methods=['GET'])
def get_top_sender():
    """Retourne l'utilisateur qui envoie le plus de messages"""
    if not db:
        return jsonify({'error': 'MongoDB non disponible'}), 503
    
    try:
        result = db.messages.aggregate([
            {'$group': {'_id': '$from', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 1}
        ])
        
        result = list(result)
        if result:
            return jsonify({
                'username': result[0]['_id'],
                'message_count': result[0]['count']
            }), 200
        
        return jsonify({'message': 'Aucun message trouvé'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats/top-receiver', methods=['GET'])
def get_top_receiver():
    """Retourne l'utilisateur qui reçoit le plus de messages"""
    if not db:
        return jsonify({'error': 'MongoDB non disponible'}), 503
    
    try:
        result = db.messages.aggregate([
            {'$group': {'_id': '$to', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 1}
        ])
        
        result = list(result)
        if result:
            return jsonify({
                'username': result[0]['_id'],
                'message_count': result[0]['count']
            }), 200
        
        return jsonify({'message': 'Aucun message trouvé'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== ROUTE DE SANTÉ ==============

@app.route('/api/health', methods=['GET'])
def health():
    """Vérif de la santé du serveur"""
    status = {
        'status': 'ok',
        'mongodb': 'connected' if db else 'disconnected',
        'redis': 'connected' if redis_client else 'disconnected'
    }
    return jsonify(status), 200


# ============== GESTION D'ERREURS ==============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route non trouvée'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur interne du serveur'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
