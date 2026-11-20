"""Tests for command generation (helm, argocd, playbook, install)."""

from install import (
    ArgocdOptions,
    DeploymentMethod,
    HelmOptions,
    Step,
)

# ---------------------------------------------------------------------------
# generate_helm_command
# ---------------------------------------------------------------------------


class TestGenerateHelmCommand:
    def test_basic_helm_release(self):
        step = Step(
            name="superset",
            description="Déployer Superset",
            enable=True,
            helm=HelmOptions(
                release="superset",
                values="superset/values-prod.yaml",
            ),
        )
        cmd = step.generate_helm_command(namespace="projet-dsci")
        assert cmd == (
            "helm upgrade --install superset "
            "-f superset/values-prod.yaml "
            "-n projet-dsci"
        )

    def test_helm_with_set_file(self):
        step = Step(
            name="custom",
            description="Custom step",
            enable=True,
            helm=HelmOptions(
                release="my-release",
                values="values.yaml",
                set_file=(("config.json", "files/config.json"),),
            ),
        )
        cmd = step.generate_helm_command(namespace="default")
        assert "--set-file config.json=files/config.json" in cmd
        assert "-n default" in cmd

    def test_multiple_set_files(self):
        step = Step(
            name="multi",
            description="Multi set-file",
            enable=True,
            helm=HelmOptions(
                release="app",
                values="values.yaml",
                set_file=(
                    ("a", "path/a"),
                    ("b", "path/b"),
                ),
            ),
        )
        cmd = step.generate_helm_command(namespace="ns")
        assert "--set-file a=path/a" in cmd
        assert "--set-file b=path/b" in cmd

    def test_no_helm_returns_message(self):
        step = Step(
            name="no-helm",
            description="No helm",
            enable=True,
        )
        cmd = step.generate_helm_command(namespace="ns")
        assert "No helm command" in cmd


# ---------------------------------------------------------------------------
# generate_argocd_command
# ---------------------------------------------------------------------------


class TestGenerateArgocdCommand:
    def test_basic_argocd_manifest(self):
        step = Step(
            name="superset",
            description="Déployer Superset",
            enable=True,
            argocd=ArgocdOptions(manifest="superset/manifest.yaml"),
        )
        cmd = step.generate_argocd_command()
        assert cmd == "kubectl apply -f superset/manifest.yaml"

    def test_postgres_config_argocd(self):
        step = Step(
            name="db-config",
            description="Déployer la base de données",
            enable=True,
            argocd=ArgocdOptions(manifest="postgres/config/manifest.yaml"),
        )
        cmd = step.generate_argocd_command()
        assert cmd == "kubectl apply -f postgres/config/manifest.yaml"

    def test_no_argocd_returns_message(self):
        step = Step(name="no-argocd", description="No argocd")
        cmd = step.generate_argocd_command()
        assert "No argocd command" in cmd


# ---------------------------------------------------------------------------
# generate_playbook_command
# ---------------------------------------------------------------------------


class TestGeneratePlaybookCommand:
    def test_basic_playbook(self):
        step = Step(
            name="argocd-cli",
            description="Installer ArgoCD CLI",
            enable=True,
            playbook="argocd-cli.yaml",
        )
        cmd = step.generate_playbook_command()
        assert cmd == "ansible-playbook -i localhost argocd-cli.yaml"

    def test_init_db_playbook(self):
        step = Step(
            name="init-postgres-db",
            description="Initialiser les bases",
            enable=True,
            playbook="init-db.yaml",
        )
        cmd = step.generate_playbook_command()
        assert "init-db.yaml" in cmd

    def test_no_playbook_returns_empty_string(self):
        step = Step(name="no-playbook", description="No playbook")
        cmd = step.generate_playbook_command()
        assert cmd == ""


# ---------------------------------------------------------------------------
# generate_install_commands
# ---------------------------------------------------------------------------


