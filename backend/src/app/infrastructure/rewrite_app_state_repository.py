from dataclasses import replace

from sc_core.execution import TaskResultHandle

from src.app.domain.session import SessionState, SessionUser
from src.app.domain.storage import ResultHandleKind
from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskProgress,
    TaskResultRefs,
)
from src.app.infrastructure.storage_reference_factory import (
    build_metadata_record_ref,
    build_result_handle_ref,
    build_result_provenance_ref,
    build_trace_payload_ref,
)


class InMemoryRewriteAppStateRepository:
    def __init__(self) -> None:
        self._session_state = _seed_session_state()
        self._tasks = {task.task_id: task for task in _seed_tasks()}
        self._next_task_id = max(self._tasks) + 1

    def get_session_state(self) -> SessionState:
        return self._session_state

    def set_active_dataset_id(self, dataset_id: str | None) -> SessionState:
        self._session_state = replace(self._session_state, active_dataset_id=dataset_id)
        return self._session_state

    def list_tasks(self) -> list[TaskDetail]:
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> TaskDetail | None:
        return self._tasks.get(task_id)

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail:
        task_id = self._next_task_id
        task = TaskDetail(
            task_id=task_id,
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
            progress=TaskProgress(
                phase="queued",
                percent_complete=0,
                summary="Task accepted by rewrite in-memory scaffold.",
                updated_at="2026-03-12 10:30:00",
            ),
            result_refs=_build_pending_result_refs(task_id=task_id, draft=draft),
        )
        self._tasks[task.task_id] = task
        self._next_task_id += 1
        return task


def _seed_session_state() -> SessionState:
    return SessionState(
        session_id="rewrite-local-session",
        auth_state="authenticated",
        auth_mode="development_stub",
        scopes=("datasets:read", "datasets:write", "tasks:read", "tasks:submit"),
        user=SessionUser(
            user_id="researcher-01",
            display_name="Rewrite Local User",
            email="rewrite.local@example.com",
        ),
        workspace_id="ws-device-lab",
        workspace_slug="device-lab",
        workspace_display_name="Device Lab Workspace",
        workspace_role="owner",
        default_task_scope="workspace",
        active_dataset_id="fluxonium-2025-031",
    )


