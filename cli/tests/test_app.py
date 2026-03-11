from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sc_cli.app import app
from sc_cli.runtime import reset_runtime_state


@pytest.fixture(autouse=True)
def reset_cli_runtime() -> Iterator[None]:
    reset_runtime_state()
    yield
    reset_runtime_state()


def test_preview_artifacts_command_lists_sc_core_exports() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["core", "preview-artifacts"])

    assert result.exit_code == 0
    assert "sc_core preview artifacts:" in result.stdout
    assert "definition.normalized.json" in result.stdout
    assert "parameter-bundle.toml" in result.stdout


def test_circuit_definition_inspect_command_delegates_to_sc_core(tmp_path: Path) -> None:
    source_file = tmp_path / "demo.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "name: fluxonium_demo",
                "family: fluxonium",
                "junction_1: JJ",
                "capacitor_1: C",
                "inductor_1: L",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "inspect", str(source_file)])

    assert result.exit_code == 0
    assert f"source_file: {source_file.resolve()}" in result.stdout
    assert "circuit_name: fluxonium_demo" in result.stdout
    assert "family: fluxonium" in result.stdout
    assert '"schemdraw_ready": true' in result.stdout
    assert "Port mapping metadata still needs migration from legacy forms." in result.stdout


def test_circuit_definition_inspect_command_supports_definition_id() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "inspect", "--definition-id", "18"])

    assert result.exit_code == 0
    assert "source_definition_id: 18" in result.stdout
    assert "definition_name: FloatingQubitWithXYLine" in result.stdout
    assert "validation_status: warning" in result.stdout


def test_session_show_command_reads_rewrite_session_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "show"])

    assert result.exit_code == 0
    assert "session_id: rewrite-local-session" in result.stdout
    assert "workspace_id: ws-device-lab" in result.stdout
    assert "default_task_scope: workspace" in result.stdout


def test_datasets_list_command_reads_rewrite_dataset_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["datasets", "list"])

    assert result.exit_code == 0
    assert "datasets: 2" in result.stdout
    assert "fluxonium-2025-031" in result.stdout
    assert "transmon-coupler-014" in result.stdout


def test_tasks_list_command_reads_rewrite_task_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "list"])

    assert result.exit_code == 0
    assert "tasks: 3" in result.stdout
    assert "#301" in result.stdout
    assert "#303" in result.stdout
    assert "#304" not in result.stdout


def test_tasks_show_command_reads_one_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "show", "301"])

    assert result.exit_code == 0
    assert "task_id: 301" in result.stdout
    assert "execution_mode: run" in result.stdout
    assert "worker_task_name: simulation_run_task" in result.stdout
    assert "request_ready: true" in result.stdout


def test_tasks_show_command_uses_structured_backend_error_message() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "show", "999"])

    assert result.exit_code == 2
    assert "error: Task 999 was not found. [not_found/task_not_found]" in result.output
