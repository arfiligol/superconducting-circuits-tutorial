from collections.abc import Iterator
from pathlib import Path

import pytest
from sc_backend import ApiErrorBodyResponse, BackendContractError
from typer.testing import CliRunner

from sc_cli.app import app
from sc_cli.commands import (
    characterization,
    datasets,
    events,
    ops,
    results,
    session,
    simulation,
    tasks,
)
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


def test_circuit_definition_list_command_reads_rewrite_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "list"])

    assert result.exit_code == 0
    assert "circuit_definitions: 3" in result.stdout
    assert "#18" in result.stdout
    assert "FloatingQubitWithXYLine" in result.stdout


def test_circuit_definition_list_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "list", "--output", "json"])

    assert result.exit_code == 0
    assert '"definition_id": 18' in result.stdout
    assert '"name": "FloatingQubitWithXYLine"' in result.stdout


def test_circuit_definition_inspect_command_supports_json_output(tmp_path: Path) -> None:
    source_file = tmp_path / "demo-json.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "name: fluxonium_demo_json",
                "family: fluxonium",
                "junction_1: JJ",
                "capacitor_1: C",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        app, ["circuit-definition", "inspect", str(source_file), "--output", "json"]
    )

    assert result.exit_code == 0
    assert f'"source_file": "{source_file.resolve()}"' in result.stdout
    assert '"circuit_name": "fluxonium_demo_json"' in result.stdout


def test_circuit_definition_create_command_persists_local_source(tmp_path: Path) -> None:
    source_file = tmp_path / "created.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "circuit:",
                "  name: fluxonium_cli_create",
                "  family: fluxonium",
                "  elements:",
                "    junction:",
                "      ej_ghz: 8.91",
                "    capacitance:",
                "      ec_ghz: 1.17",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "circuit-definition",
            "create",
            str(source_file),
            "--name",
            "FluxoniumCliCreate",
        ],
    )

    assert result.exit_code == 0
    assert "source_definition_id: 19" in result.stdout
    assert "definition_name: FluxoniumCliCreate" in result.stdout
    assert "validation_status: warning" in result.stdout


def test_circuit_definition_create_command_supports_json_output(tmp_path: Path) -> None:
    source_file = tmp_path / "created-json.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "circuit:",
                "  name: transmon_cli_create",
                "  family: transmon",
                "  elements:",
                "    coupler:",
                "      g_mhz: 12.4",
                "    bus:",
                "      resonance_ghz: 6.94",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "circuit-definition",
            "create",
            str(source_file),
            "--name",
            "TransmonCliCreate",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"definition_id": 19' in result.stdout
    assert '"name": "TransmonCliCreate"' in result.stdout
    assert '"validation_status": "warning"' in result.stdout


def test_circuit_definition_create_command_uses_structured_validation_error(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "blank.circuit.yaml"
    source_file.write_text("   \n", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "circuit-definition",
            "create",
            str(source_file),
            "--name",
            "BlankDefinition",
        ],
    )

    assert result.exit_code == 2
    assert (
        "error: Request validation failed. [validation/request_validation_failed]" in result.output
    )
    assert "field_error: source_text:" in result.output


def test_circuit_definition_update_command_updates_existing_definition(tmp_path: Path) -> None:
    source_file = tmp_path / "updated.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "circuit:",
                "  name: floating_qubit_cli_update",
                "  family: fluxonium",
                "  elements:",
                "    junction:",
                "      ej_ghz: 8.73",
                "    shunt_inductor:",
                "      el_ghz: 0.47",
                "    capacitance:",
                "      ec_ghz: 1.19",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "circuit-definition",
            "update",
            "18",
            str(source_file),
            "--name",
            "FloatingQubitCliUpdate",
        ],
    )

    assert result.exit_code == 0
    assert "source_definition_id: 18" in result.stdout
    assert "definition_name: FloatingQubitCliUpdate" in result.stdout
    assert "validation_status: warning" in result.stdout


