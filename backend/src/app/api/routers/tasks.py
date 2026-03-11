from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.app.api.schemas.storage import (
    MetadataRecordRefResponse,
    ResultHandleRefResponse,
    TracePayloadRefResponse,
)
from src.app.api.schemas.tasks import (
    TaskDetailResponse,
    TaskMutationResponse,
    TaskProgressResponse,
    TaskResultRefsResponse,
    TaskSubmissionRequest,
    TaskSummaryResponse,
)
from src.app.domain.storage import MetadataRecordRef, ResultHandleRef, TracePayloadRef
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
                _build_metadata_record_ref_response(record)
                for record in task.result_refs.metadata_records
            ],
            trace_payload=_build_trace_payload_ref_response(task.result_refs.trace_payload),
            result_handles=[
                _build_result_handle_ref_response(handle)
                for handle in task.result_refs.result_handles
            ],
        ),
    )


def _build_metadata_record_ref_response(
    record: MetadataRecordRef,
) -> MetadataRecordRefResponse:
    return MetadataRecordRefResponse(
        backend=record.backend,
        record_type=record.record_type,
        record_id=record.record_id,
        version=record.version,
    )


def _build_trace_payload_ref_response(
    trace_payload: TracePayloadRef | None,
) -> TracePayloadRefResponse | None:
    if trace_payload is None:
        return None
    return TracePayloadRefResponse(
        backend=trace_payload.backend,
        store_key=trace_payload.store_key,
        store_uri=trace_payload.store_uri,
        group_path=trace_payload.group_path,
        array_path=trace_payload.array_path,
        schema_version=trace_payload.schema_version,
    )


def _build_result_handle_ref_response(
    handle: ResultHandleRef,
) -> ResultHandleRefResponse:
    return ResultHandleRefResponse(
        handle_id=handle.handle_id,
        kind=handle.kind,
        status=handle.status,
        label=handle.label,
        metadata_record=_build_metadata_record_ref_response(handle.metadata_record),
        payload_backend=handle.payload_backend,
        payload_format=handle.payload_format,
        payload_locator=handle.payload_locator,
        provenance_task_id=handle.provenance_task_id,
    )
