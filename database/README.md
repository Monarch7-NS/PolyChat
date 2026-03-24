# Base de données - PolyChat

Ce dossier contient la configuration et les scripts de la base de données.

## MongoDB ReplicaSet

La configuration MongoDB est entièrement gérée par `docker-compose.yml`.

### Architecture

- **mongo1** : Node primaire (27017)
- **mongo2** : Node secondaire (27018)
- **mongo3** : Node secondaire (27019)

### Collections

#### users
```json
{
  "_id": ObjectId,
  "username": "string (unique)",
  "created_at": "datetime"
}
```

#### messages
```json
{
  "_id": ObjectId,
  "from": "string",
  "to": "string",
  "content": "string",
  "timestamp": "datetime",
  "read": "boolean"
}
```

#### conversations
```json
{
  "_id": ObjectId,
  "participants": ["string", "string"],
  "last_message": "string",
  "updated_at": "datetime"
}
```

## Redis

Utilisé pour :
- `online:users` : SET des utilisateurs connectés
- `session:{username}` : HASH des infos de session

## Accès à la base de données

```bash
# Avec Docker
docker exec -it mongo1 mongosh -u admin -p password --authenticationDatabase admin

# Avec une URI MongoDB locale
mongodb://admin:password@localhost:27017/?authSource=admin&replicaSet=polychat-rs
```
