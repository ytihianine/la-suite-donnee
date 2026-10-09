import shlex
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
OPTIONS_PATH = CURR_DIR / "install_options.yaml"


@dataclass(frozen=True)
class Options:
    name: str
    enable: bool
    cmd: tuple[str, ...]
    wait_app: str | None = None


@dataclass(frozen=True)
class InstallOptions:
    steps: list[Options]


def load_from_yaml(options_path: Path) -> InstallOptions:
    with options_path.open("r") as f:
        _options = yaml.safe_load(stream=f)

    steps = [
        Options(
            name=step["name"],
            enable=step["enable"],
            cmd=tuple(step["cmd"]),
            wait_app=step.get("wait_app"),
        )
        for step in _options["steps"]
    ]

    return InstallOptions(steps=steps)


# ==============================
# Helpers
# ==============================
def run(cmd: Sequence[str], check: bool = True) -> CompletedProcess[str]:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(  # noqa: PLW1510
        cmd,
        cwd=CURR_DIR,  # Force execution from current py script location
        text=True,
    )
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def wait_for_argocd_app(app_name: str, timeout: int = 300) -> None:
    print(
        f"Waiting for ArgoCD application '{app_name}' ",
        f"to be Healthy and Synced (timeout: {timeout}s)",
    )

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
            f"{Red}ERROR: ArgoCD application '{app_name}' ",
            f"did not become healthy within {timeout}s. Aborting.{Color_Off}",
        )
        sys.exit(1)

    print(f"{Green}ArgoCD application '{app_name}' is Healthy and Synced.{Color_Off}")


def prompt_choice(options: InstallOptions) -> Literal["Yes", "No", "Cancel"]:
    print(
        "This script will install la Suite Donnée with the following installation options:"
    )
    for step in options.steps:
        state = "enabled" if step.enable else "disabled"
        marker = f"{Green}✔{Color_Off}" if step.enable else f"{Red}✖{Color_Off}"
        print(f"\t {step.name}: {state} {marker}")
    print()

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
        print(f"[Etape {i}/{total}]")
        if step.enable:
            print(f"{step.name} is enabled. Running commands...")
            for command in step.cmd:
                run(shlex.split(command))
            if step.wait_app:
                wait_for_argocd_app(step.wait_app)
        else:
            print(f"{Yellow}{step.name} is disabled... Skipping{Color_Off}")


if __name__ == "__main__":
    main()
