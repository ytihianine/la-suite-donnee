# La Suite Donnée — AGENTS.md

## Setup

1. `make duplicate-env-vars` then edit `.env`
2. `make setup-dev-env && source env/bin/activate` (creates venv + installs packages via `uv` + installs pre-commit hooks)
3. Python 3.12+ required, Node.js 24+ required only for releases (semantic-release)
4. Ansible runs against localhost; adjust `ansible.cfg` `become_exe` if needed

## Commands

| Command | What |
|---|---|
| `make setup-dev-env` | One-shot: create venv, install packages, install pre-commit |
| `make test` | Run `pytest` on `tests/` |
| `make run-pre-commit` | Run all pre-commit hooks manually |
| `make install-la-suite-donnee` | Run `install.py` — the main installation entrypoint |
| `make build-trino` / `build-superset` / `build-airflow` / `build-polaris` | Build custom Docker images (accept `*_VERSION` arg) |
| `make deploy-<app>` | Deploy a single app via `kubectl apply -f argocd/<app>/manifest.yaml` |
| `make deploy-all` | Deploy Renovate, databases, init-db, Superset, Airflow |

## Architecture

- **argocd/** — per-app subdirectories, each with `Chart.yaml`, `values-prod.yaml`, `manifest.yaml`, optional `templates/`. These are the ArgoCD Application manifests (bitnami/postgres, apache/superset, apache/airflow, renovatebot, polaris, trino).
- **images/** — Dockerfiles for custom Superset, Airflow, Trino, and Polaris images.
- **ansible/playbooks/** — localhost playbooks for ArgoCD install, ARGOCD CLI, ArgoCD repo add, and DB init.
- **install.py** — interactive orchestrator read `install_options.json` to decide which apps to deploy and in which order.

## Git / Release

- Trunk-based: `main` is production. Short-lived `feat/` and `fix/` branches merged via PR.
- Releases use semantic-release (`.releaserc`) on **both `main` and `next`** branches, triggered manually via GitHub Actions `workflow_dispatch`.
- Needs `GH_TOKEN` secret with `contents`, `issues`, `pull-requests` write permissions.
- Conventional commits with custom release rules: `custom` = patch, `release` = major.
- Upstream remote: `https://github.com/ytihianine/la-suite-donnee.git`

## Gotchas

- **PVCs must be deleted** before re-deploying Postgres with new passwords. Data loss risk — the README warns explicitly.
- `install.py` runs `make` subcommands from its own directory (`os.getcwd` is overridden). Do not move it.
- `.env` is gitignored. Always start from `.env.example` via `make duplicate-env-vars`.
- CI lint uses Python 3.14 (not 3.12 as in the README prereqs). The Makefile uses `PYTHON := python3` which resolves to whatever is in the venv.
- Renovatebot needs a GitHub token secret in `argocd/renovatebot/templates/renovatebot-secret.yaml` and matching `values-prod.yaml` config.
- `deploy-all` does **not** yet include Trino or Polaris (comment in Makefile line 154 confirms this).

## Style

- Python: `ruff` for linting + formatting (replaces black/isort). Pre-commit hooks apply `--fix` automatically.
- YAML: checked by pre-commit. All Helm values are production overrides in `*-values.yaml`.
