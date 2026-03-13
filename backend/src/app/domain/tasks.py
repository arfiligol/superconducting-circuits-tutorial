from dataclasses import dataclass
from typing import Literal

from sc_core.execution import (
    TaskExecutionHistoryContext,
    TaskExecutionHistoryEvent,
    TaskExecutionHistoryEventType,
    TaskExecutionHistoryLevel,
    TaskExecutionHistoryMetadataValue,
    TaskResultHandle,
    build_task_execution_history,
    build_task_lifecycle_history_event,
    build_task_submission_history_event,
)
from sc_core.storage import TraceResultLinkage
from sc_core.tasking import TaskExecutionMode, WorkerTaskName

from src.app.domain.storage import MetadataRecordRef, ResultHandleRef, TracePayloadRef

TaskKind = Literal["simulation", "post_processing", "characterization"]
TaskLane = Literal["simulation", "characterization"]
TaskStatus = Literal["queued", "running", "completed", "failed"]
TaskQueueBackend = Literal["in_memory_scaffold"]
TaskVisibilityScope = Literal["workspace", "owned"]
TaskDispatchStatus = Literal["accepted", "running", "completed", "failed"]
TaskSubmissionSource = Literal["active_dataset", "explicit_dataset", "definition_only"]
TaskEventType = TaskExecutionHistoryEventType
TaskEventLevel = TaskExecutionHistoryLevel
TaskEventMetadataValue = TaskExecutionHistoryMetadataValue
TaskEventOrder = Literal["asc", "desc"]


@dataclass(frozen=True)
class TaskProgress:
    phase: TaskStatus
    percent_complete: int
    summary: str
    updated_at: str


@dataclass(frozen=True)
class TaskResultRefs:
    result_handle: TaskResultHandle
    metadata_records: tuple[MetadataRecordRef, ...]
    trace_payload: TracePayloadRef | None
    result_handles: tuple[ResultHandleRef, ...]

    @property
    def trace_batch_id(self) -> int | None:
        return self.result_handle.trace_batch_id

    @property
    def analysis_run_id(self) -> int | None:
        return self.result_handle.analysis_run_id

    def storage_linkage(self) -> TraceResultLinkage:
        return TraceResultLinkage.from_result_handle(self.result_handle)


@dataclass(frozen=True)
class TaskSummary:
    task_id: int
    kind: TaskKind
    lane: TaskLane
    execution_mode: TaskExecutionMode
    status: TaskStatus
    submitted_at: str
    owner_user_id: str
    owner_display_name: str
    workspace_id: str
    workspace_slug: str
    visibility_scope: TaskVisibilityScope
    dataset_id: str | None
    definition_id: int | None
    summary: str


@dataclass(frozen=True)
class TaskDispatch:
    dispatch_key: str
    status: TaskDispatchStatus
    submission_source: TaskSubmissionSource
    accepted_at: str
    last_updated_at: str


TaskEvent = TaskExecutionHistoryEvent


@dataclass(frozen=True)
class TaskDetail(TaskSummary):
    queue_backend: TaskQueueBackend
    worker_task_name: WorkerTaskName
    request_ready: bool
    submitted_from_active_dataset: bool
    progress: TaskProgress
    result_refs: TaskResultRefs
    dispatch: TaskDispatch | None = None
    events: tuple[TaskEvent, ...] = ()


@dataclass(frozen=True)
class TaskListQuery:
    status: TaskStatus | None = None
    lane: TaskLane | None = None
    scope: TaskVisibilityScope = "workspace"
    dataset_id: str | None = None
    limit: int = 20


@dataclass(frozen=True)
class TaskEventHistoryQuery:
    order: TaskEventOrder = "desc"
    limit: int = 20
    event_type: TaskEventType | None = None


@dataclass(frozen=True)
class TaskHistoryView:
    task: TaskDetail
    event_count: int
    latest_event: TaskEvent | None


@dataclass(frozen=True)
class TaskSubmissionDraft:
    kind: TaskKind
    dataset_id: str | None
    definition_id: int | None
    summary: str | None


