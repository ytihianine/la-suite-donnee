import os
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from subprocess import CompletedProcess
from textwrap import dedent
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
VENV_BIN = CURR_DIR / "env" / ("Scripts" if os.name == "nt" else "bin")


class DeploymentMethod(StrEnum):
    ARGOCD = "argocd"
    HELM = "helm"


@dataclass(frozen=True)
class HelmOptions:
    release: str
    values: str
    set_file: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ArgocdOptions:
    manifest: str


@dataclass(frozen=True)
class Step:
    name: str
    description: str
    enable: bool = False
    helm: HelmOptions | None = None
    argocd: ArgocdOptions | None = None
    playbook: str | None = None

    @property
    def enable_logs(self) -> str:
        state = "enabled" if self.enable else "disabled"
        marker = f"{Green}✔{Color_Off}" if self.enable else f"{Red}✖{Color_Off}"
        return f"{marker} {self.name}: {state} {marker} — {self.description}"

    def generate_install_commands(
        self, method: DeploymentMethod, namespace: str
    ) -> list[str]:
        cmd = []

        if self.enable is False:
            return cmd

        if method == DeploymentMethod.HELM and self.helm is not None:
            _cmd = ["helm", "upgrade", "--install", self.helm.release]

            if self.helm.values:
                cmd.extend(["-f", self.helm.values])
            for name, path in self.helm.set_file:
                cmd.extend(["--set-file", f"{name}={path}"])

            cmd.extend(["-n", namespace])
            cmd.append(" ".join(_cmd))

        if method == DeploymentMethod.ARGOCD and self.argocd is not None:
            cmd.append(f"kubectl apply -f {self.argocd.manifest}")

        if self.playbook is not None:
            cmd.append(f"ansible-playbook -i localhost {self.playbook}")

        return cmd


@dataclass(frozen=True)
class InstallOptions:
    mode: DeploymentMethod
    namespace: str
    app_folder: str
    playbook_folder: str
    timeout: str
    steps: list[Step]


def _load_helm_options(raw: dict | None) -> HelmOptions | None:
    if raw is None:
        return None
    return HelmOptions(
        release=raw["release"],
        values=raw.get("values", ()),
        set_file=tuple((p["name"], p["path"]) for p in raw.get("set_file", ())),
    )


def _load_argocd_options(raw: dict | None) -> ArgocdOptions | None:
    if raw is None:
        return None
    return ArgocdOptions(manifest=raw["manifest"])


def load_from_yaml(options_path: Path) -> InstallOptions:
    with options_path.open("r") as f:
        _options = yaml.safe_load(stream=f)

    global_params = _options.get("global")
    deployment_config = _options.get("deployment_config")
    steps = [
        Step(
            name=step["name"],
            description=step["description"],
            enable=step["config"]["enable"],
            helm=_load_helm_options(raw=step.get("helm") or step["config"].get("helm")),
            argocd=_load_argocd_options(
                raw=step.get("argocd") or step["config"].get("argocd")
            ),
            playbook=step.get("playbook") or step["config"].get("playbook"),
        )
        for step in _options["steps"]
    ]

    return InstallOptions(
        mode=DeploymentMethod[deployment_config.get("mode", "argocd").upper()],
        namespace=deployment_config.get("namespace"),
        app_folder=global_params.get("app_folder"),
        playbook_folder=global_params.get("playbook_folder"),
        timeout=global_params.get("timeout"),
        steps=steps,
    )


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


def run(
    cmd: Sequence[str],
    check: bool = True,
    stdin: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> CompletedProcess[str]:
    print(f"$ {' '.join(cmd)}")
    env = build_env()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(  # noqa: PLW1510
        cmd,
        cwd=CURR_DIR,  # Force execution from current py script location
        env=env,  # Use the local venv for child processes
        text=True,
        input=stdin,
    )
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def prompt_choice() -> Literal["Yes", "No", "Cancel"]:
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
    install_mode = user_options.mode
    namespace = user_options.namespace

    if namespace is None:
        raise ValueError("Please define the namespace value in install_options.yaml.")

    print(
        dedent(
            text=f"""
            {"=" * 70}
            This script will install la Suite Donnée
            using the '{install_mode}' method.
            {"-" * 70}
        """
        )
    )

    enable_logs = []
    cmd_logs = []
    for step in user_options.steps:
        enable_logs.append(step.enable_logs)
        cmd_logs.extend(
            step.generate_install_commands(
                method=user_options.mode, namespace=namespace
            )
        )

    print("[Summary] Enabled steps:")
    print(f"\t{'\n\t'.join(enable_logs)}")
    print("[Summary] Commands to execute:")
    print(f"\t{'\n\t'.join(cmd_logs)}")
    print("=" * 70)

    choice = prompt_choice()

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
    print(f"Installing la Suite Donnée using the {install_mode} method...")

    total = len(user_options.steps)
    for i, step in enumerate(user_options.steps, start=1):
        print(f"[Etape {i}/{total}] {step.name.upper()} - {step.description}")
        if not step.enable:
            print(f"{Yellow}{step.name} is disabled... Skipping{Color_Off}")
            continue

        cmd = step.generate_install_commands(method=install_mode, namespace=namespace)
        run(cmd=cmd)


if __name__ == "__main__":
    main()
