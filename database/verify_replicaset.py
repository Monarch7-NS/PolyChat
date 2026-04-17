import time
from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27027,localhost:27018,localhost:27019/?replicaSet=rs0")

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Tentative de connexion au cluster MongoDB...")
    print(f"URI: {MONGO_URI}")
    
    try:
        # directConnection=False is implicit with replicaSet in URI
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Le ping force une découverte du cluster
        client.admin.command('ping')
        
        # Récupérer le status du ReplicaSet
        status = client.admin.command('replSetGetStatus')
        
        print(f"\n✅ Connecté avec succès au ReplicaSet: {status['set']}")
        print(f"Membres du cluster:")
        
        for member in status['members']:
            state_str = member['stateStr']
            name = member['name']
            health = "🟢 En ligne" if member['health'] == 1 else "🔴 Hors ligne"
            
            icon = "👑" if state_str == "PRIMARY" else ("🔄" if state_str == "SECONDARY" else "❓")
            print(f"  - {icon} {name} | État: {state_str} | Santé: {health}")
            
        print("\nTest réussi ! Parfait pour une capture d'écran du rapport.")
        
    except Exception as e:
        print(f"\n❌ Erreur de connexion ou ReplicaSet non initialisé: {e}")
        print("Avez-vous bien lancé `docker-compose up -d` ?")

if __name__ == "__main__":
    main()
