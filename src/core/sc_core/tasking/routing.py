from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

LaneName = Literal["simulation", "characterization"]
TaskSubmissionKind = Literal["simulation", "post_processing", "characterization"]
TaskExecutionMode = Literal["run", "smoke"]
WorkerTaskName = Literal[
    "simulation_run_task",
    "simulation_smoke_task",
    "simulation_failure_task",
    "simulation_crash_task",
    "post_processing_run_task",
    "post_processing_smoke_task",
    "characterization_run_task",
    "characterization_smoke_task",
    "characterization_failure_task",
    "characterization_crash_task",
]


@dataclass(frozen=True)
class WorkerTaskRoute:
    """Canonical route metadata for one persisted task submission."""

    task_kind: TaskSubmissionKind
    lane: LaneName
    worker_task_name: WorkerTaskName
    execution_mode: TaskExecutionMode
    request_ready: bool
    requires_trace_batch: bool


@dataclass(frozen=True)
class WorkerDispatchPlan:
    """Canonical queue-dispatch plan for one persisted task submission."""

    lane: LaneName
    queue_name: LaneName
    worker_task_name: WorkerTaskName
    execution_mode: TaskExecutionMode
    request_ready: bool
    requires_trace_batch: bool
    job_timeout: int = -1
    failure_ttl: int = 86400
    result_ttl: int = 3600


def extract_parameters_payload(request_payload: Mapping[str, object] | None) -> dict[str, object]:
    """Return a shallow parameters payload from one task request body."""
    if request_payload is None:
        return {}

    raw_parameters = request_payload.get("parameters")
    if not isinstance(raw_parameters, Mapping):
        return {}

    return {key: value for key, value in raw_parameters.items() if isinstance(key, str)}


def resolve_worker_task_route(
    task_kind: TaskSubmissionKind,
    *,
    request_is_valid: bool,
    has_trace_batch_id: bool,
) -> WorkerTaskRoute:
    """Resolve the canonical worker lane and callable name for one task submission."""
    if task_kind == "simulation":
        return _build_route(
            task_kind=task_kind,
            lane="simulation",
            run_task_name="simulation_run_task",
            smoke_task_name="simulation_smoke_task",
            request_is_valid=request_is_valid,
            has_trace_batch_id=has_trace_batch_id,
            requires_trace_batch=True,
        )

    if task_kind == "post_processing":
        return _build_route(
            task_kind=task_kind,
            lane="simulation",
            run_task_name="post_processing_run_task",
            smoke_task_name="post_processing_smoke_task",
            request_is_valid=request_is_valid,
            has_trace_batch_id=has_trace_batch_id,
            requires_trace_batch=True,
        )

    if task_kind == "characterization":
        return _build_route(
            task_kind=task_kind,
            lane="characterization",
            run_task_name="characterization_run_task",
            smoke_task_name="characterization_smoke_task",
            request_is_valid=request_is_valid,
            has_trace_batch_id=has_trace_batch_id,
            requires_trace_batch=False,
        )

    raise ValueError(f"Unsupported task kind '{task_kind}'.")


def build_worker_dispatch_plan(
    route: WorkerTaskRoute,
    *,
    job_timeout: int = -1,
    failure_ttl: int = 86400,
    result_ttl: int = 3600,
) -> WorkerDispatchPlan:
    """Build the canonical queue-dispatch plan for one resolved worker route."""
    return WorkerDispatchPlan(
        lane=route.lane,
        queue_name=route.lane,
        worker_task_name=route.worker_task_name,
        execution_mode=route.execution_mode,
        request_ready=route.request_ready,
        requires_trace_batch=route.requires_trace_batch,
        job_timeout=job_timeout,
        failure_ttl=failure_ttl,
        result_ttl=result_ttl,
    )


def _build_route(
    *,
    task_kind: TaskSubmissionKind,
    lane: LaneName,
    run_task_name: WorkerTaskName,
    smoke_task_name: WorkerTaskName,
    request_is_valid: bool,
    has_trace_batch_id: bool,
    requires_trace_batch: bool,
) -> WorkerTaskRoute:
    request_ready = request_is_valid and (has_trace_batch_id or not requires_trace_batch)
    return WorkerTaskRoute(
        task_kind=task_kind,
        lane=lane,
        worker_task_name=run_task_name if request_ready else smoke_task_name,
        execution_mode="run" if request_ready else "smoke",
        request_ready=request_ready,
        requires_trace_batch=requires_trace_batch,
    )
