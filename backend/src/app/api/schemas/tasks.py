from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskProgressResponse(BaseModel):
    phase: Literal["queued", "running", "completed", "failed"]
    percent_complete: int = Field(ge=0, le=100)
    summary: str
    updated_at: str


class TaskResultRefsResponse(BaseModel):
    trace_batch_id: int | None
    analysis_run_id: int | None


class TaskSummaryResponse(BaseModel):
    task_id: int
    kind: Literal["simulation", "post_processing", "characterization"]
    lane: Literal["simulation", "characterization"]
    status: Literal["queued", "running", "completed", "failed"]
    submitted_at: str
    submitted_by: str
    dataset_id: str | None
    definition_id: int | None
    summary: str


class TaskDetailResponse(TaskSummaryResponse):
    queue_backend: Literal["in_memory_scaffold"]
    worker_task_name: str | None
    submitted_from_active_dataset: bool
    progress: TaskProgressResponse
    result_refs: TaskResultRefsResponse


class TaskSubmissionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    kind: Literal["simulation", "post_processing", "characterization"]
    dataset_id: str | None = Field(default=None, min_length=1)
    definition_id: int | None = Field(default=None, ge=1)
    summary: str | None = Field(default=None, min_length=1)


class TaskMutationResponse(BaseModel):
    operation: Literal["submitted"]
    task: TaskDetailResponse
