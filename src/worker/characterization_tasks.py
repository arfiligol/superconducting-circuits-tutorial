"""Characterization-lane smoke and failure tasks."""

from __future__ import annotations

import os
from typing import Any

from worker.characterization_execution import execute_characterization_task
from worker.characterization_huey import huey
from worker.runtime import TaskExecutionResult, execute_managed_task, mark_task_running_before_crash

_LANE_NAME = "characterization"


@huey.task(retries=0)
def characterization_run_task(task_id: int) -> dict[str, Any]:
    """Execute one real persisted characterization task on the characterization lane."""
    return execute_managed_task(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="characterization_run_task",
        operation=lambda: execute_characterization_task(task_id),
    )


@huey.task(retries=0)
def characterization_smoke_task(task_id: int) -> dict[str, Any]:
    """Queue one minimal successful characterization-lane lifecycle round-trip."""
    return execute_managed_task(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="characterization_smoke_task",
        operation=lambda: TaskExecutionResult(
            result_summary_payload={"smoke_result": "ok"},
        ),
    )


@huey.task(retries=0)
def characterization_failure_task(
    task_id: int,
    message: str = "characterization smoke failure",
) -> dict[str, Any]:
    """Queue one task that fails with a structured Python exception payload."""
    return execute_managed_task(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="characterization_failure_task",
        operation=lambda: (_ for _ in ()).throw(RuntimeError(message)),
    )


@huey.task(retries=0)
def characterization_crash_task(task_id: int, exit_code: int = 86) -> None:
    """Queue one task that intentionally crashes the characterization worker process."""
    mark_task_running_before_crash(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="characterization_crash_task",
    )
    os._exit(int(exit_code))
