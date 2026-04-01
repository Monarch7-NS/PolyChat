#!/bin/bash

# Attendre que mongo1 soit prêt
echo "Attente de MongoDB..."
until mongosh --host mongo1 --eval "db.adminCommand('ping')" &>/dev/null; do
  sleep 2
done

# Initialiser le Replica Set
echo "Initialisation du Replica Set..."
mongosh --host mongo1 <<EOF
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27017" },
    { _id: 2, host: "mongo3:27017" }
  ]
})
EOF

echo "Replica Set initialisé."
