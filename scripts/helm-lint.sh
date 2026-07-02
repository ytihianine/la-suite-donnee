#!/usr/bin/env bash
set -euo pipefail

# Add helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add apache https://airflow.apache.org
helm repo add apache-superset http://apache.github.io/superset/
helm repo add trinodb https://trinodb.github.io/charts/
helm repo add polaris https://downloads.apache.org/polaris/helm-chart
helm repo add external-secrets https://charts.external-secrets.io
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo add renovatebot https://docs.renovatebot.com/helm-charts
helm repo update

# Lint each Helm chart
charts=(
  argocd/superset
  argocd/airflow
  argocd/trino
  argocd/polaris
  argocd/renovatebot
  argocd/external-secrets
  argocd/secret-operator
  argocd/postgres/config
  argocd/postgres/data
)

for chart in "${charts[@]}"; do
  echo "==> Linting $chart"
  values_file="$chart/values-prod.yaml"
  if [ -f "$values_file" ]; then
    helm lint "$chart" -f "$values_file"
  else
    helm lint "$chart"
  fi
done