def test_circuit_definition_update_command_supports_json_output(tmp_path: Path) -> None:
    source_file = tmp_path / "updated-json.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "circuit:",
                "  name: readout_chain_cli_update",
                "  family: fluxonium",
                "  elements:",
                "    readout:",
                "      resonator_ghz: 6.92",
                "    coupling:",
                "      chi_mhz: 2.8",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "circuit-definition",
            "update",
            "12",
            str(source_file),
            "--name",
            "ReadoutChainCliUpdate",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"definition_id": 12' in result.stdout
    assert '"name": "ReadoutChainCliUpdate"' in result.stdout
    assert '"validation_status": "warning"' in result.stdout


def test_circuit_definition_delete_command_deletes_definition() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "delete", "7", "--yes"])

    assert result.exit_code == 0
    assert "operation: deleted" in result.stdout
    assert "definition_id: 7" in result.stdout


def test_circuit_definition_delete_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "delete", "7", "--yes", "--output", "json"])

    assert result.exit_code == 0
    assert '"operation": "deleted"' in result.stdout
    assert '"definition_id": 7' in result.stdout


def test_circuit_definition_delete_command_requires_confirmation() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "delete", "7"])

    assert result.exit_code == 2
    assert "error: Pass --yes to delete a persisted circuit definition." in result.output


def test_session_show_command_reads_rewrite_session_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "show"])

    assert result.exit_code == 0
    assert "session_id: rewrite-local-session" in result.stdout
    assert "workspace_id: ws-device-lab" in result.stdout
    assert "default_task_scope: workspace" in result.stdout


def test_session_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "show", "--output", "json"])

    assert result.exit_code == 0
    assert '"session_id": "rewrite-local-session"' in result.stdout
    assert '"workspace_id": "ws-device-lab"' in result.stdout


def test_session_whoami_command_reads_identity_context() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "whoami"])

    assert result.exit_code == 0
    assert "identity_user_id: researcher-01" in result.stdout
    assert "identity_display_name: Rewrite Local User" in result.stdout
    assert "can_submit_tasks: true" in result.stdout


def test_session_whoami_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "whoami", "--output", "json"])

    assert result.exit_code == 0
    assert '"session_id": "rewrite-local-session"' in result.stdout
    assert '"user_id": "researcher-01"' in result.stdout
    assert '"can_manage_datasets": true' in result.stdout


def test_session_workspace_command_reads_workspace_context() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "workspace"])

    assert result.exit_code == 0
    assert "workspace_id: ws-device-lab" in result.stdout
    assert "workspace_display_name: Device Lab Workspace" in result.stdout
    assert "active_dataset_id: fluxonium-2025-031" in result.stdout


def test_session_workspace_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "workspace", "--output", "json"])

    assert result.exit_code == 0
    assert '"workspace_id": "ws-device-lab"' in result.stdout
    assert '"default_task_scope": "workspace"' in result.stdout
    assert '"active_dataset": {' in result.stdout


def test_session_active_dataset_command_reads_active_dataset_context() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "active-dataset"])

    assert result.exit_code == 0
    assert "active_dataset_id: fluxonium-2025-031" in result.stdout
    assert "active_dataset_name: Fluxonium sweep 031" in result.stdout


def test_session_active_dataset_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "active-dataset", "--output", "json"])

    assert result.exit_code == 0
    assert '"active_dataset": {' in result.stdout
    assert '"dataset_id": "fluxonium-2025-031"' in result.stdout


def test_session_set_active_dataset_command_updates_session_state() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["session", "set-active-dataset", "transmon-coupler-014"],
    )

    assert result.exit_code == 0
    assert "active_dataset_id: transmon-coupler-014" in result.stdout
    assert "active_dataset_name: Coupler detuning 014" in result.stdout


def test_session_set_active_dataset_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["session", "set-active-dataset", "transmon-coupler-014", "--output", "json"],
    )

    assert result.exit_code == 0
    assert '"dataset_id": "transmon-coupler-014"' in result.stdout
    assert '"name": "Coupler detuning 014"' in result.stdout


def test_session_set_active_dataset_command_supports_clearing_context() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "set-active-dataset", "--clear"])

    assert result.exit_code == 0
    assert "active_dataset: none" in result.stdout


