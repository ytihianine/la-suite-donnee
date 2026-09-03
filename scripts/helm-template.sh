#!/usr/bin/env bash
set -euo pipefail

# Add helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add apache https://airflow.apache.org
helm repo add apache-superset https://apache.github.io/superset/
helm repo add trinodb https://trinodb.github.io/charts/
helm repo add polaris https://downloads.apache.org/polaris/helm-chart
helm repo add renovatebot https://docs.renovatebot.com/helm-charts
helm repo update

# Render each umbrella chart independently with its production values
charts=(
  argocd/superset
  argocd/airflow
  argocd/trino
  argocd/polaris
  argocd/renovatebot
  argocd/postgres/config
  argocd/postgres/data
)

cleanup() {
  for chart in "${charts[@]}"; do
    rm -rf "$chart/Chart.lock" "$chart/charts"
  done
}
trap cleanup EXIT

for chart in "${charts[@]}"; do
  echo "==> Rendering $chart"
  helm dependency build "$chart"
  values_file="$chart/values-prod.yaml"
  if [ -f "$values_file" ]; then
    helm template "render-${chart//\//}" "$chart" -f "$values_file" --namespace default
  else
    helm template "render-${chart//\//}" "$chart" --namespace default
  fi
done
