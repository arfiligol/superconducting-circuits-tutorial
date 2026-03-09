"""Worker-lane integration tests for WS3 smoke, failure, and crash semantics."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from core.shared.persistence import database
from core.shared.persistence.models import DesignRecord
from core.shared.persistence.reconcile import reconcile_stale_tasks_and_batches
from core.shared.persistence.unit_of_work import get_unit_of_work

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _utcnow() -> datetime:
    """Return one naive UTC timestamp without using deprecated utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


def _configure_worker_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SC_DATABASE_PATH", str(tmp_path / "database.db"))
    monkeypatch.setenv("SC_SIMULATION_HUEY_DB_PATH", str(tmp_path / "simulation_huey.db"))
    monkeypatch.setenv(
        "SC_CHARACTERIZATION_HUEY_DB_PATH",
        str(tmp_path / "characterization_huey.db"),
    )
    database.get_engine.cache_clear()


def _reload_worker_modules() -> tuple[object, object, object, object]:
    for module_name in [
        "worker.characterization_tasks",
        "worker.characterization_huey",
        "worker.simulation_tasks",
        "worker.simulation_huey",
        "worker.runtime",
        "worker.config",
    ]:
        sys.modules.pop(module_name, None)

    simulation_huey = importlib.import_module("worker.simulation_huey")
    simulation_tasks = importlib.import_module("worker.simulation_tasks")
    characterization_huey = importlib.import_module("worker.characterization_huey")
    characterization_tasks = importlib.import_module("worker.characterization_tasks")
    return (
        simulation_huey,
        simulation_tasks,
        characterization_huey,
        characterization_tasks,
    )


def _create_task(task_kind: str) -> int:
    with get_unit_of_work() as uow:
        design = uow.datasets.add(
            DesignRecord(
                name=f"{task_kind}-design",
                source_meta={},
                parameters={},
            )
        )
        uow.flush()
        assert design.id is not None
        task = uow.tasks.create_task(
            task_kind,
            design.id,
            {"requested_via": "test"},
            "test",
        )
        uow.commit()
        assert task.id is not None
        return task.id


def test_lane_huey_paths_are_separate_from_app_db(tmp_path: Path, monkeypatch) -> None:
    _configure_worker_env(tmp_path, monkeypatch)
    simulation_huey, _simulation_tasks, characterization_huey, _characterization_tasks = (
        _reload_worker_modules()
    )

    assert str(simulation_huey.BROKER_PATH).endswith("simulation_huey.db")
    assert str(characterization_huey.BROKER_PATH).endswith("characterization_huey.db")
    assert simulation_huey.BROKER_PATH != characterization_huey.BROKER_PATH
    assert database.resolve_database_path() != simulation_huey.BROKER_PATH
    assert database.resolve_database_path() != characterization_huey.BROKER_PATH


def test_simulation_lane_smoke_task_round_trips_taskrecord(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _configure_worker_env(tmp_path, monkeypatch)
    simulation_huey, simulation_tasks, _characterization_huey, _characterization_tasks = (
        _reload_worker_modules()
    )
    task_id = _create_task("simulation_smoke")

    simulation_tasks.simulation_smoke_task(task_id)
    processed = simulation_huey.consume(max_tasks=1, idle_timeout=0.2, poll_interval=0.01)

    assert processed == 1
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        assert task is not None
        assert task.status == "completed"
        assert task.result_summary_payload["lane"] == "simulation"
        assert task.result_summary_payload["smoke_result"] == "ok"


def test_characterization_lane_smoke_task_round_trips_taskrecord(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _configure_worker_env(tmp_path, monkeypatch)
    _simulation_huey, _simulation_tasks, characterization_huey, characterization_tasks = (
        _reload_worker_modules()
    )
    task_id = _create_task("characterization_smoke")

    characterization_tasks.characterization_smoke_task(task_id)
    processed = characterization_huey.consume(max_tasks=1, idle_timeout=0.2, poll_interval=0.01)

    assert processed == 1
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        assert task is not None
        assert task.status == "completed"
        assert task.result_summary_payload["lane"] == "characterization"
        assert task.result_summary_payload["smoke_result"] == "ok"


def test_simulation_lane_failure_task_marks_failed(tmp_path: Path, monkeypatch) -> None:
    _configure_worker_env(tmp_path, monkeypatch)
    simulation_huey, simulation_tasks, _characterization_huey, _characterization_tasks = (
        _reload_worker_modules()
    )
    task_id = _create_task("simulation_failure")

    simulation_tasks.simulation_failure_task(task_id, "boom")
    processed = simulation_huey.consume(max_tasks=1, idle_timeout=0.2, poll_interval=0.01)

    assert processed == 1
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        assert task is not None
        assert task.status == "failed"
        assert task.error_payload["error_code"] == "worker_task_failed"
        assert task.error_payload["details"]["message"] == "boom"
        assert task.error_payload["details"]["lane"] == "simulation"


def test_crashed_worker_task_is_detected_as_stale(tmp_path: Path, monkeypatch) -> None:
    _configure_worker_env(tmp_path, monkeypatch)
    simulation_huey, simulation_tasks, _characterization_huey, _characterization_tasks = (
        _reload_worker_modules()
    )
    task_id = _create_task("simulation_crash")

    simulation_tasks.simulation_crash_task(task_id, 86)
    env = {
        **os.environ,
        "SC_DATABASE_PATH": str(database.resolve_database_path()),
        "SC_SIMULATION_HUEY_DB_PATH": str(simulation_huey.BROKER_PATH),
        "SC_CHARACTERIZATION_HUEY_DB_PATH": str(tmp_path / "characterization_huey.db"),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "worker.simulation_huey",
            "--max-tasks",
            "1",
            "--idle-timeout",
            "0.2",
        ],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 86

    with get_unit_of_work() as uow:
        running_task = uow.tasks.get_task(task_id)
        assert running_task is not None
        assert running_task.status == "running"
        running_task.heartbeat_at = _utcnow() - timedelta(minutes=10)
        uow.commit()

    with get_unit_of_work() as uow:
        summary = reconcile_stale_tasks_and_batches(
            uow,
            stale_before=_utcnow() - timedelta(minutes=5),
        )

    assert summary.stale_task_ids == [task_id]
    with get_unit_of_work() as uow:
        failed_task = uow.tasks.get_task(task_id)
        assert failed_task is not None
        assert failed_task.status == "failed"
        assert failed_task.error_payload["error_code"] == "stale_task_timeout"


def test_app_import_does_not_import_worker_or_julia_adapter_modules() -> None:
    env = {**os.environ, "PYTHON_JULIACALL_TRACE": "1"}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import app.main; "
                "print('APP_IMPORT_OK'); "
                "print('worker.simulation_huey' in sys.modules); "
                "print('worker.characterization_huey' in sys.modules); "
                "print('core.simulation.application.run_simulation' in sys.modules); "
                "print('core.simulation.infrastructure.julia_adapter' in sys.modules)"
            ),
        ],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    output_lines = result.stdout.strip().splitlines()
    assert output_lines == ["APP_IMPORT_OK", "False", "False", "True", "False"]
    combined_output = f"{result.stdout}\n{result.stderr}".lower()
    assert "juliacall" not in combined_output
