#!/bin/bash

# Script texte colors
# Reset
Color_Off='\033[0m'       # Text Reset

# Regular Colors
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow

# Load .env file variables into the script
set -a
source ".env"
set +a


# ==============================
# Helper functions
# ==============================
wait_for_argocd_app() {
    local app_name="$1"
    local timeout="${2:-300}"
    echo "Waiting for ArgoCD application '$app_name' to be Healthy and Synced (timeout: ${timeout}s)..."
    if ! argocd app wait "$app_name" --health --sync --timeout "$timeout"; then
        echo "ERROR: ArgoCD application '$app_name' did not become healthy within ${timeout}s. Aborting."
        exit 1
    fi
    echo -e "${Green}ArgoCD application '$app_name' is Healthy and Synced.${Color_Off}"
}

# ==============================
# User confirmation
# ==============================
echo "This script will install la Suite Donnée with the following installation options:"
echo -e "\t Install all components: $LSD_INSTALL_ALL"
echo -e "\t Install ArgoCD: $LSD_INSTALL_ARGOCD"
echo -e "\t Install ArgoCD CLI: $LSD_INSTALL_ARGOCD_CLI"
echo -e "\t Deploy Renovate Bot: $LSD_INSTALL_RENOVATE"
echo -e "\t Deploy databases: $LSD_INSTALL_DATABASES"
echo -e "\t Init databases: $LSD_INIT_DATABASES"
echo -e "\t Deploy Superset: $LSD_INSTALL_SUPERSET"
echo -e "\t Deploy Airflow: $LSD_INSTALL_AIRFLOW"
echo -e "\t Deploy Trino: $LSD_INSTALL_TRINO"
echo -e "\t Deploy Polaris: $LSD_INSTALL_POLARIS"
echo ""
echo "Do you wish to proceed the installation with your options? (Select with the number corresponding to your choice)"
select user_choice in "Yes" "No" "Cancel"; do
    case $user_choice in
        Yes ) choice="Yes"; break;;
        No ) choice="No"; break;;
        Cancel ) choice="Cancel"; break;;
        * ) echo "Invalid option. Please select 1, 2, or 3.";;
    esac
done

# ==============================
# Contrôle installation options
# ==============================
if [ "$choice" = "Yes" ]; then
    echo "Proceeding with the installation..."
elif [ "$choice" = "No" ]; then
    echo "Installation aborted by the user."
    exit 0
elif [ "$choice" = "Cancel" ]; then
    echo "Installation cancelled by the user."
    exit 0
else
    echo "Unexpected choice. Exiting."
    exit 1
fi

# ==============================
# Install la Suite Donnée
# ==============================
if [ "$LSD_INSTALL_ALL" = true ]; then
    ## Install la Suite Donnée - All in one
    echo "Install la Suite Donnée using the All-in-one command..."
    make deploy-all
else
    ## Install la Suite Donnée - step by step
    echo "Install la Suite Donnée using the step-by-step commands..."
    # Install ArgoCD
    if [ "$LSD_INSTALL_ARGOCD" = true ]; then
        echo "Installing ArgoCD..."
        make deploy-argocd
    else
        echo -e "${Yellow}LSD_INSTALL_ARGOCD is $LSD_INSTALL_ARGOCD. Skipping ArgoCD installation...${Color_Off}"
    fi

    # Install ArgoCD CLI
    if [ "$LSD_INSTALL_ARGOCD_CLI" = true ]; then
        echo "Installing ArgoCD CLI..."
        make deploy-argocd-cli
        make connect-argocd
    else
        echo -e "${Yellow}LSD_INSTALL_ARGOCD_CLI is $LSD_INSTALL_ARGOCD_CLI. Skipping ArgoCD CLI installation...${Color_Off}"
    fi

    # Deploy renovate bot
    if [ "$LSD_INSTALL_RENOVATE" = true ]; then
        echo "Deploying Renovate Bot..."
        make deploy-renovatebot
    else
        echo -e "${Yellow}LSD_INSTALL_RENOVATE is $LSD_INSTALL_RENOVATE. Skipping Renovate Bot deployment...${Color_Off}"
    fi

    # Deploy databases
    if [ "$LSD_INSTALL_DATABASES" = true ]; then
        echo "Deploying databases..."
        # App config database
        if [ "$LSD_INSTALL_CONFIG_DB" = true ]; then
            make deploy-db-config
            echo "Waiting for config database to be ready..."
            wait_for_argocd_app "db-config-prod"
        else
            echo -e "${Yellow}LSD_INSTALL_CONFIG_DB is $LSD_INSTALL_CONFIG_DB. Skipping config database deployment...${Color_Off}"
        fi
        # App data database
        if [ "$LSD_INSTALL_DATA_DB" = true ]; then
            make deploy-db-data
            echo "Waiting for data database to be ready..."
            wait_for_argocd_app "db-data-prod"
        else
            echo -e "${Yellow}LSD_INSTALL_DATA_DB is $LSD_INSTALL_DATA_DB. Skipping data database deployment...${Color_Off}"
        fi
    else
        echo -e "${Yellow}LSD_INSTALL_DATABASES is $LSD_INSTALL_DATABASES. Skipping databases deployment...${Color_Off}"
    fi

    # Init databases
    if [ "$LSD_INIT_DATABASES" = true ]; then
        echo "Checking database apps health before initialization..."
        echo "Initializing databases..."
        make init-databases
    else
        echo -e "${Yellow}LSD_INIT_DATABASES is $LSD_INIT_DATABASES. Skipping databases initialization...${Color_Off}"
    fi

    # Deploy Superset
    if [ "$LSD_INSTALL_SUPERSET" = true ]; then
        echo "Deploying Superset..."
        make deploy-superset
    else
        echo -e "${Yellow}LSD_INSTALL_SUPERSET is $LSD_INSTALL_SUPERSET. Skipping Superset deployment...${Color_Off}"
    fi

    # Deploy Airflow
    if [ "$LSD_INSTALL_AIRFLOW" = true ]; then
        echo "Deploying Airflow..."
        make deploy-airflow
    else
        echo -e "${Yellow}LSD_INSTALL_AIRFLOW is $LSD_INSTALL_AIRFLOW. Skipping Airflow deployment...${Color_Off}"
    fi

    # Deploy Trino
    if [ "$LSD_INSTALL_TRINO" = true ]; then
        echo "Deploying Trino..."
        make deploy-trino
    else
        echo -e "${Yellow}LSD_INSTALL_TRINO is $LSD_INSTALL_TRINO. Skipping Trino deployment...${Color_Off}"
    fi

    # Deploy Polaris
    if [ "$LSD_INSTALL_POLARIS" = true ]; then
        echo "Deploying Polaris..."
        make deploy-polaris
    else
        echo -e "${Yellow}LSD_INSTALL_POLARIS is $LSD_INSTALL_POLARIS. Skipping Polaris deployment...${Color_Off}"
    fi
fi
