#!/usr/bin/env bash
set -euo pipefail


# Render each umbrella chart independently with its production values
charts=(
  charts/superset/operator
  charts/superset
  charts/superset/legacy
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
  echo "==> Rendering $chart"
  helm dependency build "$chart" >/dev/null
  values_file="$chart/values-prod.yaml"
  if [ -f "$values_file" ]; then
    helm template "render-${chart//\//}" "$chart" -f "$values_file" --namespace default >/dev/null
  else
    helm template "render-${chart//\//}" "$chart" --namespace default >/dev/null
  fi
done