def _seed_tasks() -> tuple[TaskDetail, ...]:
    return (
        TaskDetail(
            task_id=301,
            kind="simulation",
            lane="simulation",
            execution_mode="run",
            status="running",
            submitted_at="2026-03-12 09:15:00",
            owner_user_id="researcher-01",
            owner_display_name="Rewrite Local User",
            workspace_id="ws-device-lab",
            workspace_slug="device-lab",
            visibility_scope="workspace",
            dataset_id="fluxonium-2025-031",
            definition_id=18,
            summary="Fluxonium parameter sweep is running.",
            queue_backend="in_memory_scaffold",
            worker_task_name="simulation_run_task",
            request_ready=True,
            submitted_from_active_dataset=True,
            progress=TaskProgress(
                phase="running",
                percent_complete=55,
                summary="simulation_run_task started in the simulation lane.",
                updated_at="2026-03-12 09:22:00",
            ),
            result_refs=_empty_result_refs(),
        ),
        TaskDetail(
            task_id=302,
            kind="characterization",
            lane="characterization",
            execution_mode="run",
            status="queued",
            submitted_at="2026-03-12 08:40:00",
            owner_user_id="researcher-01",
            owner_display_name="Rewrite Local User",
            workspace_id="ws-device-lab",
            workspace_slug="device-lab",
            visibility_scope="workspace",
            dataset_id="transmon-coupler-014",
            definition_id=None,
            summary="Coupler dataset characterization is queued.",
            queue_backend="in_memory_scaffold",
            worker_task_name="characterization_run_task",
            request_ready=True,
            submitted_from_active_dataset=False,
            progress=TaskProgress(
                phase="queued",
                percent_complete=0,
                summary="Task accepted by rewrite in-memory scaffold.",
                updated_at="2026-03-12 08:40:00",
            ),
            result_refs=_empty_result_refs(),
        ),
        TaskDetail(
            task_id=303,
            kind="post_processing",
            lane="simulation",
            execution_mode="run",
            status="completed",
            submitted_at="2026-03-11 19:05:00",
            owner_user_id="researcher-01",
            owner_display_name="Rewrite Local User",
            workspace_id="ws-device-lab",
            workspace_slug="device-lab",
            visibility_scope="owned",
            dataset_id="fluxonium-2025-031",
            definition_id=None,
            summary="Fluxonium fit bundle was post-processed.",
            queue_backend="in_memory_scaffold",
            worker_task_name="post_processing_run_task",
            request_ready=True,
            submitted_from_active_dataset=True,
            progress=TaskProgress(
                phase="completed",
                percent_complete=100,
                summary="post_processing_run_task completed in the simulation lane.",
                updated_at="2026-03-11 19:18:00",
            ),
            result_refs=_fluxonium_completed_result_refs(),
        ),
        TaskDetail(
            task_id=304,
            kind="simulation",
            lane="simulation",
            execution_mode="smoke",
            status="queued",
            submitted_at="2026-03-11 17:40:00",
            owner_user_id="researcher-02",
            owner_display_name="Modeling User",
            workspace_id="ws-device-lab",
            workspace_slug="device-lab",
            visibility_scope="owned",
            dataset_id="fluxonium-2025-031",
            definition_id=12,
            summary="Private simulation draft remains owner-only.",
            queue_backend="in_memory_scaffold",
            worker_task_name="simulation_smoke_task",
            request_ready=False,
            submitted_from_active_dataset=False,
            progress=TaskProgress(
                phase="queued",
                percent_complete=0,
                summary="Task accepted by rewrite in-memory scaffold.",
                updated_at="2026-03-11 17:40:00",
            ),
            result_refs=_empty_result_refs(),
        ),
        TaskDetail(
            task_id=305,
            kind="characterization",
            lane="characterization",
            execution_mode="run",
            status="running",
            submitted_at="2026-03-11 16:55:00",
            owner_user_id="researcher-03",
            owner_display_name="Shared Workspace User",
            workspace_id="ws-modeling",
            workspace_slug="modeling",
            visibility_scope="workspace",
            dataset_id="transmon-coupler-014",
            definition_id=None,
            summary="Modeling workspace characterization is running.",
            queue_backend="in_memory_scaffold",
            worker_task_name="characterization_run_task",
            request_ready=True,
            submitted_from_active_dataset=False,
            progress=TaskProgress(
                phase="running",
                percent_complete=35,
                summary="characterization_run_task started in the characterization lane.",
                updated_at="2026-03-11 17:00:00",
            ),
            result_refs=_characterization_result_refs(),
        ),
    )


def _empty_result_refs() -> TaskResultRefs:
    return TaskResultRefs(
        result_handle=TaskResultHandle(),
        metadata_records=(),
        trace_payload=None,
        result_handles=(),
    )


