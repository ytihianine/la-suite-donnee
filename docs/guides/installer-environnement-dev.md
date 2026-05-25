# Installer l'environnement de développement

## Résumé

À la fin de ce guide, vous aurez un environnement Python fonctionnel avec tous les packages nécessaires au projet installés et les hooks pre-commit configurés.

## Contexte

**Prérequis :**
- Python 3.12 installé sur votre machine
- `make` disponible en ligne de commande
- Accès au dépôt du projet cloné localement

**Public cible :** développeurs, nouveaux arrivants sur le projet

## Détails

### 1. Créer l'environnement Python

Exécuter la commande suivante à la racine du projet pour créer un environnement virtuel Python :

```bash
make create-py-env
```

Cette commande crée un environnement virtuel dans le dossier `env/` via `python3 -m venv`.

### 2. Activer l'environnement

Une fois l'environnement créé, l'activer dans votre terminal :

```bash
source env/bin/activate
```

> **Windows :** utiliser `env\Scripts\activate` à la place.

Vous devriez voir le nom de l'environnement `(env)` apparaître en début de ligne dans votre terminal.

### 3. Installer les packages Python

Avec l'environnement activé, lancer l'installation des dépendances :

```bash
make install-py-packages
```

Cette commande effectue les opérations suivantes :
- Met à jour `pip` vers la dernière version
- Installe `uv` (gestionnaire de packages performant)
- Installe les dépendances listées dans `requirements.txt` via `uv`

### 4. Installer les hooks pre-commit

Le projet utilise [pre-commit](https://pre-commit.com/) pour exécuter automatiquement des vérifications avant chaque commit (formatage, linting, validation YAML, etc.).

Installer les hooks Git :

```bash
make install-pre-commit
```

Les hooks suivants seront activés :
- `trailing-whitespace` : supprime les espaces en fin de ligne
- `end-of-file-fixer` : assure un saut de ligne en fin de fichier
- `check-yaml` : valide la syntaxe des fichiers YAML
- `check-added-large-files` : bloque l'ajout de fichiers volumineux
- `ruff` : linting et tri des imports
- `ruff-format` : formatage du code Python

Les hooks s'exécuteront automatiquement à chaque `git commit`. Pour les lancer manuellement sur tous les fichiers :

```bash
pre-commit run --all-files
```

### 5. Vérifier l'installation

Contrôler que l'environnement est bien configuré :

```bash
which python
```

Le résultat doit pointer vers `env/bin/python`. Vous pouvez également vérifier que les packages sont installés :

```bash
pip list
```

## Références

- [Documentation officielle venv](https://docs.python.org/3.12/library/venv.html)
- [Documentation uv](https://github.com/astral-sh/uv)
- [Documentation pre-commit](https://pre-commit.com/)
- [Ruff (linter/formateur)](https://docs.astral.sh/ruff/)
- [Makefile du projet](../../Makefile)
