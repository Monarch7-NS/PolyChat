#!/bin/bash

cd /workspaces/PolyChat

echo "======================================"
echo "Git Pull avec préservation du travail"
echo "======================================"

# Vérifier l'état actuel
echo ""
echo "État actuel du repository:"
git status

# Vérifier s'il y a des changements non committés
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
    echo ""
    echo "Aucun changement non committés, on peut faire un pull simple"
    git pull origin main
else
    echo ""
    echo "Changements détectés. Options :"
    echo ""
    echo "1. Faire un stash, pull, puis appliquer le stash"
    echo "   git stash"
    echo "   git pull origin main"
    echo "   git stash pop"
    echo ""
    echo "2. Faire directement un pull (qui mergera les changements)"
    echo "   git pull origin main"
    echo ""
    echo "Exécution de l'option 1 (plus sûre) ..."
    echo ""
    
    # Stash les changements
    echo "Sauvegarde des changements en cours..."
    git stash
    
    # Pull
    echo ""
    echo "Récupération des changements du serveur..."
    git pull origin main
    
    # Appliquer le stash
    echo ""
    echo "Application des changements sauvegardés..."
    git stash pop
fi

echo ""
echo "======================================"
echo "✓ Pull terminé !"
echo "======================================"
git log --oneline -3
