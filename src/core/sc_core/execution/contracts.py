from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from sc_core.tasking import LaneName, WorkerTaskName

ExecutionPhase = Literal["running", "completed", "failed", "crashing"]
TaskLifecycleStatus = Literal["queued", "running", "completed", "failed"]
TaskAuditActionKind = Literal[
    "worker.task_started",
    "worker.task_completed",
    "worker.task_failed",
    "worker.task_crashing",
]

EXECUTION_CONTRACT_VERSION = "sc_execution.v1"
WORKER_TASK_FAILED_ERROR_CODE = "worker_task_failed"


@dataclass(frozen=True)
class TaskCreationSpec:
    """Canonical queued-task creation contract for persistence adapters."""

    task_kind: str
    design_id: int
    request_payload: dict[str, object] = field(default_factory=dict)
    requested_by: str = ""
    actor_id: int | None = None
    dedupe_key: str | None = None
    result_handle: TaskResultHandle = field(default_factory=lambda: TaskResultHandle())


@dataclass(frozen=True)
class TaskResultHandle:
    """Stable references to execution outputs created by one task."""

    trace_batch_id: int | None = None
    analysis_run_id: int | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> TaskResultHandle:
        return cls(
            trace_batch_id=_optional_int(payload.get("trace_batch_id")),
            analysis_run_id=_optional_int(payload.get("analysis_run_id")),
        )

    def is_empty(self) -> bool:
        return self.trace_batch_id is None and self.analysis_run_id is None

    def to_payload(self) -> dict[str, int]:
        payload: dict[str, int] = {}
        if self.trace_batch_id is not None:
            payload["trace_batch_id"] = self.trace_batch_id
        if self.analysis_run_id is not None:
            payload["analysis_run_id"] = self.analysis_run_id
        return payload


@dataclass(frozen=True)
class TaskExecutionResult:
    """Framework-agnostic execution result summary returned by worker operations."""

    result_summary_payload: dict[str, object] = field(default_factory=dict)
    trace_batch_id: int | None = None
    analysis_run_id: int | None = None

    def result_handle(self) -> TaskResultHandle:
        return TaskResultHandle(
            trace_batch_id=self.trace_batch_id,
            analysis_run_id=self.analysis_run_id,
        )


@dataclass(frozen=True)
class TaskLifecycleMutation:
    """Canonical persistence-layer mutation for one task lifecycle transition."""

    status: TaskLifecycleStatus | None = None
    started_at: datetime | None = None
    heartbeat_at: datetime | None = None
    completed_at: datetime | None = None
    progress_payload: dict[str, object] | None = None
    result_summary_payload: dict[str, object] | None = None
    error_payload: dict[str, object] | None = None
    result_handle: TaskResultHandle | None = None


@dataclass(frozen=True)
class WorkerExecutionProvenance:
    """Provenance fields attached to persisted execution payloads and logs."""

    lane: LaneName
    worker_task_name: WorkerTaskName
    worker_pid: int | None = None
    started_at: str | None = None
    completed_at: str | None = None
    crash_requested_at: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "lane": self.lane,
            "worker_task_name": self.worker_task_name,
        }
        if self.worker_pid is not None:
            payload["worker_pid"] = self.worker_pid
        if self.started_at is not None:
            payload["started_at"] = self.started_at
        if self.completed_at is not None:
            payload["completed_at"] = self.completed_at
        if self.crash_requested_at is not None:
            payload["crash_requested_at"] = self.crash_requested_at
        return payload


def build_worker_execution_provenance(
    *,
    lane: LaneName,
    worker_task_name: WorkerTaskName,
    worker_pid: int | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
    crash_requested_at: datetime | None = None,
) -> WorkerExecutionProvenance:
    """Build canonical worker provenance while normalizing timestamp encoding."""
    return WorkerExecutionProvenance(
        lane=lane,
        worker_task_name=worker_task_name,
        worker_pid=worker_pid,
        started_at=_optional_isoformat(started_at),
        completed_at=_optional_isoformat(completed_at),
        crash_requested_at=_optional_isoformat(crash_requested_at),
    )