class TestGenerateInstallCommands:
    def test_helm_method_helm_command_only(self):
        step = Step(
            name="superset",
            description="Déployer Superset",
            enable=True,
            helm=HelmOptions(
                release="superset",
                values="superset/values-prod.yaml",
            ),
        )
        cmds = step.generate_install_commands(
            method=DeploymentMethod.HELM,
            namespace="projet-dsci",
        )
        # helm command + empty playbook string (no playbook set)
        assert len(cmds) == 2
        assert "helm upgrade --install superset" in cmds[0]
        assert cmds[1] == ""

    def test_argocd_method_argocd_command_only(self):
        step = Step(
            name="superset",
            description="Déployer Superset",
            enable=True,
            argocd=ArgocdOptions(manifest="superset/manifest.yaml"),
        )
        cmds = step.generate_install_commands(
            method=DeploymentMethod.ARGOCD,
            namespace="projet-dsci",
        )
        # argocd command + empty playbook string
        assert len(cmds) == 2
        assert "kubectl apply -f superset/manifest.yaml" in cmds[0]
        assert cmds[1] == ""

    def test_both_methods_includes_playbook(self):
        """Every method call always appends the playbook command when present."""
        step = Step(
            name="argocd-cli",
            description="Installer CLI",
            enable=True,
            playbook="argocd-cli.yaml",
        )
        helm_cmds = step.generate_install_commands(
            method=DeploymentMethod.HELM,
            namespace="ns",
        )
        # helm fallback + playbook
        assert len(helm_cmds) == 2
        assert "No helm command" in helm_cmds[0]
        assert "ansible-playbook" in helm_cmds[1]

        argocd_cmds = step.generate_install_commands(
            method=DeploymentMethod.ARGOCD,
            namespace="ns",
        )
        # argocd fallback + playbook
        assert len(argocd_cmds) == 2
        assert "No argocd command" in argocd_cmds[0]
        assert "ansible-playbook" in argocd_cmds[1]

    def test_disabled_step_empty_commands(self):
        step = Step(
            name="disabled",
            description="Disabled",
            enable=False,
        )
        # Even disabled steps can generate commands — the caller checks .enable
        cmds = step.generate_install_commands(
            method=DeploymentMethod.ARGOCD,
            namespace="ns",
        )
        assert cmds == [
            "No argocd command to generate. Please check install options if it should be the case.",
            "",
        ]


# ---------------------------------------------------------------------------
# Integration: full install_options.yaml command generation
# ---------------------------------------------------------------------------


class TestIntegrationCommands:
    def test_real_yaml_helm_options_present(self):
        """Verify steps in the real YAML have helm options loaded."""
        from pathlib import Path

        from install import load_from_yaml

        options = load_from_yaml(
            Path(__file__).resolve().parent.parent / "install_options.yaml"
        )

        helm_steps = [s for s in options.steps if s.helm is not None]
        assert (
            len(helm_steps) == 5
        )  # db-config, db-data, superset, airflow, renovatebot

    def test_real_yaml_argocd_options_present(self):
        """Verify steps in the real YAML have argocd options loaded."""
        from pathlib import Path

        from install import load_from_yaml

        options = load_from_yaml(
            Path(__file__).resolve().parent.parent / "install_options.yaml"
        )

        argocd_steps = [s for s in options.steps if s.argocd is not None]
        assert (
            len(argocd_steps) == 5
        )  # db-config, db-data, superset, airflow, renovatebot

    def test_real_yaml_playbook_options_present(self):
        """Verify steps in the real YAML have playbook options loaded."""
        from pathlib import Path

        from install import load_from_yaml

        options = load_from_yaml(
            Path(__file__).resolve().parent.parent / "install_options.yaml"
        )

        playbook_steps = [s for s in options.steps if s.playbook is not None]
        assert (
            len(playbook_steps) == 4
        )  # argocd, argocd-cli, argocd-add-repo, init-postgres-db

    def test_helm_method_full_pipeline(self):
        """Simulate what main() does for helm method — collect commands from all enabled steps."""
        from pathlib import Path

        from install import load_from_yaml

        options = load_from_yaml(
            Path(__file__).resolve().parent.parent / "install_options.yaml"
        )

        all_cmds = []
        for step in options.steps:
            if not step.enable:
                continue
            cmds = step.generate_install_commands(
                method=DeploymentMethod.HELM,
                namespace=options.namespace,
            )
            all_cmds.extend(cmds)

        # Currently no steps are enabled in the real YAML, so this should be empty
        assert isinstance(all_cmds, list)

    def test_argocd_method_full_pipeline(self):
        """Simulate what main() does for argocd method."""
        from pathlib import Path

        from install import load_from_yaml

        options = load_from_yaml(
            Path(__file__).resolve().parent.parent / "install_options.yaml"
        )

        all_cmds = []
        for step in options.steps:
            if not step.enable:
                continue
            cmds = step.generate_install_commands(
                method=DeploymentMethod.ARGOCD,
                namespace=options.namespace,
            )
            all_cmds.extend(cmds)

        assert isinstance(all_cmds, list)
