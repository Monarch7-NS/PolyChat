#!/bin/bash
set -e

echo ">>> Waiting for mongo1 to accept connections..."
until mongosh --host mongo1 --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; do
  sleep 2
done

echo ">>> Initiating replica set rs0..."
mongosh --host mongo1 --eval "
  try {
    rs.initiate({
      _id: 'rs0',
      members: [
        { _id: 0, host: 'mongo1:27017' },
        { _id: 1, host: 'mongo2:27017' },
        { _id: 2, host: 'mongo3:27017' }
      ]
    });
    print('ReplicaSet initiated.');
  } catch(e) {
    print('rs.initiate error (may already be initiated): ' + e.message);
  }
" --quiet

echo ">>> Waiting for primary election..."
until mongosh --host mongo1 --eval "db.hello().isWritablePrimary" --quiet 2>/dev/null | grep -q "true"; do
  sleep 2
done
echo ">>> Primary elected."

echo ">>> Creating collections and indexes on polychat database..."
mongosh --host mongo1 --eval "
  db = db.getSiblingDB('polychat');

  // users: unique index on username
  db.users.createIndex({ username: 1 }, { unique: true, name: 'username_unique' });

  // messages: index for conversation queries, and timestamp sort
  db.messages.createIndex({ from: 1, to: 1, timestamp: 1 }, { name: 'conversation_idx' });
  db.messages.createIndex({ timestamp: -1 }, { name: 'timestamp_desc' });

  // conversations: unique on sorted participants pair, and recency sort
  db.conversations.createIndex({ participants: 1 }, { unique: true, name: 'participants_unique' });
  db.conversations.createIndex({ updated_at: -1 }, { name: 'updated_at_desc' });

  print('Indexes created: ' + JSON.stringify(db.getCollectionNames()));
" --quiet

echo ">>> Database initialization complete!"
