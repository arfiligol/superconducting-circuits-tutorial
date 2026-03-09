"""Simulation-lane smoke and failure tasks."""

from __future__ import annotations

import os
from typing import Any

from worker.runtime import TaskExecutionResult, execute_managed_task, mark_task_running_before_crash
from worker.simulation_huey import huey

_LANE_NAME = "simulation"


@huey.task(retries=0)
def simulation_smoke_task(task_id: int) -> dict[str, Any]:
    """Queue one minimal successful task lifecycle round-trip."""
    return execute_managed_task(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="simulation_smoke_task",
        operation=lambda: TaskExecutionResult(
            result_summary_payload={"smoke_result": "ok"},
        ),
    )


@huey.task(retries=0)
def post_processing_smoke_task(task_id: int) -> dict[str, Any]:
    """Queue one minimal post-processing lifecycle round-trip on the simulation lane."""
    return execute_managed_task(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="post_processing_smoke_task",
        operation=lambda: TaskExecutionResult(
            result_summary_payload={
                "smoke_result": "ok",
                "flow": "post_processing",
            },
        ),
    )


@huey.task(retries=0)
def simulation_failure_task(
    task_id: int,
    message: str = "simulation smoke failure",
) -> dict[str, Any]:
    """Queue one task that fails with a structured Python exception payload."""
    return execute_managed_task(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="simulation_failure_task",
        operation=lambda: (_ for _ in ()).throw(RuntimeError(message)),
    )


@huey.task(retries=0)
def simulation_crash_task(task_id: int, exit_code: int = 86) -> None:
    """Queue one task that intentionally crashes the worker process."""
    mark_task_running_before_crash(
        task_id=task_id,
        lane_name=_LANE_NAME,
        worker_task_name="simulation_crash_task",
    )
    os._exit(int(exit_code))
