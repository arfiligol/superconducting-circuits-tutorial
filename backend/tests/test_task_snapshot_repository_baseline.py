from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from alembic import command
from alembic.config import Config
from sc_core.tasking import resolve_worker_task_route
from src.app.domain.tasks import TaskCreateDraft
from src.app.infrastructure.persistence import (
    SqliteRewriteTaskSnapshotRepository,
    build_sqlite_database_url,
    create_metadata_session_factory,
)
from src.app.infrastructure.rewrite_app_state_repository import build_seed_tasks


def test_sqlite_task_snapshot_repository_round_trips_task_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "rewrite-task-repository.db"
    _upgrade_schema(database_path)
    repository = SqliteRewriteTaskSnapshotRepository(
        create_metadata_session_factory(str(database_path))
    )

    seeded_task = build_seed_tasks()[2]

    assert repository.has_tasks() is False
    persisted_seed = repository.save_task_snapshot(seeded_task)
    assert persisted_seed.task_id == seeded_task.task_id
    assert repository.has_tasks() is True
    assert repository.get_task(303) == persisted_seed
    assert repository.list_tasks() == (persisted_seed,)

    worker_route = resolve_worker_task_route(
        "characterization",
        request_is_valid=True,
        has_trace_batch_id=False,
    )
    created = repository.create_task(
        TaskCreateDraft(
            kind="characterization",
            lane=worker_route.lane,
            execution_mode=worker_route.execution_mode,
            owner_user_id="researcher-01",
            owner_display_name="Rewrite Local User",
            workspace_id="ws-device-lab",
            workspace_slug="device-lab",
            visibility_scope="workspace",
            dataset_id="fluxonium-2025-031",
            definition_id=None,
            summary="characterization task accepted for dataset fluxonium-2025-031.",
            worker_task_name=worker_route.worker_task_name,
            request_ready=worker_route.request_ready,
            submitted_from_active_dataset=True,
        )
    )
    assert created.task_id == 304
    assert created.status == "queued"
    assert created.progress.phase == "queued"
    assert created.result_refs.result_handles == ()
    assert repository.get_task(304) == created
    assert [task.task_id for task in repository.list_tasks()] == [303, 304]

    updated = repository.save_task_snapshot(
        replace(
            created,
            status="failed",
            summary="Persisted failure snapshot",
            progress=replace(
                created.progress,
                phase="failed",
                percent_complete=100,
                summary="Persisted failure summary.",
                updated_at="2026-03-12 11:05:00",
            ),
        )
    )
    assert updated.status == "failed"
    persisted_updated = repository.get_task(304)
    assert persisted_updated is not None
    assert persisted_updated.progress.summary == "Persisted failure summary."


def _upgrade_schema(database_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", build_sqlite_database_url(database_path))
    command.upgrade(config, "head")
