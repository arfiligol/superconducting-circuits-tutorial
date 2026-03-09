"""Lazy worker-task enqueue helpers used by API and future CLI surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LaneName = Literal["simulation", "characterization"]
TaskSubmissionKind = Literal["simulation", "post_processing", "characterization"]


@dataclass(frozen=True)
class DispatchedWorkerTask:
    """Dispatch metadata returned after enqueuing one task."""

    lane: LaneName
    worker_task_name: str


def enqueue_task(task_kind: TaskSubmissionKind, *, task_id: int) -> DispatchedWorkerTask:
    """Enqueue one persisted task to its frozen worker lane."""
    if task_kind == "simulation":
        from worker.simulation_tasks import simulation_smoke_task

        simulation_smoke_task(task_id)
        return DispatchedWorkerTask(
            lane="simulation",
            worker_task_name="simulation_smoke_task",
        )

    if task_kind == "post_processing":
        from worker.simulation_tasks import post_processing_smoke_task

        post_processing_smoke_task(task_id)
        return DispatchedWorkerTask(
            lane="simulation",
            worker_task_name="post_processing_smoke_task",
        )

    if task_kind == "characterization":
        from worker.characterization_tasks import characterization_smoke_task

        characterization_smoke_task(task_id)
        return DispatchedWorkerTask(
            lane="characterization",
            worker_task_name="characterization_smoke_task",
        )

    raise ValueError(f"Unsupported task kind '{task_kind}'.")
