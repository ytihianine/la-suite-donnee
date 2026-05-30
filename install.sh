#!/bin/bash

# Load .env file variables into the script
set -a
source ".env"
set +a


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
        echo "LSD_INSTALL_ARGOCD is $LSD_INSTALL_ARGOCD. Skipping ArgoCD installation..."
    fi

    # Install ArgoCD CLI
    if [ "$LSD_INSTALL_ARGOCD_CLI" = true ]; then
        echo "Installing ArgoCD CLI..."
        make deploy-argocd-cli
    else
        echo "LSD_INSTALL_ARGOCD_CLI is $LSD_INSTALL_ARGOCD_CLI. Skipping ArgoCD CLI installation..."
    fi

    # Deploy renovate bot
    if [ "$LSD_INSTALL_RENOVATE" = true ]; then
        echo "Deploying Renovate Bot..."
        make deploy-renovatebot
    else
        echo "LSD_INSTALL_RENOVATE is $LSD_INSTALL_RENOVATE. Skipping Renovate Bot deployment..."
    fi

    # Deploy databases
    if [ "$LSD_INSTALL_DATABASES" = true ]; then
        echo "Deploying databases..."
        make deploy-databases
    else
        echo "LSD_INSTALL_DATABASES is $LSD_INSTALL_DATABASES. Skipping databases deployment..."
    fi

    # Init databases
    if [ "$LSD_INIT_DATABASES" = true ]; then
        echo "Initializing databases..."
        make init-databases
    else
        echo "LSD_INIT_DATABASES is $LSD_INIT_DATABASES. Skipping databases initialization..."
    fi

    # Deploy Superset
    if [ "$LSD_INSTALL_SUPERSET" = true ]; then
        echo "Deploying Superset..."
        make deploy-superset
    else
        echo "LSD_INSTALL_SUPERSET is $LSD_INSTALL_SUPERSET. Skipping Superset deployment..."
    fi

    # Deploy Airflow
    if [ "$LSD_INSTALL_AIRFLOW" = true ]; then
        echo "Deploying Airflow..."
        make deploy-airflow
    else
        echo "LSD_INSTALL_AIRFLOW is $LSD_INSTALL_AIRFLOW. Skipping Airflow deployment..."
    fi

    # Deploy Trino
    if [ "$LSD_INSTALL_TRINO" = true ]; then
        echo "Deploying Trino..."
        make deploy-trino
    else
        echo "LSD_INSTALL_TRINO is $LSD_INSTALL_TRINO. Skipping Trino deployment..."
    fi

    # Deploy Polaris
    if [ "$LSD_INSTALL_POLARIS" = true ]; then
        echo "Deploying Polaris..."
        make deploy-polaris
    else
        echo "LSD_INSTALL_POLARIS is $LSD_INSTALL_POLARIS. Skipping Polaris deployment..."
    fi
fi