def test_session_active_dataset_command_reports_cleared_context() -> None:
    runner = CliRunner()

    clear_result = runner.invoke(app, ["session", "set-active-dataset", "--clear"])
    result = runner.invoke(app, ["session", "active-dataset"])

    assert clear_result.exit_code == 0
    assert result.exit_code == 0
    assert "active_dataset: none" in result.stdout


def test_datasets_list_command_reads_rewrite_dataset_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["datasets", "list"])

    assert result.exit_code == 0
    assert "datasets: 2" in result.stdout
    assert "fluxonium-2025-031" in result.stdout
    assert "transmon-coupler-014" in result.stdout


def test_datasets_list_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["datasets", "list", "--output", "json"])

    assert result.exit_code == 0
    assert '"dataset_id": "fluxonium-2025-031"' in result.stdout
    assert '"dataset_id": "transmon-coupler-014"' in result.stdout


def test_datasets_show_command_reads_one_dataset() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["datasets", "show", "fluxonium-2025-031"])

    assert result.exit_code == 0
    assert "dataset_id: fluxonium-2025-031" in result.stdout
    assert "name: Fluxonium sweep 031" in result.stdout
    assert "storage_metadata_record_id: dataset:fluxonium-2025-031" in result.stdout


def test_datasets_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["datasets", "show", "transmon-coupler-014", "--output", "json"])

    assert result.exit_code == 0
    assert '"dataset_id": "transmon-coupler-014"' in result.stdout
    assert '"device_type": "Transmon"' in result.stdout
    assert '"storage": {' in result.stdout


def test_datasets_set_metadata_command_updates_dataset_metadata() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "datasets",
            "set-metadata",
            "fluxonium-2025-031",
            "--device-type",
            "Fluxonium",
            "--source",
            "measured",
            "--capability",
            "sweep-ready",
            "--capability",
            "fit-ready",
        ],
    )

    assert result.exit_code == 0
    assert "updated_fields: device_type, capabilities, source" in result.stdout
    assert "device_type: Fluxonium" in result.stdout
    assert "source: measured" in result.stdout
    assert "- sweep-ready" in result.stdout
    assert "- fit-ready" in result.stdout


def test_datasets_set_metadata_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "datasets",
            "set-metadata",
            "transmon-coupler-014",
            "--device-type",
            "Transmon",
            "--source",
            "simulated",
            "--capability",
            "cross-resonance",
            "--capability",
            "detuning-scan",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"updated_fields": [' in result.stdout
    assert '"source": "simulated"' in result.stdout
    assert '"capabilities": [' in result.stdout
    assert '"detuning-scan"' in result.stdout


def test_datasets_set_metadata_command_uses_structured_validation_error() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "datasets",
            "set-metadata",
            "fluxonium-2025-031",
            "--device-type",
            "Fluxonium",
            "--source",
            "measured",
            "--capability",
            "duplicate-capability",
            "--capability",
            "duplicate-capability",
        ],
    )

    assert result.exit_code == 2
    assert (
        "error: Request validation failed. [validation/request_validation_failed]" in result.output
    )
    assert "field_error: capabilities:" in result.output


def test_tasks_list_command_reads_rewrite_task_state() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "list"])

    assert result.exit_code == 0
    assert "tasks:" in result.stdout
    assert "#301" in result.stdout
    assert "#303" in result.stdout
    assert "#304" not in result.stdout


def test_tasks_list_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "list", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 301' in result.stdout
    assert '"task_id": 303' in result.stdout
    assert '"task_id": 304' not in result.stdout


def test_tasks_show_command_reads_one_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "show", "301"])

    assert result.exit_code == 0
    assert "task_id: 301" in result.stdout
    assert "execution_mode: run" in result.stdout
    assert "worker_task_name: simulation_run_task" in result.stdout
    assert "request_ready: true" in result.stdout


def test_tasks_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "show", "301", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 301' in result.stdout
    assert '"metadata_records": []' in result.stdout
    assert '"result_handles": []' in result.stdout
    assert '"events": [' in result.stdout


