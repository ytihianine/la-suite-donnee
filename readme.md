# Template projet Python

Ce repository est un template de projet Python. Il sert de base pour démarrer un nouveau projet avec certains standards et des outils déjà configurés (semantic-release).
Il peut être adapté pour utiliser d'autres technologies (node, ...).

## Pré-requis

- Python 3.12
- Node v24+
- `make`

## Installation

```bash
make setup-dev-env
source env/bin/activate
```

Cette commande crée l'environnement virtuel, installe les dépendances et configure pre-commit.

## Variables d'environnement

Copier `.env.example` en `.env` et adapter les valeurs.
Si des variables d'environnement sont ajoutées, il faut modifier `src/utils/settings.py` pour qu'elles soient lues.

## Lancer le projet

```bash
python -m src.main
```

## Tests

Pour lancer les tests
```bash
make test
```

## Structure

```
.
├── .github/
│    ├── workflows: workflows github
│    └── skills: skills copilot
├── src/         # Code source
├── tests/       # Tests unitaires (pytest)
└── docs/        # Documentation complementaire
```

## Workflow de release

Les releases sont gérées automatiquement via [semantic-release](https://semantic-release.gitbook.io/) et deux workflows GitHub Actions.

### Branches

| Branche   | Rôle                                                                 |
|-----------|----------------------------------------------------------------------|
| `main`    | Branche de production — chaque push déclenche une release            |
| `release` | Branche de validation — permet de simuler la prochaine release       |

### Étapes

1. **Développement** : les commits sont réalisés sur des branches de feature/fix avec des messages au format [Conventional Commits](https://www.conventionalcommits.org/) (ex: `feat:`, `fix:`, `chore:`...).
2. **Pré-release (dry-run)** : merger sur la branche `release` déclenche le workflow `pre-release` qui exécute `semantic-release --dry-run`. Aucune release n'est publiée ; cela permet de vérifier le numéro de version et le changelog qui seraient générés.
3. **Release** : merger sur `main` déclenche le workflow `release` qui exécute `semantic-release` et publie la release GitHub avec le tag de version et le changelog correspondant.

> Les deux workflows peuvent également être déclenchés manuellement depuis l'onglet **Actions** de GitHub.

### Pré-requis

Un secret `GH_TOKEN` doit être configuré dans le repository GitHub avec les permissions `contents: write`, `issues: write` et `pull-requests: write`.

## Commandes disponibles

Quelques commandes utiles

| Commande              | Description                                      |
|-----------------------|--------------------------------------------------|
| `make setup-dev-env`  | Configure l'environnement de developpement       |
| `make test`           | Lance les tests pytest                           |
| `make clean`          | Supprime les fichiers temporaires                |
