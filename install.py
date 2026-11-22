import json
import os
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess
from typing import Literal

import yaml

# ==============================
# Variables
# ==============================
# Colors
Color_Off = "\033[0m"
Red = "\033[0;31m"
Green = "\033[0;32m"
Yellow = "\033[0;33m"

# Options
CURR_DIR = Path(__file__).resolve().parent
OPTIONS_PATH = CURR_DIR / "ansible" / "vars" / "install.yaml"
VENV_BIN = CURR_DIR / "env" / ("Scripts" if os.name == "nt" else "bin")


@dataclass(frozen=True)
class Options:
    name: str
    description: str
    enable: bool
    data: dict


@dataclass(frozen=True)
class InstallOptions:
    steps: list[Options]
    deployment_method: str


def load_from_yaml(options_path: Path) -> InstallOptions:
    with options_path.open("r") as f:
        _options = yaml.safe_load(stream=f)

    deployment_method = _options["deployment_method"]
    if deployment_method not in ("helm", "argocd"):
        raise ValueError(f"Unsupported deployment method: {deployment_method}")

    steps = [
        Options(
            name=step["name"],
            description=step["description"],
            enable=step["enable"],
            data=step,
        )
        for step in _options["install_steps"]
    ]

    return InstallOptions(steps=steps, deployment_method=deployment_method)


# ==============================
# Helpers
# ==============================
def build_env() -> dict[str, str]:
    """Return a copy of the environment with the local venv bin dir first in PATH.

    This ensures commands like `ansible-playbook` resolve to the venv ones
    even when the venv is not activated in the calling shell.
    """
    env = os.environ.copy()
    if VENV_BIN.is_dir():
        env["PATH"] = os.pathsep.join((str(VENV_BIN), env.get("PATH", "")))
    return env


def run(cmd: Sequence[str], check: bool = True) -> CompletedProcess[str]:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(  # noqa: PLW1510
        cmd,
        cwd=CURR_DIR,  # Force execution from current py script location
        env=build_env(),  # Use the local venv for child processes
        text=True,
    )
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def prompt_choice(options: InstallOptions) -> Literal["Yes", "No", "Cancel"]:
    user_options = ["Yes", "No", "Cancel"]

    while True:
        print("Do you wish to proceed the installation?")
        for i, opt in enumerate(user_options, 1):
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
def main() -> None:
    user_options = load_from_yaml(options_path=OPTIONS_PATH)

    print()
    print(
        "This script will install la Suite Donnée with the following installation options:"
    )
    print()
    print(f"Deployment method: {user_options.deployment_method}")
    for step in user_options.steps:
        state = "enabled" if step.enable else "disabled"
        marker = f"{Green}✔{Color_Off}" if step.enable else f"{Red}✖{Color_Off}"
        print(f"\t {step.name}: {state} {marker}")
    print()

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

    total = len(user_options.steps)
    for i, step in enumerate(user_options.steps, start=1):
        print(f"[Etape {i}/{total}] {step.name.upper()} - {step.description}")
        if step.enable:
            playbook = step.data.get(
                "playbook",
                f"ansible/playbooks/deploy-{user_options.deployment_method}.yaml",
            )
            run(
                [
                    "ansible-playbook",
                    "-i",
                    "localhost,",
                    playbook,
                    "--extra-vars",
                    f"@{OPTIONS_PATH}",
                    "--extra-vars",
                    json.dumps({"install_step": step.data}),
                ]
            )
        else:
            print(f"{Yellow}{step.name} is disabled... Skipping{Color_Off}")


if __name__ == "__main__":
    main()
