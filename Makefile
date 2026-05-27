# Variables
PYTHON_VERSION=3.12
AIRFLOW_VERSION=3.1.8
ENV_NAME = env
TRINO_VERSION ?= 481
POLARIS_VERSION ?= 1.5.0
SUPERSET_VERSION ?= 6.0.0

# OS detection
ifeq ($(OS),Windows_NT)
    PYTHON := python
    VENV_BIN := $(ENV_NAME)/Scripts
else
    PYTHON := python3
    VENV_BIN := $(ENV_NAME)/bin
endif

.PHONY: create-py-env clean install-py-packages install-pre-commit test build-trino

create-py-env: ## Créer un nouvel environnement python
	@echo "Création d'un environnement"
	$(PYTHON) -m venv $(ENV_NAME)
	@echo "L'environnement a été créé"
	@echo "Activation du nouvel environnement"
	@echo "Exécuter dans votre terminal: source $(ENV_NAME)/bin/activate"


install-py-packages: ## Installer les packages python
	@echo "Installation/Mise à jour de pip"
	$(VENV_BIN)/python -m pip install --upgrade pip
	@echo "Installation de uv"
	$(VENV_BIN)/python -m pip install uv
	$(VENV_BIN)/uv pip install --python $(VENV_BIN)/python -r requirements.txt


install-pre-commit: ## Installer pre-commit
	$(VENV_BIN)/pre-commit install

setup-dev-env: create-py-env install-py-packages install-pre-commit ## Configurer l'environnement de développement

test: ## Lancer les tests pytest
	$(VENV_BIN)/python -m pytest tests/

run-pre-commit: ## Lancer pre-commit sur tous les fichiers
	$(VENV_BIN)/pre-commit run --all-files

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

clean: ## Nettoie les fichiers temporaires
	@echo "Nettoyage des fichiers temporaires"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Nettoyage terminé"
