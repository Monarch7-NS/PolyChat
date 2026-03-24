#!/bin/bash

# Script de pull sécurisé avec gestion automatique du stash

cd /workspaces/PolyChat || { echo "Erreur: impossible d'accéder au répertoire"; exit 1; }

echo "======================================"
echo "Git Pull - Préservation du travail"
echo "======================================"

# Vérifier si git est disponible
if ! command -v git &> /dev/null; then
    echo "✗ Git n'est pas installé"
    exit 1
fi

echo ""
echo "État actuel:"
git status --short

# Vérifier s'il y a des changements locaux
if git diff-index --quiet HEAD --; then
    echo ""
    echo "✓ Pas de changements non committés"
    echo "Pull simple en cours..."
    git pull origin main
    EXIT_CODE=$?
else
    echo ""
    echo "⚠ Changements locaux détectés"
    echo "Stratégie: stash → pull → stash pop"
    echo ""
    
    # Créer un stash avec timestamp
    STASH_NAME="auto-stash-$(date +%s)"
    echo "Sauvegarde des changements: $STASH_NAME"
    git stash push -m "$STASH_NAME"
    STASH_EXIT=$?
    
    if [ $STASH_EXIT -ne 0 ]; then
        echo "✗ Erreur lors du stash"
        exit 1
    fi
    
    echo ""
    echo "Pull en cours..."
    git pull origin main
    PULL_EXIT=$?
    
    if [ $PULL_EXIT -ne 0 ]; then
        echo "✗ Erreur lors du pull, restauration du stash..."
        git stash pop
        exit 1
    fi
    
    echo ""
    echo "Application des changements sauvegardés..."
    git stash pop
    STASH_POP_EXIT=$?
    
    if [ $STASH_POP_EXIT -ne 0 ]; then
        echo ""
        echo "⚠ Conflit détecté lors de l'application du stash"
        echo "Les fichiers en conflit doivent être résolus manuellement"
        echo ""
        echo "Commandes utiles:"
        echo "  git status              # Voir les conflits"
        echo "  git diff                # Voir les différences"
        echo "  git checkout --ours <file>   # Garder votre version"
        echo "  git checkout --theirs <file> # Garder la version du serveur"
        echo "  git add . && git commit      # Valider la résolution"
        exit 1
    fi
    
    EXIT_CODE=0
fi

echo ""
echo "======================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Pull réussi !"
else
    echo "✗ Pull échoué (code: $EXIT_CODE)"
fi
echo "======================================"
echo ""
echo "Historique récent:"
git log --oneline -3

exit $EXIT_CODE
