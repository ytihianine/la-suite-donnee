import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import install
import pytest
import yaml


@pytest.mark.parametrize("password_file_exists", [True, False])
def test_main_uses_optional_become_password_file(
    monkeypatch, tmp_path, password_file_exists
):
    password_file = tmp_path / ".become-password"
    if password_file_exists:
        password_file.write_text("secret\n")
    monkeypatch.setattr(install, "BECOME_PASSWORD_FILE", password_file)
    monkeypatch.setattr(
        install,
        "load_from_yaml",
        lambda options_path: install.InstallOptions(
            steps=[install.Options("first", "first", True, {"name": "first"})],
            deployment_method="helm",
        ),
    )
    monkeypatch.setattr(install, "prompt_choice", lambda: True)
    with patch.object(install, "run") as run:
        install.main()
    command = run.call_args.args[0]
    assert ("--become-password-file" in command) == password_file_exists
    if password_file_exists:
        assert command[command.index("--become-password-file") + 1] == str(
            password_file
        )
        assert install.build_env()["ANSIBLE_BECOME_ASK_PASS"] == "false"
    assert "secret" not in command


def test_configured_apps_have_charts_and_matching_manifests():
    options = install.load_from_yaml(install.OPTIONS_PATH)
    for step in options.steps:
        if "playbook" in step.data:
            assert (install.CURR_DIR / step.data["playbook"]).is_file()
            continue
        chart = install.CURR_DIR / step.data["chart"]
        assert (chart / "Chart.yaml").is_file()
        assert (chart / "values-prod.yaml").is_file()
        manifest = yaml.safe_load(
            (install.CURR_DIR / step.data["manifest"]).read_text()
        )
        assert manifest["metadata"]["name"] == step.data["release_name"]
        for value in step.data.get("file_values", []):
            assert (install.CURR_DIR / value["path"]).is_file()


@pytest.mark.parametrize("method", ["helm", "argocd"])
def test_main_runs_enabled_steps_in_order(monkeypatch, method):
    steps = [
        {"name": "first", "description": "first", "enable": True, "chart": "chart"},
        {"name": "skipped", "description": "skipped", "enable": False},
        {
            "name": "operator",
            "description": "operator",
            "enable": True,
            "playbook": "ansible/playbooks/deploy-manifest.yaml",
            "manifest": "operator.yaml",
        },
    ]
    options = install.InstallOptions(
        steps=[
            install.Options(s["name"], s["description"], s["enable"], s) for s in steps
        ],
        deployment_method=method,
    )
    monkeypatch.setattr(install, "load_from_yaml", lambda options_path: options)
    monkeypatch.setattr(install, "prompt_choice", lambda: True)
    monkeypatch.setattr(install, "BECOME_PASSWORD_FILE", Path("/nonexistent"))
    with patch.object(install, "run") as run:
        install.main()
    assert run.call_args_list == [
        call(
            [
                "ansible-playbook",
                "-i",
                "localhost,",
                f"ansible/playbooks/deploy-{method}.yaml",
                "--extra-vars",
                f"@{install.OPTIONS_PATH}",
                "--extra-vars",
                json.dumps({"install_step": steps[0]}),
            ]
        ),
        call(
            [
                "ansible-playbook",
                "-i",
                "localhost,",
                "ansible/playbooks/deploy-manifest.yaml",
                "--extra-vars",
                f"@{install.OPTIONS_PATH}",
                "--extra-vars",
                json.dumps({"install_step": steps[2]}),
            ]
        ),
    ]


def test_main_stops_after_failed_step(monkeypatch):
    steps = [
        install.Options("first", "first", True, {"name": "first", "enable": True}),
        install.Options("second", "second", True, {"name": "second", "enable": True}),
    ]
    options = install.InstallOptions(steps=steps, deployment_method="helm")
    monkeypatch.setattr(install, "load_from_yaml", lambda options_path: options)
    monkeypatch.setattr(install, "prompt_choice", lambda: True)
    run = MagicMock(side_effect=SystemExit(3))
    monkeypatch.setattr(install, "run", run)

    with pytest.raises(SystemExit) as error:
        install.main()

    assert error.value.code == 3
    run.assert_called_once()
    assert "ansible/playbooks/deploy-helm.yaml" in run.call_args.args[0]


def test_failed_playbook_aborts(monkeypatch):
    monkeypatch.setattr(
        install.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 3),
    )
    with pytest.raises(SystemExit) as error:
        install.run(["ansible-playbook", "failed.yaml"])
    assert error.value.code == 3


def test_no_enabled_steps_does_not_run_ansible(monkeypatch):
    options = install.InstallOptions(steps=[], deployment_method="helm")
    monkeypatch.setattr(install, "load_from_yaml", lambda options_path: options)
    monkeypatch.setattr(install, "prompt_choice", lambda: True)
    with patch.object(install, "run") as run:
        install.main()
    run.assert_not_called()


def test_invalid_deployment_method_is_rejected(tmp_path):
    config = tmp_path / "install.yaml"
    config.write_text("deployment_method: invalid\ninstall_steps: []\n")
    with pytest.raises(ValueError, match="Unsupported deployment method"):
        install.load_from_yaml(config)
