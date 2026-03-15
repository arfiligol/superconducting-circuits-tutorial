from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from sc_cli.app import app
from sc_cli.local_circuit_definitions import (
    get_local_circuit_definition,
    reload_local_circuit_definition_state,
)
from sc_cli.local_runtime import reload_runtime_state
from sc_cli.local_store import (
    bundle_receipts_path,
    definition_catalog_path,
    task_events_path,
    task_registry_path,
    task_results_path,
)
from sc_cli.runtime import (
    get_session,
    get_task,
    reset_runtime_state,
    set_active_dataset,
    submit_task,
)


def _canonical_definition_source(name: str) -> str:
    return "\n".join(
        [
            f"name: {name}",
            "components:",
            "  - name: R1",
            "    default: 50.0",
            "    unit: Ohm",
            "  - name: C1",
            "    default: 100.0",
            "    unit: fF",
            "topology:",
            '  - [P1, "1", "0", 1]',
            '  - [R1, "1", "0", "R1"]',
            '  - [C1, "1", "0", "C1"]',
        ]
    )


def test_local_task_registry_persists_across_restart_reload() -> None:
    reset_runtime_state()
    set_active_dataset("transmon-coupler-014")
    submitted_task = submit_task(
        kind="characterization",
        summary="Persisted characterization",
    )

    assert task_registry_path().exists()
    assert task_events_path(submitted_task.task_id).exists()
    assert task_results_path(submitted_task.task_id).exists()

    reload_runtime_state()
    session = get_session()
    rehydrated_task = get_task(submitted_task.task_id)

    assert session.workspace.active_dataset is not None
    assert session.workspace.active_dataset.dataset_id == "transmon-coupler-014"
    assert rehydrated_task.task_id == submitted_task.task_id
    assert rehydrated_task.lane == "characterization"
    assert rehydrated_task.status == "queued"
    assert rehydrated_task.dataset_id == "transmon-coupler-014"
    assert len(rehydrated_task.events) == 1

    runner = CliRunner()
    show_result = runner.invoke(
        app,
        ["tasks", "show", str(submitted_task.task_id), "--output", "json"],
    )
    wait_result = runner.invoke(
        app,
        [
            "tasks",
            "wait",
            str(submitted_task.task_id),
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

    assert show_result.exit_code == 0
    assert json.loads(show_result.stdout)["task_id"] == submitted_task.task_id
    assert wait_result.exit_code == 0
    assert json.loads(wait_result.stdout)["task_id"] == submitted_task.task_id


def test_seeded_results_and_events_rehydrate_from_persisted_store() -> None:
    reset_runtime_state()

    registry_payload = json.loads(task_registry_path().read_text(encoding="utf-8"))
    task_ids = {task["task_id"] for task in registry_payload["tasks"]}
    assert 303 in task_ids
    assert task_events_path(303).exists()
    assert task_results_path(303).exists()

    reload_runtime_state()
    task = get_task(303)

    assert task.status == "completed"
    assert [event.event_type for event in task.events] == [
        "task_submitted",
        "task_completed",
    ]
    assert task.result_refs.trace_payload is not None
    assert len(task.result_refs.result_handles) == 2

    runner = CliRunner()
    inspect_result = runner.invoke(app, ["tasks", "inspect", "303", "--output", "json"])
    results_result = runner.invoke(app, ["results", "show", "303", "--output", "json"])
    events_result = runner.invoke(app, ["events", "show", "303", "--output", "json"])

    assert inspect_result.exit_code == 0
    assert json.loads(inspect_result.stdout)["task"]["task_id"] == 303
    assert results_result.exit_code == 0
    assert json.loads(results_result.stdout)["result_refs"]["trace_batch_id"] == 88
    assert events_result.exit_code == 0
    assert json.loads(events_result.stdout)["event_count"] == 2


def test_definition_catalog_and_bundle_receipts_persist_across_reload(tmp_path: Path) -> None:
    reset_runtime_state()
    runner = CliRunner()

    source_file = tmp_path / "persisted-definition.circuit.yaml"
    source_file.write_text(
        _canonical_definition_source("PersistedDefinition"),
        encoding="utf-8",
    )
    create_result = runner.invoke(
        app,
        [
            "circuit-definition",
            "create",
            str(source_file),
            "--name",
            "PersistedDefinition",
            "--output",
            "json",
        ],
    )
    assert create_result.exit_code == 0
    created_definition_id = json.loads(create_result.stdout)["definition_id"]

    bundle_file = tmp_path / "persisted-definition.bundle.json"
    export_result = runner.invoke(
        app,
        [
            "circuit-definition",
            "export-bundle",
            str(created_definition_id),
            str(bundle_file),
            "--output",
            "json",
        ],
    )
    assert export_result.exit_code == 0
    import_result = runner.invoke(
        app,
        [
            "circuit-definition",
            "import-bundle",
            str(bundle_file),
            "--output",
            "json",
        ],
    )
    assert import_result.exit_code == 0
    imported_definition_id = json.loads(import_result.stdout)["imported_definition"][
        "definition_id"
    ]

    assert definition_catalog_path().exists()
    receipts = json.loads(bundle_receipts_path().read_text(encoding="utf-8"))
    definition_receipts = [
        entry
        for entry in receipts
        if entry["bundle_family"] == "definition_bundle"
    ]
    assert [entry["operation"] for entry in definition_receipts[-2:]] == ["export", "import"]

    reload_local_circuit_definition_state()
    created_definition = get_local_circuit_definition(created_definition_id)
    imported_definition = get_local_circuit_definition(imported_definition_id)

    assert created_definition.name == "PersistedDefinition"
    assert imported_definition.lineage is not None
    assert imported_definition.lineage.imported_from_bundle_id is not None

    inspect_result = runner.invoke(
        app,
        [
            "circuit-definition",
            "inspect",
            "--definition-id",
            str(imported_definition_id),
            "--output",
            "json",
        ],
    )

    assert inspect_result.exit_code == 0
    assert json.loads(inspect_result.stdout)["definition_id"] == imported_definition_id
