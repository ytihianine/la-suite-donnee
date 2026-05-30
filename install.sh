#!/bin/bash

# ==============================
# OPTIONS
# ==============================
INSTALL_ALL=false
INSTALL_ARGOCD=false
INSTALL_ARGOCD_CLI=false
INSTALL_RENOVATE=false
INSTALL_DATABASES=false
INIT_DATABASES=false
INSTALL_SUPERSET=false
INSTALL_AIRFLOW=false
INSTALL_TRINO=false
INSTALL_POLARIS=false

# ==============================
# User confirmation
# ==============================
echo "This script will install la Suite Donnée with the following installation options:"
echo -e "\t Install all components: $INSTALL_ALL"
echo -e "\t Install ArgoCD: $INSTALL_ARGOCD"
echo -e "\t Install ArgoCD CLI: $INSTALL_ARGOCD_CLI"
echo -e "\t Deploy Renovate Bot: $INSTALL_RENOVATE"
echo -e "\t Deploy databases: $INSTALL_DATABASES"
echo -e "\t Init databases: $INIT_DATABASES"
echo -e "\t Deploy Superset: $INSTALL_SUPERSET"
echo -e "\t Deploy Airflow: $INSTALL_AIRFLOW"
echo -e "\t Deploy Trino: $INSTALL_TRINO"
echo -e "\t Deploy Polaris: $INSTALL_POLARIS"
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
if [ "$INSTALL_ALL" = true ]; then
    ## Install la Suite Donnée - All in one
    echo "Install la Suite Donnée using the All-in-one command..."
    make deploy-all
else
    ## Install la Suite Donnée - step by step
    echo "Install la Suite Donnée using the step-by-step commands..."
    # Install ArgoCD
    if [ "$INSTALL_ARGOCD" = true ]; then
        echo "Installing ArgoCD..."
        make deploy-argocd
    else
        echo "INSTALL_ARGOCD is $INSTALL_ARGOCD. Skipping ArgoCD installation..."
    fi

    # Install ArgoCD CLI
    if [ "$INSTALL_ARGOCD_CLI" = true ]; then
        echo "Installing ArgoCD CLI..."
        make deploy-argocd-cli
    else
        echo "INSTALL_ARGOCD_CLI is $INSTALL_ARGOCD_CLI. Skipping ArgoCD CLI installation..."
    fi

    # Deploy renovate bot
    if [ "$INSTALL_RENOVATE" = true ]; then
        echo "Deploying Renovate Bot..."
        make deploy-renovatebot
    else
        echo "INSTALL_RENOVATE is $INSTALL_RENOVATE. Skipping Renovate Bot deployment..."
    fi

    # Deploy databases
    if [ "$INSTALL_DATABASES" = true ]; then
        echo "Deploying databases..."
        make deploy-databases
    else
        echo "INSTALL_DATABASES is $INSTALL_DATABASES. Skipping databases deployment..."
    fi

    # Init databases
    if [ "$INIT_DATABASES" = true ]; then
        echo "Initializing databases..."
        make init-databases
    else
        echo "INIT_DATABASES is $INIT_DATABASES. Skipping databases initialization..."
    fi

    # Deploy Superset
    if [ "$INSTALL_SUPERSET" = true ]; then
        echo "Deploying Superset..."
        make deploy-superset
    else
        echo "INSTALL_SUPERSET is $INSTALL_SUPERSET. Skipping Superset deployment..."
    fi

    # Deploy Airflow
    if [ "$INSTALL_AIRFLOW" = true ]; then
        echo "Deploying Airflow..."
        make deploy-airflow
    else
        echo "INSTALL_AIRFLOW is $INSTALL_AIRFLOW. Skipping Airflow deployment..."
    fi

    # Deploy Trino
    if [ "$INSTALL_TRINO" = true ]; then
        echo "Deploying Trino..."
        make deploy-trino
    else
        echo "INSTALL_TRINO is $INSTALL_TRINO. Skipping Trino deployment..."
    fi

    # Deploy Polaris
    if [ "$INSTALL_POLARIS" = true ]; then
        echo "Deploying Polaris..."
        make deploy-polaris
    else
        echo "INSTALL_POLARIS is $INSTALL_POLARIS. Skipping Polaris deployment..."
    fi
fi
