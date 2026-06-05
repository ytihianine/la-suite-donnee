#!/usr/bin/env python3
import os
import json
import subprocess
import sys
from pathlib import Path
from typing import TypedDict, Mapping, Any

# ==============================
# Variables
# ==============================
# Colors
Color_Off = "\033[0m"
Red = "\033[0;31m"
Green = "\033[0;32m"
Yellow = "\033[0;33m"

# Options
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
OPTIONS_PATH = Path(CURR_DIR, "install_options.json")


class ArgoCDConfig(TypedDict):
    DEPLOY_APP: bool
    INSTALL_CLI: bool
    ADD_REPO: bool


class RenovateBotConfig(TypedDict):
    DEPLOY_APP: bool


class DatabaseConfig(TypedDict):
    DEPLOY_CONFIG_DB: bool
    DEPLOY_DATA_DB: bool
    INIT_DB: bool


class AppConfig(TypedDict):
    DEPLOY_APP: bool


class InstallOptions(TypedDict):
    ARGOCD: ArgoCDConfig
    RENOVATEBOT: RenovateBotConfig
    DATABASES: DatabaseConfig
    SUPERSET: AppConfig
    AIRFLOW: AppConfig
    TRINO: AppConfig
    POLARIS: AppConfig


# ==============================
# Helpers
# ==============================
def load_options(options_path: Path) -> InstallOptions:
    with options_path.open("r") as f:
        return json.load(f)


def run(cmd, check=True):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=CURR_DIR,  # Force execution from current py script location
        text=True,
    )
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def wait_for_argocd_app(app_name, timeout=300):
    print(
        f"Waiting for ArgoCD application '{app_name}' to be Healthy and Synced (timeout: {timeout}s)..."
    )  # noqa

    result = run(
        [
            "argocd",
            "app",
            "wait",
            app_name,
            "--health",
            "--sync",
            "--timeout",
            str(timeout),
        ],
        check=False,
    )

    if result.returncode != 0:
        print(
            f"{Red}ERROR: ArgoCD application '{app_name}' did not become healthy within {timeout}s. Aborting.{Color_Off}"
        )  # noqa
        sys.exit(1)

    print(f"{Green}ArgoCD application '{app_name}' is Healthy and Synced.{Color_Off}")


def prompt_choice(options: Mapping[str, Any]):
    print(
        "This script will install la Suite Donnée with the following installation options:"
    )
    for app, option in options.items():
        print(f"Options for {app}")
        for k, v in option.items():
            print(f"\t {k}: {v}")
    print()

    options = ["Yes", "No", "Cancel"]

    while True:
        print("Do you wish to proceed the installation?")
        for i, opt in enumerate(options, 1):
            print(f"{i}) {opt}")

        choice = input("> ").strip()

        if choice in ["1", "Yes"]:
            return "Yes"
        elif choice in ["2", "No"]:
            return "No"
        elif choice in ["3", "Cancel"]:
            return "Cancel"
        else:
            print("Invalid option. Please select 1, 2, or 3.")


# ==============================
# Main
# ==============================
def main():
    user_options = load_options(options_path=OPTIONS_PATH)

    choice = prompt_choice(options=user_options)

    if choice == "Yes":
        print("Proceeding with the installation...")
    elif choice == "No":
        print("Installation aborted by the user.")
        sys.exit(0)
    elif choice == "Cancel":
        print("Installation cancelled by the user.")
        sys.exit(0)
    else:
        print("Unexpected choice. Exiting.")
        sys.exit(1)

    # ==============================
    # Install la Suite Donnée
    # ==============================
    print("Install la Suite Donnée using the modular method...")

    # ArgoCD
    if user_options["ARGOCD"]["DEPLOY_APP"] is True:
        print("Installing ArgoCD...")
        run(["make", "deploy-argocd"])
    else:
        print(f"{Yellow}Skipping ArgoCD installation...{Color_Off}")

    # ArgoCD CLI
    if user_options["ARGOCD"]["INSTALL_CLI"] is True:
        print("Installing ArgoCD CLI...")
        run(["make", "deploy-argocd-cli"])
        run(["make", "connect-argocd"])
    else:
        print(f"{Yellow}Skipping ArgoCD CLI installation...{Color_Off}")

    # Add repo
    if user_options["ARGOCD"]["ADD_REPO"] is True:
        print("Adding repo to ArgoCD...")
        run(["make", "deploy-argocd-add-repo"])
    else:
        print(f"{Yellow}Skipping ArgoCD repo addition...{Color_Off}")

    # Renovate
    if user_options["RENOVATEBOT"]["DEPLOY_APP"] is True:
        print("Deploying Renovate Bot...")
        run(["make", "deploy-renovatebot"])
    else:
        print(f"{Yellow}Skipping Renovate Bot...{Color_Off}")

    # Databases
    if user_options["DATABASES"]["DEPLOY_CONFIG_DB"] is True:
        run(["make", "deploy-db-config"])
        wait_for_argocd_app("db-config-prod")
    else:
        print(f"{Yellow}Skipping config database...{Color_Off}")

    if user_options["DATABASES"]["DEPLOY_DATA_DB"] is True:
        run(["make", "deploy-db-data"])
        wait_for_argocd_app("db-data-prod")
    else:
        print(f"{Yellow}Skipping data database...{Color_Off}")

    # Init DB
    if user_options["DATABASES"]["INIT_DB"] is True:
        print("Initializing databases...")
        run(["make", "init-databases"])
    else:
        print(f"{Yellow}Skipping database initialization...{Color_Off}")

    # Superset
    if user_options["SUPERSET"]["DEPLOY_APP"] is True:
        print("Deploying Superset...")
        run(["make", "deploy-superset"])
    else:
        print(f"{Yellow}Skipping Superset...{Color_Off}")

    # Airflow
    if user_options["AIRFLOW"]["DEPLOY_APP"] is True:
        print("Deploying Airflow...")
        run(["make", "deploy-airflow"])
    else:
        print(f"{Yellow}Skipping Airflow...{Color_Off}")

    # Trino
    if user_options["TRINO"]["DEPLOY_APP"] is True:
        print("Deploying Trino...")
        run(["make", "deploy-trino"])
    else:
        print(f"{Yellow}Skipping Trino...{Color_Off}")

    # Polaris
    if user_options["POLARIS"]["DEPLOY_APP"] is True:
        print("Deploying Polaris...")
        run(["make", "deploy-polaris"])
    else:
        print(f"{Yellow}Skipping Polaris...{Color_Off}")


if __name__ == "__main__":
    main()
