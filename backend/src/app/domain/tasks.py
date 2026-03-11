from dataclasses import dataclass
from typing import Literal

from sc_core.tasking import TaskExecutionMode, WorkerTaskName
from src.app.domain.storage import MetadataRecordRef, ResultHandleRef, TracePayloadRef

TaskKind = Literal["simulation", "post_processing", "characterization"]
TaskLane = Literal["simulation", "characterization"]
TaskStatus = Literal["queued", "running", "completed", "failed"]
TaskQueueBackend = Literal["in_memory_scaffold"]
TaskVisibilityScope = Literal["workspace", "owned"]


@dataclass(frozen=True)
class TaskProgress:
    phase: TaskStatus
    percent_complete: int
    summary: str
    updated_at: str


@dataclass(frozen=True)
class TaskResultRefs:
    trace_batch_id: int | None
    analysis_run_id: int | None
    metadata_records: tuple[MetadataRecordRef, ...]
    trace_payload: TracePayloadRef | None
    result_handles: tuple[ResultHandleRef, ...]


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
class TaskDetail(TaskSummary):
    queue_backend: TaskQueueBackend
    worker_task_name: WorkerTaskName
    request_ready: bool
    submitted_from_active_dataset: bool
    progress: TaskProgress
    result_refs: TaskResultRefs


@dataclass(frozen=True)
class TaskListQuery:
    status: TaskStatus | None = None
    lane: TaskLane | None = None
    scope: TaskVisibilityScope = "workspace"
    dataset_id: str | None = None
    limit: int = 20


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
