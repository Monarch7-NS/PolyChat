# Backend PolyChat - Flask API

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copiez `.env.example` en `.env`
2. Configurez les variables d'environnement selon votre setup

```bash
cp .env.example .env
```

## Démarrage

```bash
python app.py
```

Le serveur sera disponible sur http://localhost:5000

## API Endpoints

### Utilisateurs

- **POST** `/api/users/login` - Se connecter
- **POST** `/api/users/logout` - Se déconnecter
- **GET** `/api/users/online` - Obtenir la liste des utilisateurs en ligne

### Messages

- **POST** `/api/messages/send` - Envoyer un message
- **GET** `/api/messages/conversation` - Récupérer l'historique entre deux utilisateurs

### Statistiques

- **GET** `/api/stats/top-sender` - L'utilisateur qui envoie le plus de messages
- **GET** `/api/stats/top-receiver` - L'utilisateur qui reçoit le plus de messages

### Santé

- **GET** `/api/health` - État du serveur et des connexions