def test_tasks_inspect_command_groups_operator_view() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "inspect", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "inspection:" in result.stdout
    assert "event_count: 2" in result.stdout
    assert "latest_event_type: task_completed" in result.stdout
    assert "result_handle_count: 2" in result.stdout


def test_tasks_inspect_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "inspect", "303", "--output", "json"])

    assert result.exit_code == 0
    assert '"task": {' in result.stdout
    assert '"inspection": {' in result.stdout
    assert '"event_count": 2' in result.stdout


def test_tasks_latest_command_reads_latest_matching_task() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["tasks", "latest", "--lane", "simulation", "--status", "completed"],
    )

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "lane: simulation" in result.stdout
    assert "status: completed" in result.stdout


def test_tasks_wait_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "tasks",
            "wait",
            "303",
            "--until-status",
            "completed",
            "--interval",
            "0.1",
            "--timeout",
            "0.2",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"status": "completed"' in result.stdout


def test_ops_inspect_command_groups_connected_operator_bundle() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["ops", "inspect", "303"])

    assert result.exit_code == 0
    assert "inspection:" in result.stdout
    assert "recent_events:" in result.stdout
    assert "result_summary:" in result.stdout
    assert "result_handle_ids: result:fluxonium-2025-031:fit-summary" in result.stdout


def test_ops_latest_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["ops", "latest", "--lane", "simulation", "--status", "completed", "--output", "json"],
    )

    assert result.exit_code == 0
    assert '"task": {' in result.stdout
    assert '"inspection": {' in result.stdout
    assert '"recent_events": [' in result.stdout
    assert '"result_summary": {' in result.stdout


