import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess

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
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = Path(CURR_DIR, "install_config.yaml")


@dataclass(frozen=True)
class InstallationStep:
    step_name: str
    enabled: bool
    command: str
    wait_for_completion: bool = False
    app_name: str | None = None
    dry_run: bool = True

    @property
    def cmd_list(self) -> list[str]:
        return self.command.split()

    @property
    def enable_icon(self) -> str:
        return f"{Green}✔{Color_Off}" if self.enabled else f"{Red}✖{Color_Off}"

    @property
    def dry_run_icon(self) -> str:
        return f"{Green}✔{Color_Off}" if self.dry_run else f"{Red}✖{Color_Off}"

    @property
    def dry_run_msg(self) -> str:
        return (
            f"{Yellow}(Command will not be executed){Color_Off}"
            if self.dry_run
            else f"{Yellow}(Command will execute){Color_Off}"
        )

    def log_step(self) -> None:
        print(f"➤  {self.step_name}")
        print(f"\t Enabled: {self.enabled} {self.enable_icon}")
        print(f"\t Dry run: {self.dry_run} {self.dry_run_icon} {self.dry_run_msg}")
        print(f"\t Command: {self.command}")
        if self.wait_for_completion:
            print(f"\t Wait for completion: {self.wait_for_completion}")
        if self.app_name:
            print(f"\t App name: {self.app_name}")


# ==============================
# Helpers
# ==============================
def load_options(config_path: Path) -> list[InstallationStep]:
    with open(file=config_path, mode="r") as f:
        steps_yaml = yaml.safe_load(stream=f)
        steps = steps_yaml.get("installation_steps", [])
        return [InstallationStep(**step) for step in steps]


def run_cmd(cmd: list[str], check: bool = True) -> CompletedProcess[str]:
    print(f"$ {cmd}")
    result = subprocess.run(
        cmd,
        cwd=CURR_DIR,  # Force execution from current py script location
        text=True,
        check=False,  # We handle errors manually to provide better error messages
    )
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def wait_for_argocd_app(app_name: str, timeout: int = 300) -> None:
    print(
        f"Waiting for application '{app_name}' to be Healthy and Synced (timeout: {timeout}s)..."
    )

    result = run_cmd(
        cmd=[
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
            f"{Red}ERROR: application '{app_name}' did not become healthy within {timeout}s. Aborting.{Color_Off}"
        )
        sys.exit(1)

    print(f"{Green}Application '{app_name}' is Healthy and Synced.{Color_Off}")


def prompt_choice(steps: list[InstallationStep]) -> str:
    print(
        "This script will install la Suite Donnée with the following installation steps:"
    )
    for step in steps:
        step.log_step()
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


def execute_installation_step(step: InstallationStep) -> None:
    if step.enabled:
        print(f"Executing step: {step.step_name}")
        if step.dry_run:
            print(
                f"{Yellow}Dry run enabled. Command to be executed: {step.command}{Color_Off}"
            )
        else:
            run_cmd(cmd=step.cmd_list)
            if step.wait_for_completion and step.app_name:
                wait_for_argocd_app(step.app_name)
    else:
        print(f"{Yellow}Skipping step: {step.step_name}{Color_Off}")


# ==============================
# Main
# ==============================
def main() -> None:
    print(f"Loading installation steps from {CONFIG_PATH} ...")
    installation_steps = load_options(config_path=CONFIG_PATH)
    print("Installation steps loaded.")

    choice = prompt_choice(steps=installation_steps)

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

    for step in installation_steps:
        execute_installation_step(step=step)


if __name__ == "__main__":
    main()