@dataclass(frozen=True)
class TaskCreateDraft:
    kind: TaskKind
    lane: TaskLane
    execution_mode: TaskExecutionMode
    owner_user_id: str
    owner_display_name: str
    workspace_id: str
    workspace_slug: str
    visibility_scope: TaskVisibilityScope
    dataset_id: str | None
    definition_id: int | None
    summary: str
    worker_task_name: WorkerTaskName
    request_ready: bool
    submitted_from_active_dataset: bool
    submission_source: TaskSubmissionSource


@dataclass(frozen=True)
class TaskLifecycleUpdate:
    task_id: int
    status: TaskStatus
    progress_percent_complete: int
    progress_summary: str
    progress_updated_at: str
    summary: str | None = None
    result_refs: TaskResultRefs | None = None
    dispatch: TaskDispatch | None = None


def task_submission_source_for(
    *,
    submitted_from_active_dataset: bool,
    dataset_id: str | None,
) -> TaskSubmissionSource:
    if submitted_from_active_dataset:
        return "active_dataset"
    if dataset_id is not None:
        return "explicit_dataset"
    return "definition_only"


def task_dispatch_status_for(task_status: TaskStatus) -> TaskDispatchStatus:
    if task_status == "queued":
        return "accepted"
    return task_status


def build_task_dispatch(
    *,
    task_id: int,
    worker_task_name: str,
    task_status: TaskStatus,
    submitted_from_active_dataset: bool,
    dataset_id: str | None,
    accepted_at: str,
    last_updated_at: str,
    submission_source: TaskSubmissionSource | None = None,
    current_dispatch: TaskDispatch | None = None,
) -> TaskDispatch:
    return TaskDispatch(
        dispatch_key=(
            current_dispatch.dispatch_key
            if current_dispatch is not None
            else f"dispatch:{task_id}:{worker_task_name}"
        ),
        status=task_dispatch_status_for(task_status),
        submission_source=(
            current_dispatch.submission_source
            if current_dispatch is not None
            else submission_source
            or task_submission_source_for(
                submitted_from_active_dataset=submitted_from_active_dataset,
                dataset_id=dataset_id,
            )
        ),
        accepted_at=current_dispatch.accepted_at if current_dispatch is not None else accepted_at,
        last_updated_at=last_updated_at,
    )


def build_task_submission_event(task: TaskDetail) -> TaskEvent:
    context = _build_task_history_context(task)
    return build_task_submission_history_event(
        submitted_at=context.submitted_at,
        dispatch_status=context.dispatch_status,
        dispatch_key=context.dispatch_key,
        submission_source=context.submission_source,
        worker_task_name=context.worker_task_name,
        dataset_id=context.dataset_id,
        definition_id=context.definition_id,
    )


def _build_task_history_context(task: TaskDetail) -> TaskExecutionHistoryContext:
    dispatch = build_task_dispatch(
        task_id=task.task_id,
        worker_task_name=task.worker_task_name,
        task_status=task.status,
        submitted_from_active_dataset=task.submitted_from_active_dataset,
        dataset_id=task.dataset_id,
        accepted_at=task.submitted_at,
        last_updated_at=task.progress.updated_at,
        current_dispatch=task.dispatch,
    )
    return TaskExecutionHistoryContext(
        task_status=task.status,
        submitted_at=task.submitted_at,
        progress_updated_at=task.progress.updated_at,
        progress_percent_complete=task.progress.percent_complete,
        dispatch_key=dispatch.dispatch_key,
        dispatch_status=dispatch.status,
        submission_source=dispatch.submission_source,
        worker_task_name=task.worker_task_name,
        dataset_id=task.dataset_id,
        definition_id=task.definition_id,
        result_handle_ids=tuple(
            str(handle.handle_id) for handle in task.result_refs.result_handles
        ),
    )


def build_task_lifecycle_event(task: TaskDetail) -> TaskEvent | None:
    context = _build_task_history_context(task)
    return build_task_lifecycle_history_event(
        task_status=context.task_status,
        progress_updated_at=context.progress_updated_at,
        progress_percent_complete=context.progress_percent_complete,
        dispatch_status=context.dispatch_status,
        dispatch_key=context.dispatch_key,
        worker_task_name=context.worker_task_name,
        result_handle_ids=context.result_handle_ids,
    )


def build_task_event_history(task: TaskDetail) -> tuple[TaskEvent, ...]:
    return build_task_execution_history(_build_task_history_context(task))
