from __future__ import annotations

from typing import cast

from sc_core.tasking import TaskExecutionMode, WorkerTaskName
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskDispatch,
    TaskDispatchStatus,
    TaskKind,
    TaskLane,
    TaskProgress,
    TaskQueueBackend,
    TaskResultRefs,
    TaskStatus,
    TaskSubmissionSource,
    TaskVisibilityScope,
)
from src.app.infrastructure.persistence.models import (
    RewriteTaskDispatchRecord,
    RewriteTaskRecord,
)


class SqliteRewriteTaskSnapshotRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def has_tasks(self) -> bool:
        with self._session_factory() as session:
            return session.scalar(select(func.count(RewriteTaskRecord.id))) != 0

    def list_tasks(self) -> tuple[TaskDetail, ...]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(RewriteTaskRecord).order_by(RewriteTaskRecord.task_id.asc())
            ).all()
            details: list[TaskDetail] = []
            dispatch_rows_changed = False
            for row in rows:
                dispatch_row, changed = _upsert_dispatch_row(session, row)
                dispatch_rows_changed = dispatch_rows_changed or changed
                details.append(_to_task_detail(row, dispatch_row))
            if dispatch_rows_changed:
                session.commit()
            return tuple(details)

    def get_task(self, task_id: int) -> TaskDetail | None:
        with self._session_factory() as session:
            row = session.scalar(
                select(RewriteTaskRecord).where(RewriteTaskRecord.task_id == task_id)
            )
            if row is None:
                return None
            dispatch_row, changed = _upsert_dispatch_row(session, row)
            if changed:
                session.commit()
            return _to_task_detail(row, dispatch_row)

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail:
        with self._session_factory() as session:
            next_task_id = session.scalar(select(func.max(RewriteTaskRecord.task_id))) or 305
            row = RewriteTaskRecord(
                task_id=next_task_id + 1,
                kind=draft.kind,
                lane=draft.lane,
                execution_mode=draft.execution_mode,
                status="queued",
                submitted_at="2026-03-12 10:30:00",
                owner_user_id=draft.owner_user_id,
                owner_display_name=draft.owner_display_name,
                workspace_id=draft.workspace_id,
                workspace_slug=draft.workspace_slug,
                visibility_scope=draft.visibility_scope,
                dataset_id=draft.dataset_id,
                definition_id=draft.definition_id,
                summary=draft.summary,
                queue_backend="in_memory_scaffold",
                worker_task_name=draft.worker_task_name,
                request_ready=draft.request_ready,
                submitted_from_active_dataset=draft.submitted_from_active_dataset,
                progress_phase="queued",
                progress_percent_complete=0,
                progress_summary="Task accepted by rewrite in-memory scaffold.",
                progress_updated_at="2026-03-12 10:30:00",
            )
            session.add(row)
            session.flush()
            dispatch_row, _ = _upsert_dispatch_row(session, row)
            session.commit()
            session.refresh(row)
            session.refresh(dispatch_row)
            return _to_task_detail(row, dispatch_row)

    def save_task_snapshot(self, task: TaskDetail) -> TaskDetail:
        with self._session_factory() as session:
            row = session.scalar(
                select(RewriteTaskRecord).where(RewriteTaskRecord.task_id == task.task_id)
            )
            if row is None:
                row = RewriteTaskRecord(task_id=task.task_id)
                session.add(row)

            row.kind = task.kind
            row.lane = task.lane
            row.execution_mode = task.execution_mode
            row.status = task.status
            row.submitted_at = task.submitted_at
            row.owner_user_id = task.owner_user_id
            row.owner_display_name = task.owner_display_name
            row.workspace_id = task.workspace_id
            row.workspace_slug = task.workspace_slug
            row.visibility_scope = task.visibility_scope
            row.dataset_id = task.dataset_id
            row.definition_id = task.definition_id
            row.summary = task.summary
            row.queue_backend = task.queue_backend
            row.worker_task_name = task.worker_task_name
            row.request_ready = task.request_ready
            row.submitted_from_active_dataset = task.submitted_from_active_dataset
            row.progress_phase = task.progress.phase
            row.progress_percent_complete = task.progress.percent_complete
            row.progress_summary = task.progress.summary
            row.progress_updated_at = task.progress.updated_at

            session.flush()
            dispatch_row, _ = _upsert_dispatch_row(session, row, _derive_dispatch_from_task(task))
            session.commit()
            session.refresh(row)
            session.refresh(dispatch_row)
            return _to_task_detail(row, dispatch_row)


