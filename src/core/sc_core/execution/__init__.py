"""Framework-agnostic execution contracts shared by backend, worker, and CLI."""

from sc_core.execution.contracts import (
    EXECUTION_CONTRACT_VERSION,
    WORKER_TASK_FAILED_ERROR_CODE,
    ExecutionPhase,
    TaskAuditActionKind,
    TaskExecutionResult,
    TaskResultHandle,
    WorkerExecutionProvenance,
    audit_action_for_phase,
    build_task_crash_payload,
    build_task_failure_payload,
    build_task_start_payload,
    build_task_success_payload,
    build_worker_audit_summary,
)

__all__ = [
    "EXECUTION_CONTRACT_VERSION",
    "WORKER_TASK_FAILED_ERROR_CODE",
    "ExecutionPhase",
    "TaskAuditActionKind",
    "TaskExecutionResult",
    "TaskResultHandle",
    "WorkerExecutionProvenance",
    "audit_action_for_phase",
    "build_task_crash_payload",
    "build_task_failure_payload",
    "build_task_start_payload",
    "build_task_success_payload",
    "build_worker_audit_summary",
]
