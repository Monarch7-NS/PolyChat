#!/bin/bash

# Attendre que mongo1 soit prêt
echo "Attente de MongoDB..."
until mongosh --host mongo1 --eval "db.adminCommand('ping')" &>/dev/null; do
  sleep 2
done

# Initialiser le Replica Set (ignoré si déjà fait)
echo "Initialisation du Replica Set..."
mongosh --host mongo1 <<EOF
try {
  rs.initiate({
    _id: "rs0",
    members: [
      { _id: 0, host: "mongo1:27017" },
      { _id: 1, host: "mongo2:27017" },
      { _id: 2, host: "mongo3:27017" }
    ]
  });
} catch(e) {
  print("ReplicaSet déjà initialisé, on continue.");
}
EOF

echo "Replica Set initialisé."

# Attendre que le primary soit élu
echo "Attente de l'élection du primary..."
until mongosh --host mongo1 --quiet --eval "print(rs.isMaster().ismaster)" 2>/dev/null | grep -q "^true$"; do
  echo "  Primary pas encore élu, on attend..."
  sleep 3
done
echo "Primary élu."

# Import automatique si un dump est présent
if [ -d "/dump/polychat" ] && [ "$(ls -A /dump/polychat 2>/dev/null)" ]; then
  echo "Dump détecté dans /dump/polychat — import automatique en cours..."
  mongorestore --host mongo1 --nsInclude="polychat.*" /dump --drop
  echo "Import terminé."
else
  echo "Aucun dump trouvé, la base sera initialisée par le backend au démarrage."
fi
