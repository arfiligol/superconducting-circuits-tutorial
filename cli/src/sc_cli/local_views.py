"""CLI-local machine-readable view contracts."""

from __future__ import annotations

from pydantic import BaseModel

from sc_cli.local_runtime import (
    LocalResultHandle,
    LocalSession,
    LocalSessionDataset,
    LocalTaskDetail,
    LocalTaskEvent,
    LocalTaskResultRefs,
    LocalTracePayload,
)


class LocalSessionIdentityEnvelope(BaseModel):
    session_id: str
    auth: dict[str, object]
    identity: dict[str, object] | None = None


class LocalSessionActiveDatasetEnvelope(BaseModel):
    active_dataset: LocalSessionDataset | None = None


class LocalTaskInspectionView(BaseModel):
    event_count: int
    latest_event: LocalTaskEvent | None = None
    metadata_record_count: int
    result_handle_count: int
    trace_payload_present: bool
    trace_batch_id: int | None = None
    analysis_run_id: str | None = None


class LocalTaskInspectionEnvelope(BaseModel):
    task: LocalTaskDetail
    inspection: LocalTaskInspectionView


class LocalTaskResultContext(BaseModel):
    task_id: int
    kind: str
    lane: str
    execution_mode: str
    status: str
    worker_task_name: str
    dataset_id: str | None = None
    definition_id: int | None = None
    summary: str
    dispatch: dict[str, object]
    lineage: dict[str, object] | None = None
    event_count: int
    result_handle_count: int
    trace_batch_id: int | None = None
    analysis_run_id: str | None = None


class LocalTaskResultRefsEnvelope(BaseModel):
    task: LocalTaskResultContext
    result_refs: LocalTaskResultRefs


class LocalTaskTracePayloadEnvelope(BaseModel):
    task: LocalTaskResultContext
    trace_payload: LocalTracePayload


class LocalTaskHandlesEnvelope(BaseModel):
    task: LocalTaskResultContext
    metadata_records: list[dict[str, object]]
    result_handles: list[LocalResultHandle]


class LocalTaskEventHistoryEnvelope(BaseModel):
    task: LocalTaskResultContext
    event_count: int
    events: list[LocalTaskEvent]


class LocalTaskLatestEventEnvelope(BaseModel):
    task: LocalTaskResultContext
    event: LocalTaskEvent


class LocalTaskResultSummary(BaseModel):
    trace_batch_id: int | None = None
    analysis_run_id: str | None = None
    metadata_record_count: int
    result_handle_count: int
    trace_payload_present: bool
    result_handle_ids: list[str]
    lineage: dict[str, object] | None = None


class LocalTaskOperationsBundleEnvelope(BaseModel):
    task: LocalTaskDetail
    inspection: LocalTaskInspectionView
    recent_events: list[LocalTaskEvent]
    result_summary: LocalTaskResultSummary


def build_session_identity_envelope(session: LocalSession) -> LocalSessionIdentityEnvelope:
    return LocalSessionIdentityEnvelope(
        session_id=session.session_id,
        auth=session.auth.model_dump(mode="json"),
        identity=None if session.identity is None else session.identity.model_dump(mode="json"),
    )


def build_session_active_dataset_envelope(
    session: LocalSession,
) -> LocalSessionActiveDatasetEnvelope:
    return LocalSessionActiveDatasetEnvelope(active_dataset=session.workspace.active_dataset)


def build_task_inspection_view(task: LocalTaskDetail) -> LocalTaskInspectionView:
    latest_event = task.events[-1] if task.events else None
    return LocalTaskInspectionView(
        event_count=len(task.events),
        latest_event=latest_event,
        metadata_record_count=len(task.result_refs.metadata_records),
        result_handle_count=len(task.result_refs.result_handles),
        trace_payload_present=task.result_refs.trace_payload is not None,
        trace_batch_id=task.result_refs.trace_batch_id,
        analysis_run_id=task.result_refs.analysis_run_id,
    )


def build_task_result_context(task: LocalTaskDetail) -> LocalTaskResultContext:
    return LocalTaskResultContext(
        task_id=task.task_id,
        kind=task.kind,
        lane=task.lane,
        execution_mode=task.execution_mode,
        status=task.status,
        worker_task_name=task.worker_task_name,
        dataset_id=task.dataset_id,
        definition_id=task.definition_id,
        summary=task.summary,
        dispatch=task.dispatch.model_dump(mode="json"),
        lineage=(
            None
            if task.result_refs.lineage is None
            else task.result_refs.lineage.model_dump(mode="json")
        ),
        event_count=len(task.events),
        result_handle_count=len(task.result_refs.result_handles),
        trace_batch_id=task.result_refs.trace_batch_id,
        analysis_run_id=task.result_refs.analysis_run_id,
    )


def build_task_inspection_envelope(task: LocalTaskDetail) -> LocalTaskInspectionEnvelope:
    return LocalTaskInspectionEnvelope(task=task, inspection=build_task_inspection_view(task))


def build_task_result_refs_envelope(task: LocalTaskDetail) -> LocalTaskResultRefsEnvelope:
    return LocalTaskResultRefsEnvelope(
        task=build_task_result_context(task),
        result_refs=task.result_refs,
    )


def build_task_trace_payload_envelope(task: LocalTaskDetail) -> LocalTaskTracePayloadEnvelope:
    assert task.result_refs.trace_payload is not None
    return LocalTaskTracePayloadEnvelope(
        task=build_task_result_context(task),
        trace_payload=task.result_refs.trace_payload,
    )


def build_task_handles_envelope(task: LocalTaskDetail) -> LocalTaskHandlesEnvelope:
    return LocalTaskHandlesEnvelope(
        task=build_task_result_context(task),
        metadata_records=[
            record.model_dump(mode="json") for record in task.result_refs.metadata_records
        ],
        result_handles=task.result_refs.result_handles,
    )


def build_task_event_history_envelope(
    task: LocalTaskDetail,
    *,
    events: list[LocalTaskEvent],
) -> LocalTaskEventHistoryEnvelope:
    return LocalTaskEventHistoryEnvelope(
        task=build_task_result_context(task),
        event_count=len(events),
        events=events,
    )


def build_task_latest_event_envelope(
    task: LocalTaskDetail,
    *,
    event: LocalTaskEvent,
) -> LocalTaskLatestEventEnvelope:
    return LocalTaskLatestEventEnvelope(task=build_task_result_context(task), event=event)


def build_task_operations_bundle_envelope(
    task: LocalTaskDetail,
    *,
    recent_events: list[LocalTaskEvent],
) -> LocalTaskOperationsBundleEnvelope:
    return LocalTaskOperationsBundleEnvelope(
        task=task,
        inspection=build_task_inspection_view(task),
        recent_events=recent_events,
        result_summary=LocalTaskResultSummary(
            trace_batch_id=task.result_refs.trace_batch_id,
            analysis_run_id=task.result_refs.analysis_run_id,
            metadata_record_count=len(task.result_refs.metadata_records),
            result_handle_count=len(task.result_refs.result_handles),
            trace_payload_present=task.result_refs.trace_payload is not None,
            result_handle_ids=[handle.handle_id for handle in task.result_refs.result_handles],
            lineage=(
                None
                if task.result_refs.lineage is None
                else task.result_refs.lineage.model_dump(mode="json")
            ),
        ),
    )
