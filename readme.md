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
- `kubectl`
- Docker (pour le build des images personnalisées)
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
├── ansible/        # Playbooks & rôles Ansible (ArgoCD, init-db)
├── argocd/         # Manifestes d'application ArgoCD
├── images/         # Dockerfile & build des images personnalisées
├── scripts/        # Scripts utilitaires (lint / template helm)
├── tests/          # Tests unitaires (pytest)
├── docs/           # Documentation complementaire
├── install.py      # Orchestrateur d'installation interactif
└── install_options.yaml  # Étapes d'installation à activer / désactiver
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
git push
# cela revient à faire git push origin main
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

**1. Configurer l'environnement Python**

```bash
make setup-dev-env
source env/bin/activate
```

La commande `make setup-dev-env` exécute `create-py-env`, `install-py-packages` et `install-pre-commit`.

**2. Configurer Ansible**

La configuration d'Ansible est disponible dans le fichier [ansible.cfg](ansible.cfg).  
L'option `become_exe` est à ajuster selon votre environnement Unix (exemple ci-dessous).

```bash
# become_exe = sudo.ws
```

#### Configuration des applications

Les manifestes des applications se situent dans `argocd/`.

**Choisir les applications à installer**

Les applications déployées lors de l'installation sont définies dans le fichier [install_options.yaml](install_options.yaml).  
Chaque étape comporte un `name`, une `description`, la ou les commandes `cmd` à exécuter, et le flag `enable` à renseigner à `true` pour activer le déploiement de l'application.

L'ordre des étapes est important : il respecte les dépendances entre les applications.  
Pour certaines étapes, le paramètre `wait_app` fait attendre que l'application ArgoCD correspondante soit `Healthy` et `Synced` avant de poursuivre :

```yaml
steps:
  - name: argocd
    description: "Déployer ArgoCD dans le namespace"
    enable: false
    cmd:
      - "make deploy-argocd"
  # ...
  - name: db-config
    description: "Déployer la base de données (app config) Postgres"
    enable: false
    cmd:
      - "kubectl apply -f argocd/postgres/config/manifest.yaml"
    wait_app: db-config-prod
  # ...
```

**ArgoCD**

L'installation d'ArgoCD est réalisée via un playbook Ansible qui déploie le chart Helm `argo-cd`.  
Pour l'installer, renseignez `enable: true` pour l'étape `argocd` dans votre fichier [install_options.yaml](install_options.yaml).

1. Configurer les variables

Mettre à jour les valeurs de [main.yaml](ansible/roles/apps/argocd/vars/main.yaml).  
A minima, il est nécessaire de renseigner le `namespace` cible.

2. Configurer les values

Mettre à jour le template [values.yaml.jinja](ansible/roles/apps/argocd/templates/values.yaml.jinja).  
Toutes les options de configuration du chart Helm sont disponibles ici [https://github.com/argoproj/argo-helm/blob/main/charts/argo-cd/values.yaml](https://github.com/argoproj/argo-helm/blob/main/charts/argo-cd/values.yaml).

**ArgoCD CLI**

Si vous souhaitez installer la CLI d'ArgoCD, renseignez `enable: true` pour l'étape `argocd-cli` dans votre fichier [install_options.yaml](install_options.yaml).  
Le playbook télécharge la dernière version de la CLI et l'installe dans `/usr/local/bin` (droits d'admin requis).

**Ajouter des dépôts à ArgoCD**

Si vous souhaitez enregistrer des dépôts Git dans ArgoCD, renseignez `enable: true` pour l'étape `argocd-add-repo` dans votre fichier [install_options.yaml](install_options.yaml).

Mettre à jour la liste des dépôts dans [main.yaml](ansible/roles/apps/argocd-add-repo/vars/main.yaml) :

```yaml
# Template
repo:
  - url: ""
    name: ""
    project: ""
    username: ""
    password: ""
    proxy: "" # Laisser vide si pas de proxy
    no_proxy: ""
```

**Renovatebot**

Si vous souhaitez installer Renovatebot, renseignez `enable: true` pour l'étape `renovatebot` dans votre fichier [install_options.yaml](install_options.yaml).

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

Si vous souhaitez installer les clusters, renseignez `enable: true` pour les étapes `db-config` et `db-data` dans votre fichier [install_options.yaml](install_options.yaml).

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

Si vous souhaitez initialiser les bases de données, renseignez `enable: true` pour l'étape `init-postgres-db` dans votre fichier [install_options.yaml](install_options.yaml).

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

Si vous souhaitez installer Superset, renseignez `enable: true` pour l'étape `superset` dans votre fichier [install_options.yaml](install_options.yaml).

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

Si vous souhaitez installer Airflow, renseignez `enable: true` pour l'étape `airflow` dans votre fichier [install_options.yaml](install_options.yaml).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [airflow-custom-secret.yaml](argocd/airflow/templates/airflow-custom-secret.yaml).

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

Si vous souhaitez installer Polaris, renseignez `enable: true` pour l'étape `polaris` dans votre fichier [install_options.yaml](install_options.yaml).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [polaris-secret.yaml](argocd/polaris/templates/polaris-secret.yaml).  
Ce secret contient les identifiants de la base de données (`DB_USER`, `DB_PASSWORD`, `DB_JDBC_URL`) et les identifiants du stockage objet (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/polaris/values-prod.yaml).  
A minima, il est nécessaire de modifier l'ingress et la persistance (`persistence.relationalJdbc` doit pointer vers le secret configuré à l'étape précédente).

3. Configurer le manifest

Mettre à jour les valeurs du [manifest.yaml](argocd/polaris/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Trino**

Si vous souhaitez installer Trino, renseignez `enable: true` pour l'étape `trino` dans votre fichier [install_options.yaml](install_options.yaml).

1. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](argocd/trino/values-prod.yaml).  
A minima, il est nécessaire de modifier l'ingress et les `catalogs` (par exemple le catalogue Iceberg REST pointant vers Polaris).

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

Le script [install.py](install.py) affiche la liste des étapes de [install_options.yaml](install_options.yaml) (nom, description et état activée/désactivée) et vous demande de confirmer avant de lancer le déploiement des applications activées, dans l'ordre défini.

## Commandes disponibles

Quelques commandes utiles :

| Commande                      | Description                                                  |
|-------------------------------|--------------------------------------------------------------|
| `make setup-dev-env`          | Configure l'environnement de développement                   |
| `make run-pre-commit`         | Exécute pre-commit sur tous les fichiers                     |
| `make test`                   | Lance les tests pytest                                       |
| `make clean`                  | Supprime les fichiers temporaires                            |
| `make install-la-suite-donnee`| Lance l'installation orchestrée de la suite                  |
| `make deploy-argocd` / `deploy-argocd-cli` / `deploy-argocd-add-repo` | Déploie ArgoCD / sa CLI / ajoute des dépôts dans ArgoCD (via Ansible) |
| `make init-databases`         | Initialise les bases de données (via Ansible)                |
| `make build-trino`            | Build l'image Docker Trino personnalisée (argument `TRINO_VERSION`) |
| `make build-superset`         | Build l'image Docker Superset personnalisée                  |
| `make build-airflow`          | Build l'image Docker Airflow personnalisée (argument `AIRFLOW_VERSION`) |
| `make build-polaris`          | Build l'image Docker Polaris personnalisée (argument `POLARIS_VERSION`) |

## Guides complémentaires

- [Installer l'environnement de développement](docs/guides/developpement.md)
