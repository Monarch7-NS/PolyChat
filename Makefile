.PHONY: help install dev docker-up docker-down logs clean

help:
	@echo "PolyChat - Commandes disponibles"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Installer les dépendances"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Lancer tous les services"
	@echo "  make docker-down   - Arrêter tous les services"
	@echo "  make docker-clean  - Arrêter et supprimer les volumes"
	@echo "  make logs          - Voir les logs de tous les services"
	@echo ""
	@echo "Développement:"
	@echo "  make dev-backend   - Lancer le backend (terminal séparé requis)"
	@echo "  make dev-frontend  - Lancer le frontend (terminal séparé requis)"
	@echo "  make dev-db        - Lancer seulement mongo et redis"
	@echo ""

install:
	@echo "Installation des dépendances..."
	@chmod +x setup.sh
	@./setup.sh

docker-up:
	@echo "Lancement de tous les services..."
	docker compose up -d
	@echo "Services lancés !"
	@echo "Frontend:  http://localhost:3000"
	@echo "Backend:   http://localhost:5000"
	@echo "MongoDB:   localhost:27017, 27018, 27019"
	@echo "Redis:     localhost:6379"

docker-down:
	@echo "Arrêt de tous les services..."
	docker compose down

docker-clean:
	@echo "Arrêt et suppression des volumes..."
	docker compose down -v
	@echo "Volumes supprimés"

logs:
	docker compose logs -f

logs-%:
	docker compose logs -f $*

dev-backend:
	@echo "Lancement du backend..."
	cd backend && source venv/bin/activate && python app.py

dev-frontend:
	@echo "Lancement du frontend..."
	cd frontend && npm start

dev-db:
	@echo "Lancement de MongoDB ReplicaSet et Redis..."
	docker compose up -d mongo1 mongo2 mongo3 redis

status:
	@docker compose ps

shell-mongo:
	docker exec -it mongo1 mongosh -u admin -p password --authenticationDatabase admin

shell-redis:
	docker exec -it redis redis-cli

clean:
	@echo "Nettoyage..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Nettoyage terminé"

.DEFAULT_GOAL := help
