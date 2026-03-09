"""Lazy worker-task enqueue helpers used by API and future CLI surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from app.services.post_processing_task_contract import (
    extract_post_processing_request_from_api_payload,
)
from app.services.simulation_task_contract import extract_simulation_request_from_api_payload

LaneName = Literal["simulation", "characterization"]
TaskSubmissionKind = Literal["simulation", "post_processing", "characterization"]


@dataclass(frozen=True)
class DispatchedWorkerTask:
    """Dispatch metadata returned after enqueuing one task."""

    lane: LaneName
    worker_task_name: str


def enqueue_task(
    task_kind: TaskSubmissionKind,
    *,
    task_id: int,
    request_payload: dict[str, Any] | None = None,
    trace_batch_id: int | None = None,
) -> DispatchedWorkerTask:
    """Enqueue one persisted task to its frozen worker lane."""
    if task_kind == "simulation":
        parameters = (
            dict(request_payload.get("parameters", {}))
            if (
                isinstance(request_payload, dict)
                and isinstance(request_payload.get("parameters"), dict)
            )
            else {}
        )
        simulation_request = extract_simulation_request_from_api_payload(parameters)
        if simulation_request is not None and trace_batch_id is not None:
            from worker.simulation_tasks import simulation_run_task

            simulation_run_task(task_id)
            return DispatchedWorkerTask(
                lane="simulation",
                worker_task_name="simulation_run_task",
            )

        from worker.simulation_tasks import simulation_smoke_task

        simulation_smoke_task(task_id)
        return DispatchedWorkerTask(
            lane="simulation",
            worker_task_name="simulation_smoke_task",
        )

    if task_kind == "post_processing":
        parameters = (
            dict(request_payload.get("parameters", {}))
            if (
                isinstance(request_payload, dict)
                and isinstance(request_payload.get("parameters"), dict)
            )
            else {}
        )
        post_processing_request = extract_post_processing_request_from_api_payload(parameters)
        if post_processing_request is not None and trace_batch_id is not None:
            from worker.simulation_tasks import post_processing_run_task

            post_processing_run_task(task_id)
            return DispatchedWorkerTask(
                lane="simulation",
                worker_task_name="post_processing_run_task",
            )

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