def test_ops_wait_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "ops",
            "wait",
            "303",
            "--until-status",
            "completed",
            "--interval",
            "0.1",
            "--timeout",
            "0.2",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"task": {' in result.stdout
    assert '"recent_events": [' in result.stdout
    assert '"event_type": "task_completed"' in result.stdout


def test_ops_submit_command_can_wait_for_requested_status() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "ops",
            "submit",
            "characterization",
            "--dataset-id",
            "transmon-coupler-014",
            "--wait",
            "--until-status",
            "queued",
            "--interval",
            "0.1",
            "--timeout",
            "0.2",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"task": {' in result.stdout
    assert '"kind": "characterization"' in result.stdout
    assert '"status": "queued"' in result.stdout
    assert '"recent_events": [' in result.stdout
    assert '"result_summary": {' in result.stdout


def test_events_show_command_groups_persisted_task_history() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["events", "show", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "event_count: 2" in result.stdout
    assert "event_type: task_submitted" in result.stdout
    assert "event_type: task_completed" in result.stdout
    assert "result_handle_ids:" in result.stdout
    assert "result:fluxonium-2025-031:fit-summary" in result.stdout
    assert "result:fluxonium-2025-031:plot-bundle" in result.stdout


def test_events_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["events", "show", "303", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"event_count": 2' in result.stdout
    assert '"event_type": "task_completed"' in result.stdout


def test_events_show_command_supports_event_type_filters() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["events", "show", "301", "--event-type", "task_running"])

    assert result.exit_code == 0
    assert "event_type: task_running" in result.stdout
    assert "event_type: task_submitted" not in result.stdout


def test_events_latest_command_reads_latest_persisted_event() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["events", "latest", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "latest_event:" in result.stdout
    assert "event_type: task_completed" in result.stdout
    assert "occurred_at: 2026-03-11 19:18:00" in result.stdout


def test_events_latest_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["events", "latest", "303", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"event": {' in result.stdout
    assert '"event_type": "task_completed"' in result.stdout


def test_events_show_command_rejects_empty_filtered_history() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["events", "show", "301", "--level", "error"])

    assert result.exit_code == 1
    assert "error: No persisted task events matched the requested filters for 301." in result.output


def test_results_show_command_groups_persisted_result_refs() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "show", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "trace_batch_id: 88" in result.stdout
    assert "metadata_record_count: 2" in result.stdout
    assert "result_handle_count: 2" in result.stdout
    assert "result:fluxonium-2025-031:fit-summary" in result.stdout


def test_results_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "show", "303", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"result_refs": {' in result.stdout
    assert '"trace_batch_id": 88' in result.stdout
    assert '"result_handles": [' in result.stdout


def test_results_trace_command_reads_trace_payload() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "trace", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "backend: local_zarr" in result.stdout
    assert (
        "store_uri: trace_store/datasets/fluxonium-2025-031/trace-batches/88.zarr" in result.stdout
    )
    assert "shape: 184, 1024" in result.stdout


def test_results_trace_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "trace", "303", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"trace_payload": {' in result.stdout
    assert '"store_key": "datasets/fluxonium-2025-031/trace-batches/88.zarr"' in result.stdout


def test_results_handles_command_reads_persisted_handles() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "handles", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "result_handle_count: 2" in result.stdout
    assert "handle_id: result:fluxonium-2025-031:fit-summary" in result.stdout
    assert "payload_locator: artifacts/fit-summary.json" in result.stdout
    assert "handle_id: result:fluxonium-2025-031:plot-bundle" in result.stdout


def test_results_handles_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "handles", "303", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"metadata_records": [' in result.stdout
    assert '"handle_id": "result:fluxonium-2025-031:fit-summary"' in result.stdout


def test_results_trace_command_rejects_tasks_without_trace_payload() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "trace", "301"])

    assert result.exit_code == 1
    assert "error: Task 301 does not expose a persisted trace payload." in result.output


def test_results_handles_command_rejects_tasks_without_result_handles() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["results", "handles", "301"])

    assert result.exit_code == 1
    assert "error: Task 301 does not expose persisted result handles." in result.output


def test_simulation_show_command_reads_simulation_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["simulation", "show", "301"])

    assert result.exit_code == 0
    assert "task_id: 301" in result.stdout
    assert "lane: simulation" in result.stdout
    assert "kind: simulation" in result.stdout


def test_simulation_inspect_command_groups_operator_view() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["simulation", "inspect", "303"])

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "inspection:" in result.stdout
    assert "latest_event_type: task_completed" in result.stdout


def test_simulation_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["simulation", "show", "301", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 301' in result.stdout
    assert '"lane": "simulation"' in result.stdout


def test_simulation_latest_command_reads_latest_simulation_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["simulation", "latest", "--status", "running"])

    assert result.exit_code == 0
    assert "task_id: 301" in result.stdout
    assert "lane: simulation" in result.stdout


def test_simulation_latest_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app, ["simulation", "latest", "--status", "completed", "--output", "json"]
    )

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"kind": "post_processing"' in result.stdout
    assert '"lane": "simulation"' in result.stdout


def test_simulation_submit_command_submits_simulation_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["simulation", "submit", "--definition-id", "18"])

    assert result.exit_code == 0
    assert "kind: simulation" in result.stdout
    assert "lane: simulation" in result.stdout
    assert "worker_task_name: simulation_smoke_task" in result.stdout


def test_simulation_submit_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["simulation", "submit", "--definition-id", "18", "--output", "json"],
    )

    assert result.exit_code == 0
    assert '"kind": "simulation"' in result.stdout
    assert '"lane": "simulation"' in result.stdout
    assert '"definition_id": 18' in result.stdout


def test_simulation_wait_command_returns_terminal_simulation_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["simulation", "wait", "303", "--interval", "0.1", "--timeout", "0.2"],
    )

    assert result.exit_code == 0
    assert "task_id: 303" in result.stdout
    assert "status: completed" in result.stdout
    assert "lane: simulation" in result.stdout


def test_simulation_wait_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["simulation", "wait", "303", "--interval", "0.1", "--timeout", "0.2", "--output", "json"],
    )

    assert result.exit_code == 0
    assert '"task_id": 303' in result.stdout
    assert '"status": "completed"' in result.stdout
    assert '"lane": "simulation"' in result.stdout


