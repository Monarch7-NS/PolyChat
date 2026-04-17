.PHONY: help install dev docker-up docker-down logs clean git-pull git-push db-export db-import

help:
	@echo "PolyChat - Commandes disponibles"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Installer les dépendances"
	@echo ""
	@echo "Git:"
	@echo "  make git-pull      - Pull sécurisé (préserve le travail local)"
	@echo "  make git-push      - Commit et push les changements"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Lancer tous les services"
	@echo "  make docker-down   - Arrêter tous les services"
	@echo "  make docker-clean  - Arrêter et supprimer les volumes"
	@echo "  make logs          - Voir les logs de tous les services"
	@echo ""
	@echo "Base de données:"
	@echo "  make db-export     - Exporter la base MongoDB vers ./dump_polychat/"
	@echo "  make db-import     - Importer la base MongoDB depuis ./dump_polychat/"
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

# ========== Git Commands ==========

git-pull:
	@echo "Pull sécurisé en cours..."
	@chmod +x do-pull.sh
	@./do-pull.sh

git-push:
	@echo "Push des changements..."
	git status --short
	@read -p "Voulez-vous continuer? (y/n) " ans; \
	if [ "$$ans" = "y" ]; then \
		git add .; \
		read -p "Message de commit: " msg; \
		git commit -m "$$msg"; \
		git push origin main; \
		echo "✓ Push terminé"; \
	else \
		echo "Annulé"; \
	fi

# ========== Development ==========

dev-backend:
	@echo "Lancement du backend..."
	cd backend && source venv/bin/activate && python app.py

dev-frontend:
	@echo "Lancement du frontend..."
	cd frontend && npm start

dev-db:
	@echo "Lancement de MongoDB ReplicaSet et Redis..."
	docker compose up -d mongo1 mongo2 mongo3 redis

# ========== Status & Utils ==========

status:
	@docker compose ps

shell-mongo:
	docker exec -it mongo1 mongosh -u admin -p password --authenticationDatabase admin

shell-redis:
	docker exec -it redis redis-cli

# ========== Base de données ==========

db-export:
	@echo "Export de la base MongoDB vers ./dump_polychat/ ..."
	docker exec mongo1 mongodump --db polychat --out /dump
	docker cp mongo1:/dump ./dump_polychat
	@echo "Export terminé : ./dump_polychat/"

db-import:
	@echo "Import de la base MongoDB depuis ./dump_polychat/ ..."
	docker cp ./dump_polychat mongo1:/dump
	docker exec mongo1 mongorestore --db polychat /dump/polychat --drop
	@echo "Import terminé"

clean:
	@echo "Nettoyage..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Nettoyage terminé"

.DEFAULT_GOAL := help
