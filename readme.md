# La Suite Donnée

La Suite Donnée est un ensemble d'outils qui permettent de faire du traitement de données bout en bout (récolte, traitement, documentation, dataviz ...).
Ce dépôt est un guide d'installation de l'ensemble des outils qui composent la Suite Donnée.

## Table des matières

- [La Suite Donnée](#la-suite-donnée)
  - [Table des matières](#table-des-matières)
  - [Pré-requis](#pré-requis)
  - [Structure](#structure)
  - [Installation du projet](#installation-du-projet)
    - [Initialiser le dépôt](#initialiser-le-dépôt)
    - [Configuration de l'installation](#configuration-de-linstallation)
      - [Configuration de l'environnement](#configuration-de-lenvironnement)
      - [Configuration des applications](#configuration-des-applications)
    - [Exécution de l'installation](#exécution-de-linstallation)
  - [Commandes disponibles](#commandes-disponibles)
  - [Guides complémentaires](#guides-complémentaires)

## Pré-requis

- Kubernetes*
- Python 3.12+
- Node.js 24+ (optionnel, uniquement pour la CI git)
- `make`

*Seul un accès à un namespace est nécessaire. Certaines ressources nécessiteront des droits d'admin du cluster.

## Structure

```
.
├── .github/
│    ├── workflows: workflows github
│    └── skills: skills copilot
├── ansible/                # Playbooks Ansible
├── argocd/                 # ArgoCD application manifests
├── images/                 # Dockerfile & build
├── tests/                  # Tests unitaires (pytest)
├── docs/                   # Documentation complementaire
├── install.py              # Orchestrateur d'installation
└── install_options.json    # Options d'installation (quelles applications déployer)
```

## Installation du projet

### Initialiser le dépôt
1. Créer et cloner votre dépôt

* Créez un nouveau dépôt Git privé vide.
* Clonez-le sur votre machine puis placez-vous dans le dossier du projet :

```bash
git clone votre_depot/
cd votre_depot/
```

2. Ajouter le dépôt source (upstream)

Ajoutez le dépôt de référence comme dépôt *upstream* :

```bash
git remote add upstream https://github.com/ytihianine/la-suite-donnee.git
```

Vérifiez que l'ajout est correct :

```bash
git remote -v
```

3. Récupérer le projet

Importez le contenu du dépôt source :

```bash
git pull upstream main
```

4. Publier sur votre dépôt

Envoyez le code sur votre dépôt :

```bash
git push origin main
```

5. Mettre à jour ultérieurement

Pour récupérer les dernières modifications du dépôt source :

```bash
git pull upstream main
```

> L'opération met à jour le code du projet sans modifier votre configuration personnelle.  
> Si vous venez de cloner de nouveau votre dépôt, il faudra répéter les étapes à partir de la 2ème



### Configuration de l'installation

#### Configuration de l'environnement

**1. Dupliquer les variables d'environnement**

```bash
make duplicate-env-vars
```

Configurez les variables d'environnement dans le fichier `.env` en fonction de votre environnement.

**2. Configurer l'environnement Python**

```bash
make setup-dev-env
source env/bin/activate
```

La commande `make setup-dev-env` exécute `create-py-env`, `install-py-packages` et `install-pre-commit`.

**3. Configurer Ansible**

La configuration d'Ansible est disponible dans le fichier [ansible.cfg](ansible.cfg).  
L'option `become_exe` est à ajuster selon votre environnement linux (exemple ci-dessous).

```bash
# become_exe = sudo.ws
```

#### Configuration des applications

Les manifestes des applications se situent dans `argocd/`.

Les options d'installation sont définies dans le fichier [install_options.json](install_options.json).
Chaque application possède un ou plusieurs flags booléens qui déterminent si elle sera déployée par le script [install.py](install.py) :

```json
{
    "ARGOCD": {
        "DEPLOY_APP": false,
        "INSTALL_CLI": false,
        "ADD_REPO": false
    },
    "RENOVATEBOT": {
        "DEPLOY_APP": false
    },
    "DATABASES": {
        "DEPLOY_CONFIG_DB": false,
        "DEPLOY_DATA_DB": false,
        "INIT_DB": false
    },
    "SUPERSET": {
        "DEPLOY_APP": false
    },
    "AIRFLOW": {
        "DEPLOY_APP": false
    },
    "TRINO": {
        "DEPLOY_APP": false
    },
    "POLARIS": {
        "DEPLOY_APP": false
    }
}
```

Activez les flags souhaités (`true`) pour chaque application à déployer.
Le script `install.py` affiche un récapitulatif des options avant de lancer l'installation et demande une confirmation.

**ArgoCD**

Si vous souhaitez installer ArgoCD, activez `ARGOCD.DEPLOY_APP=true`.  
Si ArgoCD est déjà installé sur votre cluster, laissez `false`.

**ArgoCD CLI**

Si vous souhaitez installer la CLI d'ArgoCD, activez `ARGOCD.INSTALL_CLI=true`.  
Aucune configuration particulière complémentaire.

> **Prérequis** : le déploiement des bases de données (`DATABASES.DEPLOY_CONFIG_DB` ou `DATABASES.DEPLOY_DATA_DB`) et leur initialisation (`DATABASES.INIT_DB`) nécessitent `ARGOCD.INSTALL_CLI=true`, car le script attend la synchronisation des applications via la commande `argocd app wait`.

**Renovatebot**

Si vous souhaitez installer Renovatebot, activez `RENOVATEBOT.DEPLOY_APP=true`.

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

Mettre à jour les valeurs du [manifest.yaml](argocd/renovatebot/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Bases de données**

La Suite Donnée déploie deux clusters de base de données:
- un cluster dédié aux configurations des applications
- un cluster dédié à l'hébergement des données.

Si vous souhaitez installer les clusters, activez `DATABASES.DEPLOY_CONFIG_DB=true` et/ou `DATABASES.DEPLOY_DATA_DB=true`.

1. Configurer les secrets

Cluster de configuration: mettre à jour les valeurs du secret dans [db-config-secret.yaml](argocd/postgres/config/templates/db-config-secret.yaml).  
Cluster de données: mettre à jour les valeurs du secret dans [db-data-secret.yaml](argocd/postgres/data/templates/db-data-secret.yaml).

2. Configurer les values

Cluster de configuration: Mettre à jour les valeurs de [values-prod.yaml](argocd/postgres/config/values-prod.yaml).  
Cluster de données: Mettre à jour les valeurs de [values-prod.yaml](argocd/postgres/data/values-prod.yaml).

Il n'y a pas de valeurs particulières nécessaires à mettre à jour.

Toutes les options de configuration du Helm chart sont disponibles ici [https://github.com/bitnami/charts/blob/main/bitnami/postgresql/values.yaml](https://github.com/bitnami/charts/blob/main/bitnami/postgresql/values.yaml)

3. Configurer le manifest

Cluster de configuration: mettre à jour les valeurs du [manifest.yaml](argocd/postgres/config/manifest.yaml).  
Cluster de données: mettre à jour les valeurs du [manifest.yaml](argocd/postgres/data/manifest.yaml).

Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

> ⚠️ Attention ⚠️  
> Si vos bases de données ont déjà été déployées ou si vous souhaitez changer le mot de passe de l'administrateur `postgres`, il est nécessaire de **supprimer les PVC** associés aux bases de données.  
> Sauvegardez vos données avant toute manipulation.

**Initialiser les bases de données**

> **Prérequis** : `DATABASES.INIT_DB=true` nécessite `DATABASES.DEPLOY_CONFIG_DB=true` (l'initialisation se connecte au cluster de configuration `db-config-prod-postgresql`).

Si vous souhaitez initialiser les bases de données, activez `DATABASES.INIT_DB=true`.

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

Mettre à jour les valeurs du [manifest.yaml](argocd/superset/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

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

Mettre à jour les valeurs du [manifest.yaml](argocd/airflow/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Apache Polaris**

Si vous souhaitez installer Apache Polaris, activez `POLARIS.DEPLOY_APP=true`.

1. Configurer le secret

Mettre à jour les valeurs du secret dans [polaris-secret.yaml](argocd/polaris/templates/polaris-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/polaris/values-prod.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:

```yaml
polaris:
    # Ingress configuration
    ingress:
        hosts:
            - host: polaris.lab.sspcloud.fr  # YOUR_VALUES

    persistence:
        relationalJdbc:
            secret:
                name: "polaris-secret"  # Doit correspondre au secret ci-dessus
```

Toutes les options de configuration du Helm chart sont disponibles ici [https://polaris.apache.org/in-dev/unreleased/helm-chart/](https://polaris.apache.org/in-dev/unreleased/helm-chart/).

3. Configurer le manifest

Mettre à jour les valeurs du [manifest.yaml](argocd/polaris/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Trino**

Si vous souhaitez installer Trino, activez `TRINO.DEPLOY_APP=true`.

1. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/trino/values-prod.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:

```yaml
trino:
    # Ingress configuration
    ingress:
        hosts:
            - host: trino.lab.sspcloud.fr  # YOUR_VALUES

    # Catalogs (config des connexions aux données)
    catalogs:
        data_store: |
            # YOUR_VALUES
```

Toutes les options de configuration du Helm chart sont disponibles ici [https://github.com/trinodb/charts/blob/main/charts/trino/values.yaml](https://github.com/trinodb/charts/blob/main/charts/trino/values.yaml).

2. Configurer le manifest

Mettre à jour les valeurs du [manifest.yaml](argocd/trino/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

### Exécution de l'installation

Une fois toutes les configurations précédentes terminées, poussez votre code via `git push`.  
Dans chaque manifeste, les paramètres `repoURL` et `targetRevision` doivent correspondre au repo qui contient votre code.  

Exécutez la commande suivante pour lancer l'installation :

```bash
# Depuis la racine du projet
make install-la-suite-donnee
```

## Commandes disponibles

Quelques commandes utiles :

| Commande                          | Description                                      |
|-----------------------------------|--------------------------------------------------|
| `make setup-dev-env`              | Configure l'environnement de développement       |
| `make run-pre-commit`             | Exécute pre-commit sur tous les fichiers         |
| `make test`                       | Lance les tests pytest                           |
| `make install-la-suite-donnee`    | Lance l'installation complète (install.py)       |
| `make build-trino`                | Build l'image Docker Trino personnalisée         |
| `make build-superset`             | Build l'image Docker Superset personnalisée      |
| `make build-airflow`              | Build l'image Docker Airflow personnalisée       |
| `make build-polaris`              | Build l'image Docker Polaris personnalisée       |
| `make deploy-all`                 | Déploie toutes les applications sur le cluster   |
| `make clean`                      | Supprime les fichiers temporaires                |

## Guides complémentaires

- [Installer l'environnement de développement](docs/guides/developpement.md)