def test_simulation_wait_command_supports_until_status_option() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "simulation",
            "wait",
            "301",
            "--until-status",
            "running",
            "--interval",
            "0.1",
            "--timeout",
            "0.2",
        ],
    )

    assert result.exit_code == 0
    assert "task_id: 301" in result.stdout
    assert "status: running" in result.stdout


def test_simulation_show_command_rejects_non_simulation_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["simulation", "show", "302"])

    assert result.exit_code == 1
    assert "error: Task 302 is not part of the simulation lane." in result.output


def test_characterization_show_command_reads_characterization_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["characterization", "show", "302"])

    assert result.exit_code == 0
    assert "task_id: 302" in result.stdout
    assert "lane: characterization" in result.stdout
    assert "kind: characterization" in result.stdout


def test_characterization_inspect_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["characterization", "inspect", "302", "--output", "json"])

    assert result.exit_code == 0
    assert '"task": {' in result.stdout
    assert '"inspection": {' in result.stdout
    assert '"lane": "characterization"' in result.stdout


def test_characterization_show_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["characterization", "show", "302", "--output", "json"])

    assert result.exit_code == 0
    assert '"task_id": 302' in result.stdout
    assert '"lane": "characterization"' in result.stdout


def test_characterization_latest_command_reads_latest_characterization_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["characterization", "latest"])

    assert result.exit_code == 0
    assert "task_id:" in result.stdout
    assert "kind: characterization" in result.stdout
    assert "lane: characterization" in result.stdout


def test_characterization_latest_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["characterization", "latest", "--status", "queued", "--output", "json"],
    )

    assert result.exit_code == 0
    assert '"lane": "characterization"' in result.stdout
    assert '"kind": "characterization"' in result.stdout


def test_characterization_submit_command_submits_characterization_task() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["characterization", "submit", "--dataset-id", "transmon-coupler-014"],
    )

    assert result.exit_code == 0
    assert "kind: characterization" in result.stdout
    assert "lane: characterization" in result.stdout
    assert "worker_task_name: characterization_run_task" in result.stdout


def test_characterization_submit_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["characterization", "submit", "--dataset-id", "transmon-coupler-014", "--output", "json"],
    )

    assert result.exit_code == 0
    assert '"kind": "characterization"' in result.stdout
    assert '"lane": "characterization"' in result.stdout
    assert '"dataset_id": "transmon-coupler-014"' in result.stdout


def test_characterization_wait_command_reaches_requested_status() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "characterization",
            "wait",
            "302",
            "--until-status",
            "queued",
            "--interval",
            "0.1",
            "--timeout",
            "0.2",
        ],
    )

    assert result.exit_code == 0
    assert "task_id: 302" in result.stdout
    assert "status: queued" in result.stdout
    assert "lane: characterization" in result.stdout


def test_characterization_wait_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "characterization",
            "wait",
            "302",
            "--until-status",
            "queued",
            "--interval",
            "0.1",
            "--timeout",
            "0.2",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"task_id": 302' in result.stdout
    assert '"status": "queued"' in result.stdout
    assert '"lane": "characterization"' in result.stdout


def test_characterization_show_command_rejects_non_characterization_lane_task() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["characterization", "show", "301"])

    assert result.exit_code == 1
    assert "error: Task 301 is not part of the characterization lane." in result.output


def test_tasks_submit_command_submits_simulation_task() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["tasks", "submit", "simulation", "--definition-id", "18"],
    )

    assert result.exit_code == 0
    assert "kind: simulation" in result.stdout
    assert "definition_id: 18" in result.stdout
    assert "status: queued" in result.stdout
    assert "worker_task_name: simulation_smoke_task" in result.stdout
    assert "request_ready: false" in result.stdout


def test_tasks_submit_command_supports_json_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "tasks",
            "submit",
            "characterization",
            "--dataset-id",
            "transmon-coupler-014",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"kind": "characterization"' in result.stdout
    assert '"dataset_id": "transmon-coupler-014"' in result.stdout
    assert '"status": "queued"' in result.stdout


