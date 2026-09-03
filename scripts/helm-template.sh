#!/usr/bin/env bash
set -euo pipefail


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
  helm dependency build "$chart" >/dev/null
  values_file="$chart/values-prod.yaml"
  if [ -f "$values_file" ]; then
    helm template "render-${chart//\//}" "$chart" -f "$values_file" --namespace default >/dev/null
  else
    helm template "render-${chart//\//}" "$chart" --namespace default >/dev/null
  fi
done
