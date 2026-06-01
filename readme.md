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
├── images/      # Dockerfile & build
├── tests/       # Tests unitaires (pytest)
└── docs/        # Documentation complementaire
```

## Installation

### Configuration de l'installation

#### Configuration de l'environnement
**Dupliquer les variables d'environnements**
```bash
make duplicate-env-vars
```
Configurez les variables d'environnement dans le fichier `.env` en fonction de votre environnement.

**Configurer l'environnement python**

```bash
make setup-dev-env
source env/bin/activate
```
Cette commande crée l'environnement virtuel et installe les packages nécessaires.

**Configurer Ansible**

La configuration d'Ansible est disponible dans le fichier [ansible.cfg](ansible.cfg).  
L'option become_exe est à changer en fonction de la version de votre unix. Si vous utiliser sudors, vous devez utiliser `sudo.ws`.

```bash
# become_exe = sudo.ws
```

#### Configuration des applications

Les manifestes des applications se situent dans `argocd/`.

**ArgoCD**

_Indisponible pour le moment_.  
A installer manuellement selon vos différentes possibilités.

**ArgoCD CLI**

Si vous souhaitez installer la CLI d'ArgoCD, renseigner `LSD_INSTALL_ARGOCD_CLI=true` dans votre fichier [.env](.env#24).  
Aucune configuration particulière complémentaire.

**Renovatebot**

Si vous souhaitez installer renovatebot, renseigner `LSD_INSTALL_RENOVATE=true` dans votre fichier [.env](.env#25).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [renovatebot-secret.yaml](argocd/renovatebot/templates/renovatebot-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/renovatebot/values-prod.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:

```yaml
renovate:
    cronjob:
        # -- Schedules the job to run using cron notation
        schedule: '0 */4 * * *'  # Every 4 hours

    renovate:
        # -- Custom exiting global renovate config
        existingConfigFile: ''
        # See https://docs.renovatebot.com/self-hosted-configuration
        config: |
            # YOUR_VALUES
```

Toutes les options de configuration du chart Helm sont disponibles ici [https://github.com/renovatebot/helm-charts/blob/main/charts/renovate/values.yaml](https://github.com/renovatebot/helm-charts/blob/main/charts/renovate/values.yaml).  
Pour la configuration de renovate, toutes les options sont disponibles ici [https://docs.renovatebot.com/configuration-options/](https://docs.renovatebot.com/configuration-options/).

3. Configurer le manifest

Mettre à jour les valeurs du [manisfest.yaml](argocd/renovatebot/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `trargetRevision`.

**Bases de données**

La Suite Donnée déploie deux clusters de base de données:
- un cluster dédié aux configurations des applications
- un cluster dédié à l'hébergement des données.

Si vous souhaitez installer les clusters, renseigner `LSD_INSTALL_DATABASES=true` dans votre fichier [.env](.env#26).

1. Configurer les secrets

Cluster de configuration: mettre à jour les valeurs du secret dans [db-config-secret.yaml](argocd/postgres/config/templates/db-config-secret.yaml).  
Cluster de données: mettre à jour les valeurs du secret dans [db-data-secret.yaml](argocd/postgres/data/templates/db-data-secret.yaml).

2. Configurer les values

Cluster de configuration: Mettre à jour les valeurs de [values-prod.yaml](argocd/postgres/config/values-prod.yaml).  
Cluster de données: Mettre à jour les valeurs de [values-prod.yaml](argocd/postgres/data/values-prod.yaml).

Il n'y a pas de valeurs particulières nécessaires à mettre à jour.

Toutes les options de configuration du Helm chart sont disponibles ici [https://github.com/bitnami/charts/blob/main/bitnami/postgresql/values.yaml](https://github.com/bitnami/charts/blob/main/bitnami/postgresql/values.yaml)

3. Configurer le manifest

Cluster de configuration: mettre à jour les valeurs du [manisfest.yaml](argocd/renovatebot/manifest.yaml).  
Cluster de données: mettre à jour les valeurs du [manisfest.yaml](argocd/renovatebot/manifest.yaml).

Notamment les valeurs du `namespace`, `repoURL` et `trargetRevision`.

**Initialiser les bases de données**

1. Configurer les values

Mettre à jour les valeurs de [main.yaml](ansible/roles/apps/init-db/vars/main.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:
```yaml
auth:
    host: db-config-prod-postgresql
    port: 5432
    name: defaultdb
    user: postgres          # Admin
    password: config_admin  # Défini dans le secret db-X-secret.yaml