def test_tasks_submit_command_uses_structured_backend_error_message() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "submit", "simulation"])

    assert result.exit_code == 2
    assert (
        "error: Simulation tasks require definition_id. [validation/simulation_definition_required]"
    ) in result.output


def test_tasks_submit_command_uses_structured_backend_error_json() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "submit", "simulation", "--output", "json"])

    assert result.exit_code == 2
    assert '"error": {' in result.output
    assert '"code": "simulation_definition_required"' in result.output
    assert '"category": "validation"' in result.output


def test_tasks_show_command_uses_structured_backend_error_message() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "show", "999"])

    assert result.exit_code == 2
    assert "error: Task 999 was not found. [not_found/task_not_found]" in result.output


def test_tasks_show_command_uses_structured_backend_error_json() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["tasks", "show", "999", "--output", "json"])

    assert result.exit_code == 2
    assert '"error": {' in result.output
    assert '"code": "task_not_found"' in result.output
    assert '"category": "not_found"' in result.output


def test_session_set_active_dataset_command_uses_structured_backend_error_message() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["session", "set-active-dataset", "missing-dataset"])

    assert result.exit_code == 2
    assert (
        "error: Dataset missing-dataset was not found. [not_found/dataset_not_found]"
        in result.output
    )


def test_session_set_active_dataset_command_uses_structured_backend_error_json() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["session", "set-active-dataset", "missing-dataset", "--output", "json"],
    )

    assert result.exit_code == 2
    assert '"error": {' in result.output
    assert '"code": "dataset_not_found"' in result.output
    assert '"category": "not_found"' in result.output


def test_session_show_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(
        session,
        "get_session",
        lambda: _raise_backend_error("Session lookup failed."),
    )

    result = runner.invoke(app, ["session", "show"])

    assert result.exit_code == 2
    assert "error: Session lookup failed. [validation/request_failed]" in result.output


def test_datasets_list_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(
        datasets,
        "list_datasets",
        lambda **_: _raise_backend_error("Dataset read failed."),
    )

    result = runner.invoke(app, ["datasets", "list"])

    assert result.exit_code == 2
    assert "error: Dataset read failed. [validation/request_failed]" in result.output


def test_tasks_list_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(tasks, "list_tasks", lambda **_: _raise_backend_error("Task list failed."))

    result = runner.invoke(app, ["tasks", "list"])

    assert result.exit_code == 2
    assert "error: Task list failed. [validation/request_failed]" in result.output


def test_simulation_wait_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(simulation, "get_task", lambda _: _raise_backend_error("Task read failed."))

    result = runner.invoke(app, ["simulation", "wait", "301"])

    assert result.exit_code == 2
    assert "error: Task read failed. [validation/request_failed]" in result.output


def test_characterization_wait_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(
        characterization,
        "get_task",
        lambda _: _raise_backend_error("Task read failed."),
    )

    result = runner.invoke(app, ["characterization", "wait", "302"])

    assert result.exit_code == 2
    assert "error: Task read failed. [validation/request_failed]" in result.output


def test_results_show_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(results, "get_task", lambda _: _raise_backend_error("Task read failed."))

    result = runner.invoke(app, ["results", "show", "303"])

    assert result.exit_code == 2
    assert "error: Task read failed. [validation/request_failed]" in result.output


def test_events_show_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(events, "get_task", lambda _: _raise_backend_error("Task read failed."))

    result = runner.invoke(app, ["events", "show", "303"])

    assert result.exit_code == 2
    assert "error: Task read failed. [validation/request_failed]" in result.output


def test_ops_inspect_command_handles_backend_contract_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr(ops, "get_task", lambda _: _raise_backend_error("Task read failed."))

    result = runner.invoke(app, ["ops", "inspect", "303"])

    assert result.exit_code == 2
    assert "error: Task read failed. [validation/request_failed]" in result.output


def _backend_error(message: str) -> BackendContractError:
    return BackendContractError(
        ApiErrorBodyResponse(
            code="request_failed",
            category="validation",
            message=message,
            status=422,
        )
    )


def _raise_backend_error(message: str) -> None:
    raise _backend_error(message)
