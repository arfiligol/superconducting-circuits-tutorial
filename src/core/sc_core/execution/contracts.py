from dataclasses import dataclass, field
from typing import Literal

from sc_core.tasking import LaneName, WorkerTaskName

ExecutionPhase = Literal["running", "completed", "failed", "crashing"]
TaskAuditActionKind = Literal[
    "worker.task_started",
    "worker.task_completed",
    "worker.task_failed",
    "worker.task_crashing",
]

EXECUTION_CONTRACT_VERSION = "sc_execution.v1"
WORKER_TASK_FAILED_ERROR_CODE = "worker_task_failed"


@dataclass(frozen=True)
class TaskResultHandle:
    """Stable references to execution outputs created by one task."""

    trace_batch_id: int | None = None
    analysis_run_id: int | None = None

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