```

2. Configurer les fichier SQL

Vous pouvez compléter les fichiers SQL pour créer des roles particuliers.  
Trois templates sont disponibles:
- [airflow.sql.jinja](ansible/roles/apps/init-db/templates/airflow.sql.jinja)
- [superset.sql.jinja](ansible/roles/apps/init-db/templates/superset.sql.jinja)
- [data-store.sql.jinja](ansible/roles/apps/init-db/templates/data-store.sql.jinja)


**Apache Superset**

1. Configurer le secret

Mettre à jour les valeurs du secret dans [superset-secret.yaml](argocd/superset/templates/superset-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/superset/values-prod.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:
```yaml
superset:
    # Ingress configuration
    ingress:
        # YOUR_VALUES

  init:
    adminUser:
        # YOUR_VALUES

  supersetNode:
    connections:
        # YOUR_VALUES
        # Doit correspondre aux identifiants de l'admin superset créé dans l'étape précédente
```

Toutes les options de configuration du Helm chart sont disponibles ici [https://github.com/apache/superset/blob/master/helm/superset/values.yaml](https://github.com/apache/superset/blob/master/helm/superset/values.yaml).

3. Configurer la configuration de Superset

Mettre à jour le fichier [superset_config_override.py](argocd/superset/superset_config_override.py).

4. Configurer le manifest

Mettre à jour les valeurs du [manisfest.yaml](argocd/superset/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `trargetRevision`.

**Apache Airflow**

1. Configurer le secret

Mettre à jour les valeurs du secret dans [airflow-secret.yaml](argocd/airflow/templates/airflow-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/airflow/values-prod.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:
```yaml
airflow:
    # Ingress configuration
    ingress:
        # YOUR_VALUES

    # Airflow database & redis config
    data:
        # Otherwise pass connection values in
        metadataConnection:
        # YOUR_VALUES

    # Airflow webserver settings
    webserver:
        enabled: false

        # Create initial user.
        defaultUser:
            # YOUR_VALUES
```

Toutes les options de configuration du Helm chart sont disponibles ici [https://github.com/apache/airflow/blob/main/chart/values.yaml](https://github.com/apache/airflow/blob/main/chart/values.yaml)

3. Configurer le manifest

Mettre à jour les valeurs du [manisfest.yaml](argocd/airflow/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `trargetRevision`.

**Apache Polaris**

_a venir_

**Trino**

_a venir_

### Exécution de l'installation

Une fois toutes les configurations précédentes terminées, il est nécessaire de push votre code via `git push`.  
Dans chaque manifeste, les paramètres `repoURL` et `targetRevision` doivent correspondre au repo qui contient votre code.  

Exécuter la commande suivante pour lancer l'installation

```bash
bash install.sh
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

### Pré-requis GitHub Actions

Un secret `GH_TOKEN` doit être configuré dans le repository GitHub avec les permissions `contents: write`, `issues: write` et `pull-requests: write`.

## Commandes disponibles

Quelques commandes utiles

| Commande              | Description                                      |
|-----------------------|--------------------------------------------------|
| `make setup-dev-env`  | Configure l'environnement de developpement       |
| `make test`           | Lance les tests pytest                           |
| `make clean`          | Supprime les fichiers temporaires                |
