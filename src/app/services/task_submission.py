"""Persisted task submission helpers for API-authenticated callers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from app.services.execution_context import ActorContext, UseCaseContext
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import DesignRecord, TaskRecord
from worker.dispatch import DispatchedWorkerTask, TaskSubmissionKind, enqueue_task


@dataclass(frozen=True)
class SubmittedTask:
    """API-facing result of one task submission attempt."""

    task: TaskRecord
    dispatch: DispatchedWorkerTask
    dedupe_hit: bool


def _detach_task(task: TaskRecord) -> TaskRecord:
    """Return a detached copy of one persisted task record."""
    return TaskRecord(
        id=task.id,
        task_kind=task.task_kind,
        status=task.status,
        design_id=task.design_id,
        trace_batch_id=task.trace_batch_id,
        analysis_run_id=task.analysis_run_id,
        requested_by=task.requested_by,
        actor_id=task.actor_id,
        dedupe_key=task.dedupe_key,
        request_payload=dict(task.request_payload),
        progress_payload=dict(task.progress_payload),
        result_summary_payload=dict(task.result_summary_payload),
        error_payload=dict(task.error_payload),
        created_at=task.created_at,
        started_at=task.started_at,
        heartbeat_at=task.heartbeat_at,
        completed_at=task.completed_at,
    )


def _stable_json_payload(payload: dict[str, Any]) -> str:
    """Return one stable JSON string for dedupe-key derivation."""
    return json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=True)


def _build_dedupe_key(
    *,
    task_kind: TaskSubmissionKind,
    design_id: int,
    normalized_payload: dict[str, Any],
) -> str:
    """Build one stable soft-dedupe key for a task submission request."""
    canonical = _stable_json_payload(
        {
            "task_kind": task_kind,
            "design_id": int(design_id),
            "request": normalized_payload,
        }
    )
    return f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"


def create_api_task(
    *,
    task_kind: TaskSubmissionKind,
    design_id: int,
    request_payload: dict[str, Any],
    actor: ActorContext,
    force_rerun: bool,
) -> SubmittedTask:
    """Create one persisted task record and enqueue it on the frozen worker lane."""
    context = UseCaseContext(
        actor=actor,
        source="api",
        force_rerun=bool(force_rerun),
        metadata={"task_kind": task_kind, "design_id": int(design_id)},
    )
    normalized_request_payload = dict(request_payload)
    dedupe_key = _build_dedupe_key(
        task_kind=task_kind,
        design_id=design_id,
        normalized_payload=normalized_request_payload,
    )

    with get_unit_of_work() as uow:
        design = uow.datasets.get(design_id)
        if design is None:
            raise ValueError(f"Design ID {design_id} not found.")

        if not force_rerun:
            existing = uow.tasks.find_active_by_dedupe_key(dedupe_key)
            if existing is not None:
                dispatch = _dispatch_metadata_for_task_kind(task_kind)
                uow.audit_logs.append_log(
                    actor_id=actor.actor_id,
                    action_kind="task.dedupe_reused",
                    resource_kind="task",
                    resource_id=existing.id or 0,
                    summary=(
                        f"Reused active {task_kind} task {existing.id} for design {design_id}."
                    ),
                    payload={"dedupe_key": dedupe_key, "task_kind": task_kind},
                )
                uow.commit()
                return SubmittedTask(
                    task=_detach_task(existing),
                    dispatch=dispatch,
                    dedupe_hit=True,
                )

        persisted_request_payload = {
            "task_kind": task_kind,
            "design_id": int(design_id),
            "parameters": normalized_request_payload,
            "context": context.to_payload(),
        }
        task = uow.tasks.create_task(
            task_kind=task_kind,
            design_id=design_id,
            request_payload=persisted_request_payload,
            requested_by=context.requested_by,
            actor_id=actor.actor_id,
            dedupe_key=None if force_rerun else dedupe_key,
        )
        uow.audit_logs.append_log(
            actor_id=actor.actor_id,
            action_kind="task.requested",
            resource_kind="task",
            resource_id=task.id or 0,
            summary=f"Requested {task_kind} task for design {design_id}.",
            payload={
                "task_kind": task_kind,
                "design_id": int(design_id),
                "force_rerun": bool(force_rerun),
                "dedupe_key": None if force_rerun else dedupe_key,
            },
        )
        uow.commit()
        detached_task = _detach_task(task)

    if detached_task.id is None:
        raise ValueError("Task submission did not produce a persisted task ID.")
    dispatch = enqueue_task(task_kind, task_id=int(detached_task.id))
    return SubmittedTask(task=detached_task, dispatch=dispatch, dedupe_hit=False)


def _dispatch_metadata_for_task_kind(task_kind: TaskSubmissionKind) -> DispatchedWorkerTask:
    """Return static dispatch metadata without enqueueing a new task."""
    if task_kind == "simulation":
        return DispatchedWorkerTask("simulation", "simulation_smoke_task")
    if task_kind == "post_processing":
        return DispatchedWorkerTask("simulation", "post_processing_smoke_task")
    if task_kind == "characterization":
        return DispatchedWorkerTask("characterization", "characterization_smoke_task")
    raise ValueError(f"Unsupported task kind '{task_kind}'.")


def require_design(design_id: int) -> DesignRecord:
    """Load one design or raise if it does not exist."""
    with get_unit_of_work() as uow:
        design = uow.datasets.get(design_id)
        if design is None:
            raise ValueError(f"Design ID {design_id} not found.")
        return design
