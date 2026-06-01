# Installer l'environnement de développement

## Résumé

À la fin de ce guide, vous aurez un environnement Python fonctionnel avec les dépendances du projet installées, les hooks pre-commit configurés et un workflow Git/release clarifié.

## Contexte

**Prérequis :**
- Python 3.12 installé sur votre machine
- Node.js 24+ (nécessaire pour la release via semantic-release)
- `make` disponible en ligne de commande
- Accès au dépôt du projet cloné localement

**Public cible :** développeurs, nouveaux arrivants sur le projet

## Détails

### Installation en une commande

Vous pouvez installer l'ensemble de l'environnement de développement avec la commande suivante:

```bash
make setup-dev-env
```

Cette commande exécute automatiquement :
- `make create-py-env`
- `make install-py-packages`
- `make install-pre-commit`

Important : la variable `ENV_NAME` est lue depuis le fichier `.env`.
Si vous n'avez pas encore de fichier `.env`, commencez par :

```bash
make duplicate-env-vars
```

### 1. Initialiser le fichier `.env` (première installation)

Dupliquer le template de variables d'environnement :

```bash
make duplicate-env-vars
```

Cette étape crée le fichier `.env` avec les valeurs par défaut du projet, dont `ENV_NAME=env`.

### 2. Créer l'environnement Python

Exécuter la commande suivante à la racine du projet pour créer un environnement virtuel Python :

```bash
make create-py-env
```

Cette commande crée un environnement virtuel dans le dossier défini par `ENV_NAME` (par défaut `env/`) via `python3 -m venv`.

### 3. Activer l'environnement (recommandé)

Une fois l'environnement créé, l'activer dans votre terminal :

```bash
source env/bin/activate
```

> **Windows :** utiliser `env\Scripts\activate` à la place.

Vous devriez voir le nom de l'environnement `(env)` apparaître en début de ligne dans votre terminal.

Note : les cibles `make` utilisent directement l'interpréteur de l'environnement virtuel (`$(VENV_BIN)/python`).
L'activation reste recommandée pour exécuter vos commandes Python interactives (`python`, `pip`, etc.) dans le bon contexte.

### 4. Installer les packages Python

Avec l'environnement activé, lancer l'installation des dépendances :

```bash
make install-py-packages
```

Cette commande effectue les opérations suivantes :
- Met à jour `pip` vers la dernière version
- Installe `uv` (gestionnaire de packages performant)
- Installe les dépendances listées dans `requirements.txt` via `uv`

### 5. Installer les hooks pre-commit

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

Les hooks s'exécuteront automatiquement à chaque `git commit`.
Pour les lancer manuellement sur tous les fichiers :

```bash
make run-pre-commit
```

### 6. Vérifier l'installation

Contrôler que l'environnement est bien configuré :

```bash
which python
```

Le résultat doit pointer vers `env/bin/python`. Vous pouvez également vérifier que les packages sont installés :

```bash
pip list
make test
```

La commande `make test` exécute les tests du dossier `tests/` via `pytest`.

## Workflow de release

Le workflow adopté pour ce dépôt est une stratégie de Trunk-Based Development.
Les releases sont gérées via [semantic-release](https://semantic-release.gitbook.io/) et le workflow GitHub Actions [github-release](../../.github/workflows/github-release.yaml), déclenché manuellement.

### Branches

| Branche   | Rôle                     |
|-----------|--------------------------|
| `main`    | Branche de production    |
| `feat/<sujet>` | Branche de développement |
| `fix/<sujet>`  | Branche de correction    |

Toutes les branches, à l'exception de `main`, doivent être de courte durée et fusionnées rapidement dans `main`.

### Étapes

1. **Créer une branche courte depuis `main`**

```bash
git checkout main
git pull origin main
git checkout -b feat/mon-sujet
```

2. **Développer et valider localement**

```bash
make run-pre-commit
make test
```

3. **Créer une Pull Request vers `main`**
- Vérifier que la CI est verte
- Demander une review

4. **Fusionner la PR**
- Préférer un historique propre (squash ou rebase selon vos conventions d'équipe)

5. **Déclencher la release manuelle**
- Aller dans l'onglet GitHub Actions
- Lancer le workflow `github-release`

Lorsque la release est déclenchée, `semantic-release` analyse les commits et publie automatiquement la version GitHub correspondante.

### Pré-requis GitHub Actions

Un secret `GH_TOKEN` doit être configuré dans le dépôt GitHub avec les permissions suivantes :
- `contents: write`
- `issues: write`
- `pull-requests: write`

## Références

- [Documentation officielle venv](https://docs.python.org/3.12/library/venv.html)
- [Documentation uv](https://github.com/astral-sh/uv)
- [Documentation pre-commit](https://pre-commit.com/)
- [Ruff (linter/formateur)](https://docs.astral.sh/ruff/)
- [Workflow de release GitHub](../../.github/workflows/github-release.yaml)
- [Makefile du projet](../../Makefile)
