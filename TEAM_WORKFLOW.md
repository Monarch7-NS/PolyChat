# Workflow Git - Manuel d'équipe PolyChat

Bonjour ! 👋

Ce document explique comment nous collaborons efficacement sur PolyChat en gérant les modifications simultanées sans perdre du travail.

## 🎯 Le problème

Quand deux personnes travaillent sur le même repository :
- Vous modifiez `README.md`
- Votre collègue modifie aussi `README.md` et pousse
- Vous ne pouvez pas pousser sans créer un conflit

**Solution:** Utiliser un workflow Git sécurisé avec `stash`.

## ✅ La solution

### Option 1: Commande simple (recommandé)

```bash
make git-pull
```

C'est tout ! Le script s'occupe de :
1. Sauvegarder votre travail
2. Récupérer les changements de votre collègue
3. Réappliquer votre travail

### Option 2: Script manuel

```bash
bash do-pull.sh
```

### Option 3: Commandes manuelles

```bash
git stash              # Sauvegarder votre travail
git pull origin main   # Récupérer les changements
git stash pop          # Réappliquer votre travail
```

## 📋 Workflow complet

### 1. Au matin: Synchroniser

```bash
cd /workspaces/PolyChat
make git-pull
```

### 2. Pendant la journée: Travailler

Modifiez les fichiers normalement. Pas de `git add` nécessaire pour maintenant.

### 3. Avant de pousser: Préparer

Si vous avez peur de perdre votre travail:

```bash
git status              # Voir les changements
git stash              # Sauvegarder en securité
git pull origin main   # Récupérer les changements
git stash pop          # Réappliquer
```

### 4. Pousser vos changements

```bash
make git-push
```

Ou manuellement:

```bash
git add .
git commit -m "Description de vos changements"
git push origin main
```

## 🚨 En cas de conflit

Un conflit apparaît si vous et votre collègue modifiez la **même ligne** du **même fichier**.

### Étapes de résolution

```bash
# 1. Voir le conflit
git status
# Fichiers avec conflit (both modified)

# 2. Éditer le fichier problématique
cat README.md
# Vous verrez des marqueurs:
# <<<<<<<  Votre version
# =======
# >>>>>>>  Version du serveur

# 3. Supprimer les marqueurs et fusionner manuellement

# 4. Valider la résolution
git add .
git commit -m "Résolution du conflit"
git push origin main
```

### Exemple de conflit

**Avant:**
```
<<<<<<< HEAD
# Mon titre - Version locale
=======
# Le titre du collègue - Version du serveur
>>>>>>> origin/main
```

**Après résolution (garder les deux ou choisir une):**
```
# Le titre du collègue - Version du serveur
# Ou fusionner les deux de manière intelligente
```

## 💡 Bonnes pratiques

### ✅ À faire

1. **Pullez en premier**
   ```bash
   make git-pull
   ```

2. **Committez régulièrement**
   ```bash
   git commit -m "feature: Ajout de la validation"
   git commit -m "fix: Correction du bug de login"
   ```

3. **Utilisez des messages clairs**
   ```
   feature: Ajout de la validation des messages
   fix: Correction du calcul des statistiques
   docs: Mise à jour du README
   ```

4. **Poussez régulièrement**
   ```bash
   make git-push
   ```

5. **Communiquez en cas de conflits**
   - "Je travaille sur le backend API"
   - "Je modifie le README"

### ❌ À éviter

1. **Ne forcez jamais un push**
   ```bash
   git push --force  # 🔴 DANGEREUX!
   ```

2. **Ne commitez pas les dépendances**
   ```bash
   git add node_modules  # 🔴 NON!
   git add __pycache__   # 🔴 NON!
   ```

3. **Ne modifiez pas les variables d'env en prod**
   ```bash
   # Éditez .env.example, pas .env
   ```

4. **Ne commitez jamais les secrets**
   ```bash
   # Pas de mots de passe dans le code!
   ```

## 📚 Ressources

- [GIT_GUIDE.md](./GIT_GUIDE.md) - Guide complet et détaillé
- [SETUP.md](./SETUP.md) - Guide d'installation
- [CHANGES.md](./CHANGES.md) - Récapitulatif des modifications

## 🔧 Cheatsheet rapide

| Besoin | Commande |
|--------|----------|
| Synchroniser | `make git-pull` |
| Voir l'état | `git status` |
| Voir mes changements | `git diff` |
| Ajouter des fichiers | `git add .` |
| Valider | `git commit -m "msg"` |
| Pousser | `make git-push` |
| Voir l'historique | `git log --oneline` |
| Annuler un changement | `git checkout -- file` |
| Annuler le dernier commit | `git reset --soft HEAD~1` |

## ⚠️ Urgence: Erreur grave

Si tout part en vrille:

```bash
# 1. Sauvegarder votre travail
git stash

# 2. Récupérer une version propre
git fetch origin
git reset --hard origin/main

# 3. Réappliquer votre travail
git stash pop
```

**Attention:** Cette commande écrase complètement votre dossier local!

## 📞 Besoin d'aide?

1. Consultez [GIT_GUIDE.md](./GIT_GUIDE.md)
2. Vérifiez votre statut: `git status`
3. Demandez à votre collègue
4. Utilisez `git reset --hard origin/main` pour recommencer proprement

---

**Heureux développement! 🚀**

N'oubliez pas:
- ✅ Pull souvent
- ✅ Commit régulièrement  
- ✅ Push avant de partir
- ✅ Communiquez avec l'équipe
