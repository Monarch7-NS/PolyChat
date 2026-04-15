import json
from datetime import datetime, timedelta

def seed_database(db, redis_client):
    try:
        # Vérifie si la base est déjà remplie pour éviter les doublons au redémarrage
        if db.messages.count_documents({}) > 0:
            print("💡 Base de données déjà peuplée, on ignore le remplissage.")
            return

        print("🌱 Remplissage (Seeding) de la base de données avec des utilisateurs fictifs...")
        
        users = ["Alice", "Bob", "Charlie", "Prof"]
        now = datetime.utcnow()
        
        # 1. Remplissage de l'historique Redis
        for u in users:
            # On simule qu'ils se sont tous connectés il y a 1 jour
            time_login = (now - timedelta(days=1)).isoformat()
            
            event = {
                "username": u,
                "event": "login",
                "timestamp": time_login
            }
            redis_client.lpush("connection_log", json.dumps(event))
            redis_client.hset("last_seen", u, time_login)
            
            # Et déconnectés 2 heures après
            time_logout = (now - timedelta(days=1, hours=-2)).isoformat()
            event_logout = {
                "username": u,
                "event": "logout",
                "timestamp": time_logout
            }
            redis_client.lpush("connection_log", json.dumps(event_logout))
            redis_client.hset("last_seen", u, time_logout)

        # 2. Ajout de messages dans MongoDB
        # format: (expéditeur, destinataire, message, minutes_dans_le_passe)
        messages_data = [
            ("Alice", "Bob", "Salut Bob, comment tu vas ?", 120),
            ("Bob", "Alice", "Salut Alice ! Ça roule et toi ?", 115),
            ("Alice", "Bob", "Très bien ! J'ai fini la partie MongoDB du projet PolyChat.", 110),
            ("Bob", "Alice", "Super, il me reste juste le seeding à faire avec Redis !", 105),
            ("Charlie", "Prof", "Bonjour monsieur, j'ai une question sur les ReplicaSets.", 60),
            ("Prof", "Charlie", "Bonjour Charlie. Le ReplicaSet garantit la haute disponibilité.", 55),
            ("Charlie", "Prof", "D'accord merci ! J'ai réussi.", 50),
            ("Alice", "Charlie", "Coucou Charlie, tu as avancé sur le Dashboard React ?", 30),
            ("Charlie", "Alice", "Oui, c'est magnifique avec le Glassmorphism !", 25),
            ("Alice", "Charlie", "Totalement 🤩", 10),
        ]

        for sender, receiver, text, min_ago in messages_data:
            ts = now - timedelta(minutes=min_ago)
            
            # Sauvegarde Message
            db.messages.insert_one({
                "from": sender,
                "to": receiver,
                "content": text,
                "timestamp": ts,
                "read": True
            })
            
            # Mise à jour Conversation
            db.conversations.update_one(
                {"participants": sorted([sender, receiver])},
                {
                    "$set": {"last_message": text, "updated_at": ts},
                    "$setOnInsert": {"participants": sorted([sender, receiver])},
                },
                upsert=True,
            )
            
            # Mise à jour de l'utilisateur
            db.users.update_one(
                {"username": sender},
                {"$setOnInsert": {"created_at": ts}, "$set": {"username": sender}},
                upsert=True
            )
            db.users.update_one(
                {"username": receiver},
                {"$setOnInsert": {"created_at": ts}, "$set": {"username": receiver}},
                upsert=True
            )

        print("✅ Base de données remplie avec succès avec les données de démonstration !")

    except Exception as e:
        print(f"❌ Erreur lors du seeding de la base de données : {e}")
