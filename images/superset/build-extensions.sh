#!/usr/bin/env bash
set -euo pipefail

# Build all Superset extensions and collect the generated *.supx bundles
# at the root of the extensions/ directory (superset-dsfr/extensions/).
#
# Paths are resolved relative to this script's location, so it works both
# from the repository (images/superset/) and from the dedicated build stage
# of images/superset/Dockerfile.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Extensions live next to this script: <script dir>/superset-dsfr/extensions
EXTENSIONS_DIR="$SCRIPT_DIR/superset-dsfr/extensions"

# Prefer the project venv, fall back to the PATH
if [ -x "$ROOT_DIR/env/bin/superset-extensions" ]; then
  SUPERSET_EXTENSIONS="$ROOT_DIR/env/bin/superset-extensions"
elif command -v superset-extensions >/dev/null 2>&1; then
  SUPERSET_EXTENSIONS="superset-extensions"
else
  echo "❌ superset-extensions not found. Run 'make setup-dev-env' (or 'pip install apache-superset-extensions-cli') first." >&2
  exit 1
fi

if [ ! -d "$EXTENSIONS_DIR" ]; then
  echo "❌ Extensions directory not found: $EXTENSIONS_DIR" >&2
  exit 1
fi

shopt -s nullglob

built=0
for ext_dir in "$EXTENSIONS_DIR"/*/; do
  ext_dir="${ext_dir%/}"
  # Only directories containing an extension.json are extensions
  if [ ! -f "$ext_dir/extension.json" ]; then
    continue
  fi

  ext_name="$(basename "$ext_dir")"
  echo "==> Building extension: $ext_name"
  (cd "$ext_dir" && "$SUPERSET_EXTENSIONS" bundle)

  # Move the generated *.supx bundle(s) to the extensions root
  moved=0
  for supx in "$ext_dir"/*.supx; do
    echo "    Moving $(basename "$supx") -> $EXTENSIONS_DIR/"
    mv "$supx" "$EXTENSIONS_DIR/"
    moved=$((moved + 1))
  done
  if [ "$moved" -eq 0 ]; then
    echo "❌ No .supx file generated for $ext_name" >&2
    exit 1
  fi

  built=$((built + 1))
done

if [ "$built" -eq 0 ]; then
  echo "❌ No extensions found in $EXTENSIONS_DIR" >&2
  exit 1
fi

echo "✅ Built $built extension(s). Bundles:"
ls -1 "$EXTENSIONS_DIR"/*.supx