def build_task_start_payload(
    *,
    provenance: WorkerExecutionProvenance,
    stale_after_seconds: int = 300,
) -> dict[str, object]:
    """Build the persisted progress payload for a task entering running state."""
    details = provenance.to_payload()
    return {
        "contract_version": EXECUTION_CONTRACT_VERSION,
        "phase": "running",
        "summary": f"{provenance.worker_task_name} started in the {provenance.lane} lane.",
        "recorded_at": provenance.started_at,
        "stage_label": provenance.worker_task_name,
        "stale_after_seconds": stale_after_seconds,
        "details": details,
        "lane": provenance.lane,
        "worker_task_name": provenance.worker_task_name,
    }


def build_task_creation_spec(
    *,
    task_kind: str,
    design_id: int,
    request_payload: Mapping[str, object] | None,
    requested_by: str,
    actor_id: int | None = None,
    dedupe_key: str | None = None,
    result_handle: TaskResultHandle | None = None,
) -> TaskCreationSpec:
    """Build the canonical queued-task creation contract for one persisted task."""
    return TaskCreationSpec(
        task_kind=task_kind.strip(),
        design_id=design_id,
        request_payload=_copy_payload(request_payload) or {},
        requested_by=requested_by.strip(),
        actor_id=actor_id,
        dedupe_key=normalize_task_dedupe_key(dedupe_key),
        result_handle=result_handle or TaskResultHandle(),
    )


def normalize_task_dedupe_key(dedupe_key: str | None) -> str | None:
    """Normalize optional dedupe keys so create/read paths share the same contract."""
    if dedupe_key is None:
        return None
    normalized = dedupe_key.strip()
    return normalized or None


def build_task_queued_payload(
    *,
    creation_spec: TaskCreationSpec,
) -> dict[str, object]:
    """Build the canonical persisted payload for one queued task."""
    payload: dict[str, object] = {
        "contract_version": EXECUTION_CONTRACT_VERSION,
        "phase": "queued",
        "summary": f"{creation_spec.task_kind} queued by {creation_spec.requested_by}.",
        "task_kind": creation_spec.task_kind,
        "requested_by": creation_spec.requested_by,
    }
    if creation_spec.actor_id is not None:
        payload["actor_id"] = creation_spec.actor_id
    if creation_spec.dedupe_key is not None:
        payload["dedupe_key"] = creation_spec.dedupe_key
    if not creation_spec.result_handle.is_empty():
        payload["result_refs"] = creation_spec.result_handle.to_payload()
    return payload


def build_task_queued_mutation(
    *,
    creation_spec: TaskCreationSpec,
) -> TaskLifecycleMutation:
    """Build the canonical queued-state mutation for one newly created task."""
    return TaskLifecycleMutation(
        status="queued",
        progress_payload=build_task_queued_payload(creation_spec=creation_spec),
        result_handle=creation_spec.result_handle,
    )


def build_task_running_mutation(
    *,
    recorded_at: datetime,
    progress_payload: Mapping[str, object] | None = None,
) -> TaskLifecycleMutation:
    """Build the canonical running-state mutation for one task."""
    return TaskLifecycleMutation(
        status="running",
        started_at=recorded_at,
        heartbeat_at=recorded_at,
        progress_payload=_copy_payload(progress_payload),
    )


def build_task_heartbeat_mutation(
    *,
    recorded_at: datetime,
    progress_payload: Mapping[str, object],
) -> TaskLifecycleMutation:
    """Build the canonical heartbeat mutation for one already-running task."""
    return TaskLifecycleMutation(
        heartbeat_at=recorded_at,
        progress_payload=_copy_payload(progress_payload),
    )


def build_task_completed_mutation(
    *,
    recorded_at: datetime,
    result_summary_payload: Mapping[str, object],
    result_handle: TaskResultHandle,
) -> TaskLifecycleMutation:
    """Build the canonical completion mutation for one finished task."""
    return TaskLifecycleMutation(
        status="completed",
        heartbeat_at=recorded_at,
        completed_at=recorded_at,
        result_summary_payload=_copy_payload(result_summary_payload),
        error_payload={},
        result_handle=result_handle,
    )


