"""Tests for class instantiation from the real install_options.yaml file."""

from pathlib import Path

import pytest
import yaml
from install import (
    ArgocdOptions,
    DeploymentMethod,
    HelmOptions,
    InstallOptions,
    Step,
    load_from_yaml,
)

OPTIONS_PATH = Path(__file__).resolve().parent.parent / "install_options.yaml"


@pytest.fixture
def raw_yaml():
    """Load the raw YAML dict from disk."""
    with OPTIONS_PATH.open("r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def install_options():
    """Load the fully instantiated InstallOptions from disk."""
    return load_from_yaml(OPTIONS_PATH)


# ---------------------------------------------------------------------------
# Raw YAML structure checks
# ---------------------------------------------------------------------------


class TestRawYamlStructure:
    def test_global_keys_present(self, raw_yaml):
        assert "global" in raw_yaml
        global_ = raw_yaml["global"]
        assert "playbook_folder" in global_
        assert "app_folder" in global_
        assert "timeout" in global_

    def test_deployment_config_keys_present(self, raw_yaml):
        assert "deployment_config" in raw_yaml
        dc = raw_yaml["deployment_config"]
        assert "mode" in dc
        assert "namespace" in dc

    def test_steps_list_exists(self, raw_yaml):
        assert "steps" in raw_yaml
        assert isinstance(raw_yaml["steps"], list)
        assert len(raw_yaml["steps"]) > 0

    def test_each_step_has_required_keys(self, raw_yaml):
        for step in raw_yaml["steps"]:
            assert "name" in step
            assert "description" in step
            assert "config" in step
            assert "enable" in step["config"]

    def test_mode_is_valid(self, raw_yaml):
        mode_str = raw_yaml["deployment_config"]["mode"].upper()
        assert mode_str in ("ARGOCD", "HELM")


# ---------------------------------------------------------------------------
# DeploymentMethod enum
# ---------------------------------------------------------------------------


class TestDeploymentMethod:
    def test_argocd_value(self):
        assert DeploymentMethod.ARGOCD == "argocd"

    def test_helm_value(self):
        assert DeploymentMethod.HELM == "helm"

    def test_from_yaml_string(self, raw_yaml):
        mode_str = raw_yaml["deployment_config"]["mode"].upper()
        method = DeploymentMethod[mode_str]
        assert isinstance(method, DeploymentMethod)


# ---------------------------------------------------------------------------
# HelmOptions / ArgocdOptions
# ---------------------------------------------------------------------------


class TestHelmOptions:
    def test_db_config_has_helm_options(self, install_options):
        step = next(s for s in install_options.steps if s.name == "db-config")
        assert step.helm is not None
        assert isinstance(step.helm, HelmOptions)

    def test_helm_options_fields(self, install_options):
        step = next(s for s in install_options.steps if s.name == "db-config")
        helm = step.helm
        assert helm.release == "db-config-cluster"
        assert helm.values == "postgres/config/values-prod.yaml"
        assert helm.set_file == ()

    def test_airflow_helm_options(self, install_options):
        step = next(s for s in install_options.steps if s.name == "airflow")
        helm = step.helm
        assert helm.release == "airflow"
        assert helm.values == "airflow/values-prod.yaml"

    def test_superset_set_file_absent(self, install_options):
        step = next(s for s in install_options.steps if s.name == "superset")
        assert step.helm.set_file == ()

    def test_argocd_options_exist(self, install_options):
        step = next(s for s in install_options.steps if s.name == "db-config")
        assert step.argocd is not None
        assert isinstance(step.argocd, ArgocdOptions)

    def test_argocd_manifest_field(self, install_options):
        step = next(s for s in install_options.steps if s.name == "db-config")
        assert step.argocd.manifest == "postgres/config/manifest.yaml"

    def test_disabled_step_still_has_options(self, install_options):
        """Disabled steps should still have their helm/argocd options parsed."""
        step = next(s for s in install_options.steps if s.name == "argocd")
        assert step.enable is False
        assert step.playbook == "argocd.yaml"

    def test_playbook_field_present(self, install_options):
        """Steps that only have playbook should expose it."""
        step = next(s for s in install_options.steps if s.name == "init-postgres-db")
        assert step.playbook == "init-db.yaml"


# ---------------------------------------------------------------------------
# Step dataclass
# ---------------------------------------------------------------------------


class TestStep:
    def test_step_name(self, install_options):
        names = [s.name for s in install_options.steps]
        assert "superset" in names
        assert "airflow" in names
        assert "renovatebot" in names

    def test_step_description(self, install_options):
        step = next(s for s in install_options.steps if s.name == "superset")
        assert step.description == "Déployer Superset dans le namespace"

    def test_enable_flag_varies(self, install_options):
        enabled = [s.name for s in install_options.steps if s.enable]
        disabled = [s.name for s in install_options.steps if not s.enable]
        assert len(enabled) > 0
        assert len(disabled) > 0

    def test_all_steps_are_frozen(self, install_options):
        """Frozen dataclass should raise on attribute mutation."""
        step = install_options.steps[0]
        with pytest.raises(Exception):  # noqa: B017
            step.name = "new-name"


# ---------------------------------------------------------------------------
# InstallOptions dataclass
# ---------------------------------------------------------------------------


class TestInstallOptions:
    def test_mode_loaded(self, install_options):
        assert install_options.mode == DeploymentMethod.ARGOCD

    def test_namespace_loaded(self, install_options):
        assert install_options.namespace == "projet-dsci"

    def test_app_folder_loaded(self, install_options):
        assert install_options.app_folder == "$app_folder argocd"

    def test_playbook_folder_loaded(self, install_options):
        assert install_options.playbook_folder == "$playbook_folder ansible/playbooks"

    def test_timeout_loaded(self, install_options):
        assert install_options.timeout == "10m"

    def test_steps_count(self, install_options):
        assert len(install_options.steps) == 9

    def test_steps_are_dataclass_instances(self, install_options):
        for step in install_options.steps:
            assert isinstance(step, Step)

    def test_install_options_is_frozen(self):
        opts = InstallOptions(
            mode=DeploymentMethod.HELM,
            namespace="test-ns",
            app_folder="argocd",
            playbook_folder="ansible/playbooks",
            timeout="5m",
            steps=[],
        )
        with pytest.raises(Exception):  # noqa: B017
            opts.namespace = "other-ns"  # pyright: ignore[reportAttributeAccessIssue]


# ---------------------------------------------------------------------------
# load_from_yaml function
# ---------------------------------------------------------------------------


class TestLoadFromYaml:
    def test_returns_install_options(self):
        opts = load_from_yaml(OPTIONS_PATH)
        assert isinstance(opts, InstallOptions)

    def test_custom_path(self, tmp_path):
        custom_yaml = tmp_path / "custom_options.yaml"
        custom_yaml.write_text(
            yaml.dump(
                {
                    "global": {
                        "playbook_folder": "playbooks",
                        "app_folder": "apps",
                        "timeout": "30m",
                    },
                    "deployment_config": {
                        "mode": "helm",
                        "namespace": "custom-ns",
                    },
                    "steps": [
                        {
                            "name": "test-step",
                            "description": "A test step",
                            "config": {
                                "enable": True,
                            },
                        }
                    ],
                }
            )
        )
        opts = load_from_yaml(custom_yaml)
        assert opts.mode == DeploymentMethod.HELM
        assert opts.namespace == "custom-ns"
        assert len(opts.steps) == 1
        assert opts.steps[0].name == "test-step"
