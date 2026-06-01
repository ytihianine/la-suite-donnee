# Charger les variables d'environnement depuis le fichier .env
-include .env

# OS detection
ifeq ($(OS),Windows_NT)
    PYTHON := python
    VENV_BIN := $(ENV_NAME)/Scripts
else
    PYTHON := python3
    VENV_BIN := $(ENV_NAME)/bin
endif

# Couleurs pour les messages
Color_Off='\033[0m'
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m

.PHONY: create-py-env clean install-py-packages install-pre-commit test build-trino

create-py-env: ## Créer un nouvel environnement python
	@echo "Création d'un environnement"
	$(PYTHON) -m venv $(ENV_NAME)
	@echo "$(GREEN)L'environnement a été créé$(Color_Off)"
	@echo "Activation du nouvel environnement"
	@echo "$(YELLOW)Exécuter dans votre terminal: source $(ENV_NAME)/bin/activate$(Color_Off)"

# =====================================================================
# Environnement de développement Python
# =====================================================================
duplicate-env-vars: ## Dupliquer les variables d'environnement du système dans le nouvel environnement virtuel
	@echo "Création du fichier .env à partir du template .env.example"
	cp .env.example .env
	@echo "$(GREEN)Les variables d'environnement ont été dupliquées dans le fichier .env$(Color_Off)"

install-py-packages: ## Installer les packages python
	@echo "Installation/Mise à jour de pip"
	$(VENV_BIN)/python -m pip install --upgrade pip
	@echo "Installation de uv"
	$(VENV_BIN)/python -m pip install uv
	$(VENV_BIN)/uv pip install --python $(VENV_BIN)/python -r requirements.txt
	@echo "$(GREEN)Les packages python ont été installés avec succès$(Color_Off)"

install-pre-commit: ## Installer pre-commit
	$(VENV_BIN)/pre-commit install

setup-dev-env: create-py-env install-py-packages install-pre-commit ## Configurer l'environnement de développement

test: ## Lancer les tests pytest
	$(VENV_BIN)/python -m pytest tests/

run-pre-commit: ## Lancer pre-commit sur tous les fichiers
	$(VENV_BIN)/pre-commit run --all-files

# =====================================================================
# Build les images Docker personnalisées des applications
# =====================================================================
build-trino: ## Build the custom Trino Docker image locally (TRINO_VERSION=481)
	docker build -f images/trino/Dockerfile \
		--no-cache \
		--build-arg TRINO_VERSION=$(TRINO_VERSION) \
		-t trino-custom:$(TRINO_VERSION) .

build-superset: ## Build the custom Superset Docker image locally (SUPERSET_VERSION=6.0.0)
	docker build -f images/superset/Dockerfile \
		--no-cache \
		--build-arg SUPERSET_VERSION=$(SUPERSET_VERSION) \
		-t superset-custom:$(SUPERSET_VERSION) .

build-polaris: ## Build the custom Polaris Docker image locally (POLARIS_VERSION=1.5.0)
	docker build -f images/polaris/Dockerfile \
		--no-cache \
		--build-arg POLARIS_VERSION=$(POLARIS_VERSION) \
		-t polaris-custom:$(POLARIS_VERSION) .

# =====================================================================
# Déployer les applications sur le cluster Kubernetes
# =====================================================================

deploy-argocd: ## Déployer ArgoCD sur le cluster Kubernetes
	@echo "Déploiement d'ArgoCD sur le cluster Kubernetes"
	$(VENV_BIN)/ansible-playbook -i localhost ansible/playbooks/argocd.yaml
	@echo "$(GREEN)ArgoCD a été déployé avec succès$(Color_Off)"

deploy-argocd-cli: ## Déployer ArgoCD CLI sur le cluster Kubernetes
	@echo "Déploiement d'ArgoCD CLI sur le cluster Kubernetes"
	$(VENV_BIN)/ansible-playbook -i localhost ansible/playbooks/argocd-cli.yaml
	@echo "$(GREEN)ArgoCD CLI a été déployé avec succès$(Color_Off)"

connect-argocd: ## Se connecter à ArgoCD CLI
	@echo "Connexion à ArgoCD CLI"
	argocd login --core
	@echo "$(GREEN)Connexion à ArgoCD CLI réussie$(Color_Off)"

deploy-renovatebot: ## Déployer RenovateBot sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement de RenovateBot sur le cluster Kubernetes"
	kubectl apply -f argocd/renovatebot/manifest.yaml
	@echo "$(GREEN)RenovateBot a été déployé avec succès$(Color_Off)"

deploy-db-config: ## Déployer la configuration de la base de données sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement de la base de données de configuration sur le cluster Kubernetes"
	kubectl apply -f argocd/postgres/config/manifest.yaml
	@echo "$(GREEN)La base de données de configuration a été déployée avec succès$(Color_Off)"

deploy-db-data: ## Déployer la configuration de la base de données sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement de la base de données de configuration sur le cluster Kubernetes"
	kubectl apply -f argocd/postgres/data/manifest.yaml
	@echo "$(GREEN)La base de données de configuration a été déployée avec succès$(Color_Off)"

deploy-databases: deploy-db-config deploy-db-data ## Déployer la configuration et les données de la base de données sur le cluster Kubernetes à partir d'ArgoCD

init-databases: ## Initialiser la base de données de configuration
	@echo "Initialisation de la base de données de configuration"
	$(VENV_BIN)/ansible-playbook -i localhost ansible/playbooks/init-db.yaml
	@echo "$(GREEN)La base de données de configuration a été initialisée avec succès$(Color_Off)"

deploy-trino: ## Déployer Trino sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement de Trino sur le cluster Kubernetes"
	kubectl apply -f argocd/trino/manifest.yaml
	@echo "$(GREEN)Trino a été déployé avec succès$(Color_Off)"

deploy-superset: ## Déployer Superset sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement de Superset sur le cluster Kubernetes"
	kubectl apply -f argocd/superset/manifest.yaml
	@echo "$(GREEN)Superset a été déployé avec succès$(Color_Off)"

deploy-airflow: ## Déployer Airflow sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement d'Airflow sur le cluster Kubernetes"
	kubectl apply -f argocd/airflow/manifest.yaml
	@echo "$(GREEN)Airflow a été déployé avec succès$(Color_Off)"

deploy-polaris: ## Déployer Polaris sur le cluster Kubernetes à partir d'ArgoCD
	@echo "Déploiement de Polaris sur le cluster Kubernetes"
	kubectl apply -f argocd/polaris/manifest.yaml
	@echo "$(GREEN)Polaris a été déployé avec succès$(Color_Off)"

# Need to add deploy-trino  deploy-polaris
deploy-all: deploy-renovatebot deploy-db-config deploy-db-data init-db deploy-superset deploy-airflow ## Déployer toutes les applications sur le cluster Kubernetes à partir d'ArgoCD

# =====================================================================
# Autres commandes utiles
# =====================================================================
clean: ## Nettoie les fichiers temporaires
	@echo "Nettoyage des fichiers temporaires"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "$(GREEN)✓ Nettoyage terminé$(Color_Off)"
