# Guide Git pour PolyChat

## Synchronisation avec l'équipe

### Pull sécurisé (préserve votre travail)

```bash
# Option 1: Avec le script fourni
bash do-pull.sh

# Option 2: Avec Make
make git-pull

# Option 3: Manuellement avec stash
git stash
git pull origin main
git stash pop
```

**Stratégie:**
1. Sauvegarder vos changements locaux (`git stash`)
2. Récupérer les changements du serveur (`git pull`)
3. Réappliquer vos changements (`git stash pop`)

### Push de vos changements

```bash
# Option 1: Avec Make
make git-push

# Option 2: Manuellement
git add .
git commit -m "Description de vos changements"
git push origin main
```

---

## Gestion des conflits

### Avant de faire un pull

```bash
# Vérifier l'état de votre repository
git status

# Voir les changements locaux
git diff

# Voir les changements non committés
git diff --cached
```

### Si un conflit survient

Un conflit se manifeste par des marqueurs `<<<<<<<`, `=======`, `>>>>>>>` dans les fichiers.

```bash
# 1. Voir le statut
git status

# 2. Voir les conflits en détail
git diff

# 3. Consulter chaque fichier et résoudre manuellement
# Les marqueurs indiquent:
# <<<<<<<  Début de votre version
# =======  Séparateur
# >>>>>>>  Fin de leur version

# 4. Après résolution, valider
git add .
git commit -m "Résolution des conflits"
```

### Stratégies de résolution

**Garder votre version:**
```bash
git checkout --ours <fichier>
```

**Garder la version du serveur:**
```bash
git checkout --theirs <fichier>
```

**Annuler et recommencer:**
```bash
git merge --abort
```

---

## Scénarios courants

### Scénario 1: Vous et un collègue modifiez le même fichier

```bash
# Votre travail en local
git stash

# Récupérer ses changements
git pull origin main

# Réappliquer vos changements
git stash pop

# Si conflit: éditer le fichier et résoudre
git add <fichier>
git commit -m "Fusion des changements"
git push origin main
```

### Scénario 2: Conflit dans README.md

```bash
# 1. Voir le conflit
cat README.md  # Voir les marqueurs <<<<<<<, =======, >>>>>>>

# 2. Éditer le fichier pour combiner les changements
# Vous pouvez garder les deux versions ou en choisir une

# 3. Valider la résolution
git add README.md
git commit -m "Fusion du README"
git push
```

### Scénario 3: Annuler un pull et recommencer

```bash
# Si le pull a créé un conflit
git merge --abort

# Recommencer proprement
git stash
git pull origin main
git stash pop
```

---

## Bonnes pratiques

1. **Toujours faire un pull avant de commencer**
   ```bash
   make git-pull
   ```

2. **Committez régulièrement votre travail**
   ```bash
   git add .
   git commit -m "Descriptif du changement"
   ```

3. **Utilisez des messages clairs**
   ```bash
   # ✓ Bon
   git commit -m "feat: Ajout de la validation des messages"
   
   # ✗ Mauvais
   git commit -m "fix"
   ```

4. **Push régulièrement pour éviter les gros conflits**
   ```bash
   make git-push
   ```

5. **En cas de doute, demandez à votre collègue**
   - Ne forcez jamais un push (`git push --force`)
   - Communiquez sur les zones du code que vous modifiez

---

## Commandes utiles

```bash
# Voir l'historique
git log --oneline

# Voir les changements non committés
git diff

# Voir les changements committés mais non pushés
git diff origin/main

# Annuler les changements d'un fichier
git checkout -- <fichier>

# Annuler le dernier commit (avant push)
git reset --soft HEAD~1

# Voir les branches
git branch -a

# Voir le statut détaillé
git status -s
```

---

## En cas de problème grave

```bash
# Sauvegarder tout votre travail
git stash

# Récupérer une version propre
git fetch origin
git reset --hard origin/main

# Réappliquer votre travail
git stash pop
```

**⚠️ Attention:** Cette commande écrase complètement votre répertoire local!

---

## Fichiers importants

- `do-pull.sh` - Script de pull sécurisé
- `commit.sh` - Script de commit et push
- `Makefile` - Commandes raccourcis (`make git-pull`, `make git-push`)

Consultez le [README principal](./README.md) pour plus de détails sur le projet.
