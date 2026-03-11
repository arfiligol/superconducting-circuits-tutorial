from dataclasses import dataclass
from typing import Literal

TaskKind = Literal["simulation", "post_processing", "characterization"]
TaskLane = Literal["simulation", "characterization"]
TaskStatus = Literal["queued", "running", "completed", "failed"]
TaskQueueBackend = Literal["in_memory_scaffold"]


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


@dataclass(frozen=True)
class TaskSummary:
    task_id: int
    kind: TaskKind
    lane: TaskLane
    status: TaskStatus
    submitted_at: str
    submitted_by: str
    dataset_id: str | None
    definition_id: int | None
    summary: str


@dataclass(frozen=True)
class TaskDetail(TaskSummary):
    queue_backend: TaskQueueBackend
    worker_task_name: str | None
    submitted_from_active_dataset: bool
    progress: TaskProgress
    result_refs: TaskResultRefs


@dataclass(frozen=True)
class TaskListQuery:
    status: TaskStatus | None = None
    lane: TaskLane | None = None
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
    submitted_by: str
    dataset_id: str | None
    definition_id: int | None
    summary: str
    worker_task_name: str
    submitted_from_active_dataset: bool
