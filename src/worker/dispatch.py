"""Lazy worker-task enqueue helpers used by API and future CLI surfaces."""

from __future__ import annotations

from typing import Any, Literal

from sc_core.tasking import (
    WorkerDispatchPlan,
    build_worker_dispatch_plan,
    extract_parameters_payload,
    resolve_worker_task_route,
)

from app.services.characterization_task_contract import (
    extract_characterization_request_from_api_payload,
)
from app.services.post_processing_task_contract import (
    extract_post_processing_request_from_api_payload,
)
from app.services.simulation_task_contract import extract_simulation_request_from_api_payload
from worker.config import create_queue

LaneName = Literal["simulation", "characterization"]
TaskSubmissionKind = Literal["simulation", "post_processing", "characterization"]
DispatchedWorkerTask = WorkerDispatchPlan


def enqueue_task(
    task_kind: TaskSubmissionKind,
    *,
    task_id: int,
    request_payload: dict[str, Any] | None = None,
    trace_batch_id: int | None = None,
) -> DispatchedWorkerTask:
    """Enqueue one persisted task to its frozen worker lane."""
    parameters = extract_parameters_payload(request_payload)
    request_is_valid = _request_is_valid(task_kind=task_kind, parameters=parameters)
    dispatch = build_worker_dispatch_plan(
        resolve_worker_task_route(
            task_kind,
            request_is_valid=request_is_valid,
            has_trace_batch_id=trace_batch_id is not None,
        )
    )
    task_callable = dispatch.worker_task_name
    queue = create_queue(dispatch.queue_name)
    if task_callable == "simulation_run_task":
        from worker.simulation_tasks import simulation_run_task

        queue.enqueue(
            simulation_run_task,
            task_id,
            job_timeout=dispatch.job_timeout,
            failure_ttl=dispatch.failure_ttl,
            result_ttl=dispatch.result_ttl,
        )
        return dispatch
    if task_callable == "simulation_smoke_task":
        from worker.simulation_tasks import simulation_smoke_task

        queue.enqueue(
            simulation_smoke_task,
            task_id,
            job_timeout=dispatch.job_timeout,
            failure_ttl=dispatch.failure_ttl,
            result_ttl=dispatch.result_ttl,
        )
        return dispatch
    if task_callable == "post_processing_run_task":
        from worker.simulation_tasks import post_processing_run_task

        queue.enqueue(
            post_processing_run_task,
            task_id,
            job_timeout=dispatch.job_timeout,
            failure_ttl=dispatch.failure_ttl,
            result_ttl=dispatch.result_ttl,
        )
        return dispatch
    if task_callable == "post_processing_smoke_task":
        from worker.simulation_tasks import post_processing_smoke_task

        queue.enqueue(
            post_processing_smoke_task,
            task_id,
            job_timeout=dispatch.job_timeout,
            failure_ttl=dispatch.failure_ttl,
            result_ttl=dispatch.result_ttl,
        )
        return dispatch
    if task_callable == "characterization_run_task":
        from worker.characterization_tasks import characterization_run_task

        queue.enqueue(
            characterization_run_task,
            task_id,
            job_timeout=dispatch.job_timeout,
            failure_ttl=dispatch.failure_ttl,
            result_ttl=dispatch.result_ttl,
        )
        return dispatch
    if task_callable == "characterization_smoke_task":
        from worker.characterization_tasks import characterization_smoke_task

        queue.enqueue(
            characterization_smoke_task,
            task_id,
            job_timeout=dispatch.job_timeout,
            failure_ttl=dispatch.failure_ttl,
            result_ttl=dispatch.result_ttl,
        )
        return dispatch
    raise ValueError(f"Unsupported worker task '{task_callable}'.")


def _request_is_valid(
    *,
    task_kind: TaskSubmissionKind,
    parameters: dict[str, object],
) -> bool:
    if task_kind == "simulation":
        return extract_simulation_request_from_api_payload(parameters) is not None
    if task_kind == "post_processing":
        return extract_post_processing_request_from_api_payload(parameters) is not None
    if task_kind == "characterization":
        return extract_characterization_request_from_api_payload(parameters) is not None
    raise ValueError(f"Unsupported task kind '{task_kind}'.")
