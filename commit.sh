#!/bin/bash

cd /workspaces/PolyChat

echo "======================================"
echo "Git - Commit et Push"
echo "======================================"

# Vérifier l'état
echo "État du repository :"
git status

# Ajouter tous les fichiers
echo ""
echo "Ajout des fichiers..."
git add .

# Vérifier les changements
echo ""
echo "Changements à être committés :"
git diff --cached --name-only

# Commit
echo ""
echo "Commit des changements..."
git commit -m "feat: Configuration complète de l'architecture PolyChat

- Création de la structure frontend React avec Axios
- Création de l'API backend Flask avec MongoDB et Redis
- Configuration du Docker Compose avec MongoDB ReplicaSet et Redis
- Dockerfiles pour frontend et backend
- Documentation complète (SETUP.md, README.md)
- Scripts d'installation et Makefile pour faciliter le développement
- Variables d'environnement et gitignore configurés
- Infrastructure prête pour l'équipe"

# Push vers GitHub
echo ""
echo "Push vers GitHub..."
git push origin main

echo ""
echo "======================================"
echo "✓ Commit et Push terminés !"
echo "======================================"
git log --oneline -1
