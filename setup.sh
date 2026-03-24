#!/bin/bash

echo "======================================"
echo "PolyChat - Setup & Installation"
echo "======================================"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Frontend
echo -e "\n${BLUE}[1/3] Configuration du Frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances npm..."
    npm install
else
    echo "node_modules trouvé, passage de l'installation"
fi
cp .env.example .env 2>/dev/null || true
cd ..

# Backend
echo -e "\n${BLUE}[2/3] Configuration du Backend...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo "Création d'un environnement virtuel Python..."
    python3 -m venv venv
fi
echo "Activation de l'environnement virtuel..."
source venv/bin/activate
echo "Installation des dépendances Python..."
pip install -r requirements.txt
cp .env.example .env 2>/dev/null || true
cd ..

# Database
echo -e "\n${BLUE}[3/3] Configuration de la Base de Données...${NC}"
echo "MongoDB ReplicaSet et Redis seront configurés via Docker Compose"

echo -e "\n${GREEN}======================================"
echo "✓ Configuration complète !"
echo "======================================${NC}"

echo -e "\nPour démarrer l'infrastructure complète (Docker) :"
echo "  ${BLUE}docker compose up -d${NC}"

echo -e "\nOu pour un développement local :"
echo -e "  ${BLUE}Terminal 1 (Backend)${NC}"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    python app.py"

echo -e "\n  ${BLUE}Terminal 2 (Frontend)${NC}"
echo "    cd frontend"
echo "    npm start"

echo -e "\n  ${BLUE}Terminal 3 (Dépendances données)${NC}"
echo "    docker compose up mongo1 mongo2 mongo3 redis"

echo -e "\nVoir ${BLUE}SETUP.md${NC} pour plus de détails."
