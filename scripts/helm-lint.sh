#!/usr/bin/env bash
set -euo pipefail

# Add helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add apache https://airflow.apache.org
helm repo add apache-superset http://apache.github.io/superset/
helm repo add trinodb https://trinodb.github.io/charts/
helm repo add polaris https://downloads.apache.org/polaris/helm-chart
helm repo add renovatebot https://docs.renovatebot.com/helm-charts
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo update

# Lint each Helm chart
charts=(
  charts/superset
  charts/airflow
  charts/trino
  charts/polaris
  charts/renovatebot
  charts/postgres/config
  charts/postgres/data
  charts/postgres/legacy/config
  charts/postgres/legacy/data
)

cleanup() {
  for chart in "${charts[@]}"; do
    rm -rf "$chart/Chart.lock" "$chart/charts"
  done
}
trap cleanup EXIT

for chart in "${charts[@]}"; do
  echo "==> Linting $chart"
  helm dependency build "$chart" >/dev/null
  values_file="$chart/values-prod.yaml"
  if [ -f "$values_file" ]; then
    helm lint "$chart" -f "$values_file"
  else
    helm lint "$chart"
  fi
done