def _fluxonium_completed_result_refs() -> TaskResultRefs:
    trace_batch_record = build_metadata_record_ref("trace_batch", "trace_batch:88", version=1)
    return TaskResultRefs(
        result_handle=TaskResultHandle(trace_batch_id=88),
        metadata_records=(
            trace_batch_record,
            build_metadata_record_ref("result_handle", "result_handle:501", version=2),
        ),
        trace_payload=build_trace_payload_ref(
            payload_role="task_output",
            store_key="datasets/fluxonium-2025-031/trace-batches/88.zarr",
            store_uri="trace_store/datasets/fluxonium-2025-031/trace-batches/88.zarr",
            group_path="trace_batches/88",
            array_path="signals/iq_real",
            dtype="float64",
            shape=(184, 1024),
            chunk_shape=(16, 1024),
        ),
        result_handles=(
            build_result_handle_ref(
                handle_id="result:fluxonium-2025-031:fit-summary",
                kind="fit_summary",
                status="materialized",
                label="Fluxonium fit summary",
                metadata_record=build_metadata_record_ref(
                    "result_handle",
                    "result_handle:501",
                    version=2,
                ),
                payload_backend="json_artifact",
                payload_format="json",
                payload_role="report_artifact",
                payload_locator="artifacts/fit-summary.json",
                provenance_task_id=303,
                provenance=build_result_provenance_ref(
                    source_dataset_id="fluxonium-2025-031",
                    source_task_id=303,
                    trace_batch_record=trace_batch_record,
                ),
            ),
            build_result_handle_ref(
                handle_id="result:fluxonium-2025-031:plot-bundle",
                kind="plot_bundle",
                status="materialized",
                label="Fluxonium plot bundle",
                metadata_record=build_metadata_record_ref(
                    "result_handle",
                    "result_handle:502",
                    version=1,
                ),
                payload_backend="bundle_archive",
                payload_format="zip",
                payload_role="bundle_artifact",
                payload_locator="artifacts/plot-bundle.zip",
                provenance_task_id=303,
                provenance=build_result_provenance_ref(
                    source_dataset_id="fluxonium-2025-031",
                    source_task_id=303,
                    trace_batch_record=trace_batch_record,
                ),
            ),
        ),
    )


def _characterization_result_refs() -> TaskResultRefs:
    analysis_run_record = build_metadata_record_ref("analysis_run", "analysis_run:12", version=4)
    return TaskResultRefs(
        result_handle=TaskResultHandle(analysis_run_id=12),
        metadata_records=(
            analysis_run_record,
            build_metadata_record_ref("result_handle", "result_handle:612", version=3),
        ),
        trace_payload=build_trace_payload_ref(
            payload_role="analysis_projection",
            store_key="datasets/transmon-coupler-014/analysis-runs/12.zarr",
            store_uri="trace_store/datasets/transmon-coupler-014/analysis-runs/12.zarr",
            group_path="analysis_runs/12",
            array_path="derived/chi_fit",
            dtype="float64",
            shape=(76, 64),
            chunk_shape=(16, 64),
        ),
        result_handles=(
            build_result_handle_ref(
                handle_id="result:transmon-coupler-014:characterization-report",
                kind="characterization_report",
                status="materialized",
                label="Coupler characterization report",
                metadata_record=build_metadata_record_ref(
                    "result_handle",
                    "result_handle:612",
                    version=3,
                ),
                payload_backend="markdown_artifact",
                payload_format="markdown",
                payload_role="report_artifact",
                payload_locator="artifacts/fit-report.md",
                provenance_task_id=305,
                provenance=build_result_provenance_ref(
                    source_dataset_id="transmon-coupler-014",
                    source_task_id=305,
                    analysis_run_record=analysis_run_record,
                ),
            ),
        ),
    )


def _build_pending_result_refs(
    *,
    task_id: int,
    draft: TaskCreateDraft,
) -> TaskResultRefs:
    pending_record = build_metadata_record_ref(
        "result_handle",
        f"result_handle:pending:{task_id}",
        version=1,
    )
    return TaskResultRefs(
        result_handle=TaskResultHandle(),
        metadata_records=(pending_record,),
        trace_payload=None,
        result_handles=(
            build_result_handle_ref(
                handle_id=f"task-result:{task_id}:primary",
                kind=_default_result_handle_kind(draft.kind),
                status="pending",
                label=_default_result_handle_label(draft.kind),
                metadata_record=pending_record,
                payload_backend=None,
                payload_format=None,
                payload_role=None,
                payload_locator=None,
                provenance_task_id=task_id,
                provenance=build_result_provenance_ref(
                    source_dataset_id=draft.dataset_id,
                    source_task_id=task_id,
                ),
            ),
        ),
    )


def _default_result_handle_kind(task_kind: str) -> ResultHandleKind:
    if task_kind == "characterization":
        return "characterization_report"
    if task_kind == "post_processing":
        return "fit_summary"
    return "simulation_trace"


def _default_result_handle_label(task_kind: str) -> str:
    if task_kind == "characterization":
        return "Pending characterization report"
    if task_kind == "post_processing":
        return "Pending fit summary"
    return "Pending simulation trace"
