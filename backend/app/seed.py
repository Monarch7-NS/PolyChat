import json
from datetime import datetime, timedelta
from app.auth import hash_password


def seed_database(db, redis_client):
    try:
        if db.messages.count_documents({}) > 0:
            print("Base de données déjà peuplée, on ignore le seeding.")
            return

        print("Seeding de la base de données...")

        # ── Utilisateurs avec mots de passe hashés ─────────────────────────────
        users = [
            {"username": "Alice",   "password": "password123", "role": "user"},
            {"username": "Bob",     "password": "password123", "role": "user"},
            {"username": "Charlie", "password": "password123", "role": "user"},
            {"username": "Prof",    "password": "password123", "role": "user"},
            {"username": "admin",   "password": "admin1234",   "role": "admin"},
        ]

        now = datetime.utcnow()
        for u in users:
            db.users.update_one(
                {"username": u["username"]},
                {
                    "$setOnInsert": {"created_at": now},
                    "$set": {
                        "username": u["username"],
                        "password": hash_password(u["password"]),
                        "role": u["role"],
                    },
                },
                upsert=True,
            )

        # ── Historique Redis pour les utilisateurs fictifs ──────────────────────
        if redis_client:
            for u in users:
                username = u["username"]
                time_login = (now - timedelta(days=1)).isoformat()
                event_login = json.dumps({"username": username, "event": "login", "timestamp": time_login})
                redis_client.lpush(f"connection_history:{username}", event_login)
                redis_client.lpush("global:connection_log", event_login)
                redis_client.hset(f"last_seen:{username}", "last_login", time_login)

                time_logout = (now - timedelta(hours=22)).isoformat()
                event_logout = json.dumps({"username": username, "event": "logout", "timestamp": time_logout})
                redis_client.lpush(f"connection_history:{username}", event_logout)
                redis_client.lpush("global:connection_log", event_logout)
                redis_client.hset(f"last_seen:{username}", "last_logout", time_logout)

        # ── Messages de démonstration ───────────────────────────────────────────
        messages_data = [
            ("Alice", "Bob",     "Salut Bob, comment tu vas ?",                         120),
            ("Bob",   "Alice",   "Salut Alice ! Ça roule et toi ?",                     115),
            ("Alice", "Bob",     "Très bien ! J'ai fini la partie MongoDB du projet.",   110),
            ("Bob",   "Alice",   "Super, il me reste le seeding à faire avec Redis !",  105),
            ("Charlie", "Prof",  "Bonjour monsieur, j'ai une question sur les ReplicaSets.", 60),
            ("Prof",  "Charlie", "Bonjour Charlie. Le ReplicaSet garantit la haute disponibilité.", 55),
            ("Charlie", "Prof",  "D'accord merci ! J'ai réussi.",                        50),
            ("Alice", "Charlie", "Coucou Charlie, tu as avancé sur le Dashboard React ?", 30),
            ("Charlie", "Alice", "Oui, c'est magnifique avec le Glassmorphism !",         25),
            ("Alice", "Charlie", "Totalement !",                                          10),
        ]

        for sender, receiver, text, min_ago in messages_data:
            ts = now - timedelta(minutes=min_ago)
            db.messages.insert_one({
                "from": sender, "to": receiver,
                "content": text, "timestamp": ts, "read": True,
            })
            db.conversations.update_one(
                {"participants": sorted([sender, receiver])},
                {
                    "$set": {"last_message": text, "updated_at": ts},
                    "$setOnInsert": {"participants": sorted([sender, receiver])},
                },
                upsert=True,
            )

        print("Seeding terminé avec succès.")
        print("  Comptes de démonstration :")
        print("    Alice / Bob / Charlie / Prof  →  mot de passe : password123")
        print("    admin                          →  mot de passe : admin1234")

    except Exception as e:
        print(f"Erreur lors du seeding : {e}")
