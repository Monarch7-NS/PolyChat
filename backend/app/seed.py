import json
from datetime import datetime, timedelta
from app.auth import hash_password


def seed_database(db, redis_client):
    try:
        # ── Toujours créer/mettre à jour l'admin (indépendamment du reste) ──────
        admin_users = [
            {"username": "admin", "password": "admin1234", "role": "admin"},
        ]
        for u in admin_users:
            existing = db.users.find_one({"username": u["username"]})
            if not existing or not existing.get("password"):
                db.users.update_one(
                    {"username": u["username"]},
                    {"$set": {
                        "username": u["username"],
                        "password": hash_password(u["password"]),
                        "role": u["role"],
                    }, "$setOnInsert": {"created_at": datetime.utcnow()}},
                    upsert=True,
                )
                print(f"✓ Compte '{u['username']}' créé/mis à jour (rôle: {u['role']})")

        # ── Migrer les utilisateurs existants sans mot de passe ─────────────────
        # (utilisateurs créés avant l'ajout de l'authentification)
        users_without_password = list(db.users.find({"password": {"$exists": False}}))
        for u in users_without_password:
            db.users.update_one(
                {"username": u["username"]},
                {"$set": {"password": hash_password("password123"), "role": "user"}}
            )
            print(f"✓ Mot de passe ajouté pour l'utilisateur existant '{u['username']}' (password123)")

        if db.messages.count_documents({}) > 0:
            print("Base de données déjà peuplée, on ignore le seeding des messages.")
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
        print(f"❌ Erreur lors du seeding de la base de données : {e}")

    # Reconstruction des leaderboards Redis depuis MongoDB (toujours exécutée)
    _rebuild_redis_stats(db, redis_client)


def _rebuild_redis_stats(db, redis_client):
    """Reconstruit les Sorted Sets Redis de stats depuis MongoDB si vides."""
    try:
        if redis_client is None:
            return

        # Ne reconstruire que si les leaderboards sont vides
        if redis_client.zcard("leaderboard:senders") > 0:
            print("💡 Leaderboards Redis déjà présents, reconstruction ignorée.")
            return

        print("🔄 Reconstruction des leaderboards Redis depuis MongoDB...")

        # Leaderboard expéditeurs
        senders = db.messages.aggregate([
            {"$group": {"_id": "$from", "count": {"$sum": 1}}}
        ])
        for s in senders:
            redis_client.zadd("leaderboard:senders", {s["_id"]: s["count"]})

        # Leaderboard destinataires
        receivers = db.messages.aggregate([
            {"$group": {"_id": "$to", "count": {"$sum": 1}}}
        ])
        for r in receivers:
            redis_client.zadd("leaderboard:receivers", {r["_id"]: r["count"]})

        # Activité journalière
        daily = db.messages.aggregate([
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "count": {"$sum": 1}
            }}
        ])
        for d in daily:
            redis_client.hset("daily:activity", d["_id"], d["count"])

        print("✅ Leaderboards Redis reconstruits depuis MongoDB.")

    except Exception as e:
        print(f"⚠️ Erreur reconstruction Redis stats : {e}")
