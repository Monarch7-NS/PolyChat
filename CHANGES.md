# Fichiers modifiés et créés

## ✅ Nouveau pull sécurisé

### Scripts Git
- **`do-pull.sh`** - Script de pull automatique avec gestion du stash
  - Détecte les changements locaux
  - Sauvegarde automatiquement avec `git stash`
  - Récupère les changements du serveur
  - Réapplique les changements locaux
  - Gère les conflits intelligemment

- **`pull.sh`** - Script alternatif de pull
- **`commit.sh`** - Script de commit et push

### Documentation
- **`GIT_GUIDE.md`** (nouveau) - Guide complet sur Git
  - Synchronisation sécurisée
  - Gestion des conflits
  - Scénarios courants
  - Bonnes pratiques
  - Commandes utiles

- **`SETUP.md`** (modifié)
  - Ajout de la section "Collaboration et Git"
  - Références au GIT_GUIDE.md
  - Commandes pratiques avec Make

- **`Makefile`** (modifié)
  - Commande `make git-pull` - Pull sécurisé
  - Commande `make git-push` - Push interactif
  - Section "Git Commands" organisée

## 🚀 Comment utiliser

### Option 1: Avec Make (recommandé)
```bash
make git-pull    # Pull sécurisé
make git-push    # Commit et push
```

### Option 2: Avec les scripts
```bash
bash do-pull.sh  # Pull sécurisé
bash commit.sh   # Commit et push
```

### Option 3: Manuelle
```bash
git stash
git pull origin main
git stash pop
git add .
git commit -m "..."
git push origin main
```

## 📋 Flux de travail recommandé

1. **Au début de la journée:**
   ```bash
   make git-pull
   ```

2. **Pendant le développement:**
   - Travaillez à votre rythme
   - Committez régulièrement

3. **Avant la fin:**
   ```bash
   make git-push
   ```

## ✨ Avantages de cette approche

✅ **Sûr** - Votre travail n'est jamais perdu
✅ **Simple** - Une seule commande
✅ **Intelligent** - Gère l'automatiquement les conflits mineurs
✅ **Documenté** - Guide complet fourni
✅ **Pratique** - Accessible via Make ou scripts
✅ **Transparent** - Vous voyez ce qui se passe

## 🔧 En cas de problème

Consultez [GIT_GUIDE.md](./GIT_GUIDE.md) pour :
- Résolution de conflits
- Annulation de changements
- Gestion d'erreurs
- Scénarios avancés

## 📞 Support

Si vous avez des questions sur le workflow Git :
1. Consultez [GIT_GUIDE.md](./GIT_GUIDE.md)
2. Utilisez `git status` pour vérifier l'état
3. Demandez à votre collègue en cas de doute
