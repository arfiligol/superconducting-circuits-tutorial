from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.app.api.presenters.storage import (
    build_metadata_record_ref_response,
    build_result_handle_ref_response,
    build_trace_payload_ref_response,
)
from src.app.api.schemas.tasks import (
    TaskDetailResponse,
    TaskDispatchResponse,
    TaskEventResponse,
    TaskMutationResponse,
    TaskProgressResponse,
    TaskResultRefsResponse,
    TaskSubmissionRequest,
    TaskSummaryResponse,
)
from src.app.domain.tasks import (
    TaskDetail,
    TaskLane,
    TaskListQuery,
    TaskStatus,
    TaskSubmissionDraft,
    TaskVisibilityScope,
)
from src.app.infrastructure.runtime import get_task_service
from src.app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskSummaryResponse])
def list_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    lane: Annotated[TaskLane | None, Query()] = None,
    scope: Annotated[TaskVisibilityScope, Query()] = "workspace",
    dataset_id: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> list[TaskSummaryResponse]:
    return [
        _build_task_summary_response(task)
        for task in task_service.list_tasks(
            TaskListQuery(
                status=status_filter,
                lane=lane,
                scope=scope,
                dataset_id=dataset_id,
                limit=limit,
            )
        )
    ]


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskDetailResponse:
    return _build_task_detail_response(task_service.get_task(task_id))


@router.post("", response_model=TaskMutationResponse, status_code=status.HTTP_201_CREATED)
def submit_task(
    payload: TaskSubmissionRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskMutationResponse:
    detail = task_service.submit_task(
        TaskSubmissionDraft(
            kind=payload.kind,
            dataset_id=payload.dataset_id,
            definition_id=payload.definition_id,
            summary=payload.summary,
        )
    )
    return TaskMutationResponse(
        operation="submitted",
        task=_build_task_detail_response(detail),
    )


def _build_task_summary_response(task: TaskDetail) -> TaskSummaryResponse:
    return TaskSummaryResponse(
        task_id=task.task_id,
        kind=task.kind,
        lane=task.lane,
        execution_mode=task.execution_mode,
        status=task.status,
        submitted_at=task.submitted_at,
        owner_user_id=task.owner_user_id,
        owner_display_name=task.owner_display_name,
        workspace_id=task.workspace_id,
        workspace_slug=task.workspace_slug,
        visibility_scope=task.visibility_scope,
        dataset_id=task.dataset_id,
        definition_id=task.definition_id,
        summary=task.summary,
    )


def _build_task_detail_response(task: TaskDetail) -> TaskDetailResponse:
    return TaskDetailResponse(
        task_id=task.task_id,
        kind=task.kind,
        lane=task.lane,
        execution_mode=task.execution_mode,
        status=task.status,
        submitted_at=task.submitted_at,
        owner_user_id=task.owner_user_id,
        owner_display_name=task.owner_display_name,
        workspace_id=task.workspace_id,
        workspace_slug=task.workspace_slug,
        visibility_scope=task.visibility_scope,
        dataset_id=task.dataset_id,
        definition_id=task.definition_id,
        summary=task.summary,
        queue_backend=task.queue_backend,
        worker_task_name=task.worker_task_name,
        request_ready=task.request_ready,
        submitted_from_active_dataset=task.submitted_from_active_dataset,
        dispatch=_build_task_dispatch_response(task),
        progress=TaskProgressResponse(
            phase=task.progress.phase,
            percent_complete=task.progress.percent_complete,
            summary=task.progress.summary,
            updated_at=task.progress.updated_at,
        ),
        result_refs=TaskResultRefsResponse(
            trace_batch_id=task.result_refs.trace_batch_id,
            analysis_run_id=task.result_refs.analysis_run_id,
            metadata_records=[
                build_metadata_record_ref_response(record)
                for record in task.result_refs.metadata_records
            ],
            trace_payload=build_trace_payload_ref_response(task.result_refs.trace_payload),
            result_handles=[
                build_result_handle_ref_response(handle)
                for handle in task.result_refs.result_handles
            ],
        ),
        events=[
            TaskEventResponse(
                event_key=event.event_key,
                event_type=event.event_type,
                level=event.level,
                occurred_at=event.occurred_at,
                message=event.message,
                metadata=event.metadata,
            )
            for event in task.events
        ],
    )


def _build_task_dispatch_response(task: TaskDetail) -> TaskDispatchResponse:
    dispatch = task.dispatch
    if dispatch is None:
        dispatch_status = "accepted" if task.status == "queued" else task.status
        submission_source = (
            "active_dataset"
            if task.submitted_from_active_dataset
            else "explicit_dataset"
            if task.dataset_id is not None
            else "definition_only"
        )
        return TaskDispatchResponse(
            dispatch_key=f"dispatch:{task.task_id}:{task.worker_task_name}",
            status=dispatch_status,
            submission_source=submission_source,
            accepted_at=task.submitted_at,
            last_updated_at=task.progress.updated_at,
        )

    return TaskDispatchResponse(
        dispatch_key=dispatch.dispatch_key,
        status=dispatch.status,
        submission_source=dispatch.submission_source,
        accepted_at=dispatch.accepted_at,
        last_updated_at=dispatch.last_updated_at,
    )