def _upsert_dispatch_row(
    session: Session,
    task_row: RewriteTaskRecord,
    dispatch: TaskDispatch | None = None,
) -> tuple[RewriteTaskDispatchRecord, bool]:
    desired_dispatch = dispatch or _derive_dispatch_from_row(task_row)
    row = session.scalar(
        select(RewriteTaskDispatchRecord).where(
            RewriteTaskDispatchRecord.task_id == task_row.task_id
        )
    )
    changed = False
    if row is None:
        row = RewriteTaskDispatchRecord(task_id=task_row.task_id)
        session.add(row)
        changed = True

    if row.dispatch_key != desired_dispatch.dispatch_key:
        row.dispatch_key = desired_dispatch.dispatch_key
        changed = True
    if row.status != desired_dispatch.status:
        row.status = desired_dispatch.status
        changed = True
    if row.submission_source != desired_dispatch.submission_source:
        row.submission_source = desired_dispatch.submission_source
        changed = True
    if row.accepted_at != desired_dispatch.accepted_at:
        row.accepted_at = desired_dispatch.accepted_at
        changed = True
    if row.last_updated_at != desired_dispatch.last_updated_at:
        row.last_updated_at = desired_dispatch.last_updated_at
        changed = True

    session.flush()
    return row, changed


def _derive_dispatch_from_row(task_row: RewriteTaskRecord) -> TaskDispatch:
    return TaskDispatch(
        dispatch_key=f"dispatch:{task_row.task_id}:{task_row.worker_task_name}",
        status=_dispatch_status(cast(TaskStatus, task_row.status)),
        submission_source=_submission_source(
            submitted_from_active_dataset=task_row.submitted_from_active_dataset,
            dataset_id=task_row.dataset_id,
        ),
        accepted_at=task_row.submitted_at,
        last_updated_at=task_row.progress_updated_at,
    )


def _derive_dispatch_from_task(task: TaskDetail) -> TaskDispatch:
    existing_dispatch = task.dispatch
    return TaskDispatch(
        dispatch_key=(
            existing_dispatch.dispatch_key
            if existing_dispatch is not None
            else f"dispatch:{task.task_id}:{task.worker_task_name}"
        ),
        status=_dispatch_status(task.status),
        submission_source=(
            existing_dispatch.submission_source
            if existing_dispatch is not None
            else _submission_source(
                submitted_from_active_dataset=task.submitted_from_active_dataset,
                dataset_id=task.dataset_id,
            )
        ),
        accepted_at=(
            existing_dispatch.accepted_at if existing_dispatch is not None else task.submitted_at
        ),
        last_updated_at=task.progress.updated_at,
    )


def _dispatch_status(task_status: TaskStatus) -> TaskDispatchStatus:
    if task_status == "queued":
        return "accepted"
    return cast(TaskDispatchStatus, task_status)


def _submission_source(
    *,
    submitted_from_active_dataset: bool,
    dataset_id: str | None,
) -> TaskSubmissionSource:
    if submitted_from_active_dataset:
        return "active_dataset"
    if dataset_id is not None:
        return "explicit_dataset"
    return "definition_only"


def _to_task_detail(
    row: RewriteTaskRecord,
    dispatch_row: RewriteTaskDispatchRecord,
) -> TaskDetail:
    return TaskDetail(
        task_id=row.task_id,
        kind=cast(TaskKind, row.kind),
        lane=cast(TaskLane, row.lane),
        execution_mode=cast(TaskExecutionMode, row.execution_mode),
        status=cast(TaskStatus, row.status),
        submitted_at=row.submitted_at,
        owner_user_id=row.owner_user_id,
        owner_display_name=row.owner_display_name,
        workspace_id=row.workspace_id,
        workspace_slug=row.workspace_slug,
        visibility_scope=cast(TaskVisibilityScope, row.visibility_scope),
        dataset_id=row.dataset_id,
        definition_id=row.definition_id,
        summary=row.summary,
        queue_backend=cast(TaskQueueBackend, row.queue_backend),
        worker_task_name=cast(WorkerTaskName, row.worker_task_name),
        request_ready=row.request_ready,
        submitted_from_active_dataset=row.submitted_from_active_dataset,
        progress=TaskProgress(
            phase=cast(TaskStatus, row.progress_phase),
            percent_complete=row.progress_percent_complete,
            summary=row.progress_summary,
            updated_at=row.progress_updated_at,
        ),
        result_refs=_empty_result_refs(),
        dispatch=TaskDispatch(
            dispatch_key=dispatch_row.dispatch_key,
            status=cast(TaskDispatchStatus, dispatch_row.status),
            submission_source=cast(TaskSubmissionSource, dispatch_row.submission_source),
            accepted_at=dispatch_row.accepted_at,
            last_updated_at=dispatch_row.last_updated_at,
        ),
    )


def _empty_result_refs() -> TaskResultRefs:
    from sc_core.execution import TaskResultHandle

    return TaskResultRefs(
        result_handle=TaskResultHandle(),
        metadata_records=(),
        trace_payload=None,
        result_handles=(),
    )
