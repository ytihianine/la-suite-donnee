# La Suite Donnée

La Suite Donnée est un ensemble d'outils qui permettent de faire du traitement de données bout en bout (récolte, traitement, documentation, dataviz ...).
Ce repository est un guide d'installation de l'ensemble des outils qui composent la Suite Donnée.

## Table des matières

[TO DEFINE]

## Pré-requis

- Kubernetes*
- Python v3.12+
- Node v24+
- `make`

*Seul un accès à un namespace est nécessaire. Certaines ressources nécessiteront des droits d'admin du cluster.

## Structure

```
.
├── .github/
│    ├── workflows: workflows github
│    └── skills: skills copilot
├── ansible/     # Playbooks Ansible
├── argocd/      # ArgoCD application manifests
├── tests/       # Tests unitaires (pytest)
└── docs/        # Documentation complementaire
```

## Installation

```bash
make setup-dev-env
source env/bin/activate
```

Cette commande crée l'environnement virtuel, installe les dépendances et configure pre-commit.


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

### Pré-requis GitHub Actions

Un secret `GH_TOKEN` doit être configuré dans le repository GitHub avec les permissions `contents: write`, `issues: write` et `pull-requests: write`.

## Commandes disponibles

Quelques commandes utiles

| Commande              | Description                                      |
|-----------------------|--------------------------------------------------|
| `make setup-dev-env`  | Configure l'environnement de developpement       |
| `make test`           | Lance les tests pytest                           |
| `make clean`          | Supprime les fichiers temporaires                |