def build_task_failed_mutation(
    *,
    recorded_at: datetime,
    error_payload: Mapping[str, object],
) -> TaskLifecycleMutation:
    """Build the canonical failure mutation for one task."""
    return TaskLifecycleMutation(
        status="failed",
        heartbeat_at=recorded_at,
        completed_at=recorded_at,
        error_payload=_copy_payload(error_payload),
    )


def build_task_success_payload(
    *,
    provenance: WorkerExecutionProvenance,
    summary_payload: dict[str, object],
    result_handle: TaskResultHandle,
) -> dict[str, object]:
    """Build the persisted progress payload for a successfully completed task."""
    details: dict[str, object] = {
        **summary_payload,
        **provenance.to_payload(),
    }
    payload: dict[str, object] = {
        "contract_version": EXECUTION_CONTRACT_VERSION,
        "phase": "completed",
        "summary": f"{provenance.worker_task_name} completed in the {provenance.lane} lane.",
        "recorded_at": provenance.completed_at,
        "stage_label": provenance.worker_task_name,
        "details": details,
        "lane": provenance.lane,
        "worker_task_name": provenance.worker_task_name,
        **summary_payload,
    }
    if not result_handle.is_empty():
        payload["result_refs"] = result_handle.to_payload()
    return payload


def build_task_failure_payload(
    *,
    provenance: WorkerExecutionProvenance,
    exc_type: str,
    message: str,
) -> dict[str, object]:
    """Build the persisted error payload for a failed task."""
    return {
        "contract_version": EXECUTION_CONTRACT_VERSION,
        "phase": "failed",
        "error_code": WORKER_TASK_FAILED_ERROR_CODE,
        "summary": f"{provenance.worker_task_name} failed in the {provenance.lane} lane.",
        "details": {
            **provenance.to_payload(),
            "exception_type": exc_type,
            "message": message,
        },
    }


def build_task_crash_payload(
    *,
    provenance: WorkerExecutionProvenance,
) -> dict[str, object]:
    """Build the persisted heartbeat payload for an intentional worker crash."""
    return {
        "contract_version": EXECUTION_CONTRACT_VERSION,
        "phase": "crashing",
        **provenance.to_payload(),
    }


def build_worker_audit_payload(
    *,
    phase: ExecutionPhase,
    provenance: WorkerExecutionProvenance,
    result_handle: TaskResultHandle | None = None,
) -> dict[str, object]:
    """Build canonical audit payload metadata for one worker lifecycle event."""
    payload: dict[str, object] = {
        "contract_version": EXECUTION_CONTRACT_VERSION,
        "phase": phase,
        **provenance.to_payload(),
    }
    if result_handle is not None and not result_handle.is_empty():
        payload["result_refs"] = result_handle.to_payload()
    return payload


def audit_action_for_phase(phase: ExecutionPhase) -> TaskAuditActionKind:
    """Map one execution phase to the canonical worker audit action kind."""
    if phase == "running":
        return "worker.task_started"
    if phase == "completed":
        return "worker.task_completed"
    if phase == "failed":
        return "worker.task_failed"
    return "worker.task_crashing"


def build_worker_audit_summary(
    *,
    phase: ExecutionPhase,
    worker_task_name: WorkerTaskName,
    task_id: int,
) -> str:
    """Build the canonical worker audit summary line for one task phase."""
    if phase == "running":
        return f"Worker started {worker_task_name} for task {task_id}"
    if phase == "completed":
        return f"Worker completed {worker_task_name} for task {task_id}"
    if phase == "failed":
        return f"Worker failed {worker_task_name} for task {task_id}"
    return f"Worker is about to crash while running {worker_task_name} for task {task_id}"


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Expected integer-compatible value.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text:
            return int(text)
    raise ValueError("Expected integer-compatible value.")


def _optional_isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _copy_payload(payload: Mapping[str, object] | None) -> dict[str, object] | None:
    if payload is None:
        return None
    return dict(payload)
