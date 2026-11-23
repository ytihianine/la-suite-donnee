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
      - [TL;DR](#tldr)
      - [Configuration de l'environnement](#configuration-de-lenvironnement)
      - [Configuration des applications](#configuration-des-applications)
    - [Exécution de l'installation](#exécution-de-linstallation)
  - [Commandes disponibles](#commandes-disponibles)
  - [Guides complémentaires](#guides-complémentaires)

## Pré-requis

- Kubernetes*
- `kubectl`
- `helm` (pour les installations Helm, y compris ArgoCD)
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
├── ansible/        # Playbooks, rôles et variables d'installation
│    ├── playbooks/
│    ├── roles/
│    └── vars/install.yaml
├── charts/         # Helm charts & Manifestes d'application ArgoCD
├── images/         # Dockerfile & build des images personnalisées
├── scripts/        # Scripts utilitaires
├── docs/           # Documentation complementaire
└── install.py      # Orchestrateur d'installation interactif
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
# Pour vérifier
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

#### TL;DR

1. Configurer l'environnement python

```bash
make setup-dev-env
source env/bin/activate
```

2. Configurer les playbooks Ansible

Les playbooks Ansible sont situés dans le dossier `ansible/`.  
Les fichiers `ansible/**/vars/main.yaml` sont à adapter. Ils permettent de configurer les différentes applications (ArgoCD, initialisation de la base de données et de gérer d'autres composants nécessaires à la suite de données).  
Le fichier [install.yaml](ansible/vars/install.yaml) contient les étapes d'exécutions.

3. Configurer les manifests ArgoCD

Les manifests ArgoCD sont situés dans le dossier `argocd/`.
Il s'agit des fichiers de configuration des applications ArgoCD qui seront déployées dans le namespace.

4. Lancer l'installation

```bash
make install-la-suite-donnee
```

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

Les manifests des applications se situent dans `charts/`.

**Choisir les applications à installer**

Les étapes sont définies dans le fichier de variables Ansible [install.yaml](ansible/vars/install.yaml). Renseignez `enable: true` pour activer une étape et conservez l'ordre des dépendances.

Choisissez `deployment_method: argocd` pour appliquer les manifests Application, ou `deployment_method: helm` pour installer directement les charts locaux avec leurs fichiers `values-prod.yaml`. Configurez `app_namespace` pour Helm et les manifests Kubernetes, et `argocd_namespace` pour les Applications ArgoCD. Ces namespaces doivent déjà exister. Pour ArgoCD, configurez aussi le namespace de destination, le dépôt et la révision dans chaque manifest Application.

Les étapes avec `wait: true` attendent que le chart soit prêt en mode Helm ou que l'Application soit `Healthy` et `Synced` en mode ArgoCD avant de continuer. Les étapes spéciales utilisent directement le playbook indiqué par `playbook`. Par exemple :

```yaml
deployment_method: argocd
app_namespace: projet-dsci
argocd_namespace: projet-dsci
install_steps:
  - name: db-config
    description: "Déployer la base de données (app config) Postgres"
    enable: false
    chart: charts/postgres/config
    manifest: charts/postgres/config/manifest.yaml
    release_name: db-config-prod
    wait: true
```

Pour un opérateur ou une autre ressource sans chart Helm, ajoutez une étape à l'endroit approprié dans `install_steps` :

```yaml
  - name: mon-operateur
    description: "Déployer l'opérateur"
    enable: false
    playbook: ansible/playbooks/deploy-manifest.yaml
    manifest: chemin/vers/operateur.yaml
```

Le manifest peut contenir plusieurs documents Kubernetes. Les ressources cluster nécessitent les droits correspondants. Si l'opérateur nécessite une attente de disponibilité ou des étapes supplémentaires, utilisez un playbook dédié dans `playbook`.

**ArgoCD**

L'installation d'ArgoCD est réalisée via un playbook Ansible qui déploie le chart Helm `argo-cd`.  
Pour l'installer, renseignez `enable: true` pour l'étape `argocd` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer les variables

Mettre à jour les valeurs de [main.yaml](ansible/roles/apps/argocd/vars/main.yaml).  
A minima, il est nécessaire de renseigner le `namespace` cible.

2. Configurer les values

Mettre à jour le template [values.yaml.jinja](ansible/roles/apps/argocd/templates/values.yaml.jinja).  
Toutes les options de configuration du chart Helm sont disponibles ici [https://github.com/argoproj/argo-helm/blob/main/charts/argo-cd/values.yaml](https://github.com/argoproj/argo-helm/blob/main/charts/argo-cd/values.yaml).

**ArgoCD CLI**

Si vous souhaitez installer la CLI d'ArgoCD, renseignez `enable: true` pour l'étape `argocd-cli` dans votre fichier [install.yaml](ansible/vars/install.yaml).
Le playbook télécharge la dernière version de la CLI et l'installe dans `/usr/local/bin` (droits d'admin requis).

**Ajouter des dépôts à ArgoCD**

Si vous souhaitez enregistrer des dépôts Git dans ArgoCD, renseignez `enable: true` pour l'étape `argocd-add-repo` dans votre fichier [install.yaml](ansible/vars/install.yaml).

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

Si vous souhaitez installer Renovatebot, renseignez `enable: true` pour l'étape `renovatebot` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [renovatebot-secret.yaml](charts/renovatebot/templates/renovatebot-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](charts/renovatebot/values-prod.yaml).  
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

Mettre à jour les valeurs du [manifest.yaml](charts/renovatebot/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Bases de données**

La Suite Donnée déploie deux clusters de base de données:
- un cluster dédié aux configurations des applications
- un cluster dédié à l'hébergement des données.

Les clusters sont gérés par CloudNativePG. L'opérateur doit déjà être installé par un administrateur du cluster; le chart de l'opérateur dans [charts/postgres/operator](charts/postgres/operator/Chart.yaml) n'est pas activé par l'installateur. Si vous souhaitez créer les clusters, renseignez `enable: true` pour les étapes `db-config` et `db-data` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer les secrets

Cluster de configuration: mettre à jour les identifiants des secrets dans [db-config-secret.yaml](charts/postgres/config/templates/db-config-secret.yaml).
Cluster de données: mettre à jour les identifiants des secrets dans [db-data-secret.yaml](charts/postgres/data/templates/db-data-secret.yaml).

2. Configurer les values

Cluster de configuration: Mettre à jour les valeurs de [values-prod.yaml](charts/postgres/config/values-prod.yaml).  
Cluster de données: Mettre à jour les valeurs de [values-prod.yaml](charts/postgres/data/values-prod.yaml).

Les valeurs définissent le nom, les ressources, le stockage et la version de PostgreSQL de chaque cluster. Le service d'écriture CNPG est exposé sous le nom `<nom-du-cluster>-rw`.

3. Configurer le manifest

Cluster de configuration: mettre à jour les valeurs du [manifest.yaml](charts/postgres/config/manifest.yaml).  
Cluster de données: mettre à jour les valeurs du [manifest.yaml](charts/postgres/data/manifest.yaml).

Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

> ⚠️ Les charts CNPG créent de nouveaux clusters et ne réutilisent pas les PVC Bitnami. Sauvegardez puis restaurez les données vers CNPG avant de basculer les applications; conservez les anciens charts sous [charts/postgres/legacy](charts/postgres/legacy) jusqu'à validation de la migration.

**Initialiser les bases de données**

Les bases et rôles applicatifs sont déclarés dans les valeurs des charts CNPG. L'étape Ansible historique `init-postgres-db` reste désactivée car elle exécute les anciens templates SQL, dont le trigger d'événement n'est pas repris dans la configuration CNPG.
1. Configurer les values

Mettre à jour les valeurs de [main.yaml](ansible/roles/apps/init-db/vars/main.yaml).  
A minima, il est nécessaire de modifier les sections suivantes:
```yaml
auth:
    host: db-config-prod-rw
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

Si vous souhaitez installer Superset, renseignez `enable: true` pour l'étape `superset` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [superset-secret.yaml](charts/superset/templates/superset-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](charts/superset/values-prod.yaml).  
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

Mettre à jour le fichier [superset_config_override.py](charts/superset/superset_config_override.py).

4. Configurer le manifest

Mettre à jour les valeurs du [manifest.yaml](charts/superset/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Apache Airflow**

Si vous souhaitez installer Airflow, renseignez `enable: true` pour l'étape `airflow` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [airflow-custom-secret.yaml](charts/airflow/templates/airflow-custom-secret.yaml).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](charts/airflow/values-prod.yaml).  
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

Mettre à jour les valeurs du [manifest.yaml](charts/airflow/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Apache Polaris**

Si vous souhaitez installer Polaris, renseignez `enable: true` pour l'étape `polaris` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer le secret

Mettre à jour les valeurs du secret dans [polaris-secret.yaml](charts/polaris/templates/polaris-secret.yaml).  
Ce secret contient les identifiants de la base de données (`DB_USER`, `DB_PASSWORD`, `DB_JDBC_URL`) et les identifiants du stockage objet (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

2. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](charts/polaris/values-prod.yaml).  
A minima, il est nécessaire de modifier l'ingress et la persistance (`persistence.relationalJdbc` doit pointer vers le secret configuré à l'étape précédente).

3. Configurer le manifest

Mettre à jour les valeurs du [manifest.yaml](charts/polaris/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

**Trino**

Si vous souhaitez installer Trino, renseignez `enable: true` pour l'étape `trino` dans votre fichier [install.yaml](ansible/vars/install.yaml).

1. Configurer les values

Mettre à jour les valeurs de [values-prod.yaml](charts/trino/values-prod.yaml).  
A minima, il est nécessaire de modifier l'ingress et les `catalogs` (par exemple le catalogue Iceberg REST pointant vers Polaris).

2. Configurer le manifest

Mettre à jour les valeurs du [manifest.yaml](charts/trino/manifest.yaml).  
Notamment les valeurs du `namespace`, `repoURL` et `targetRevision`.

### Exécution de l'installation

En mode ArgoCD, une fois la configuration terminée, poussez votre code via `git push`. Dans chaque manifeste, les paramètres `repoURL` et `targetRevision` doivent correspondre au dépôt qui contient votre code.

Exécutez la commande suivante pour lancer l'installation :

```bash
# Depuis la racine du projet
make install-la-suite-donnee
```

Le script [install.py](install.py) affiche les étapes de [install.yaml](ansible/vars/install.yaml) et demande confirmation avant de lancer les playbooks activés, dans l'ordre défini. Il lance une seule commande Ansible et demande une seule fois le mot de passe de privilèges, même lorsque plusieurs étapes sont activées. Aucune commande Ansible n'est lancée si toutes les étapes sont désactivées.

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
| `make build-trino`            | Build l'image Docker Trino personnalisée |
| `make build-superset`         | Build l'image Docker Superset personnalisée                  |
| `make build-airflow`          | Build l'image Docker Airflow personnalisée |
| `make build-polaris`          | Build l'image Docker Polaris personnalisée |

## Guides complémentaires

- [Installer l'environnement de développement](docs/guides/developpement.md)
