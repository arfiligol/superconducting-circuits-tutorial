from dataclasses import replace

from src.app.domain.tasks import TaskSubmissionDraft
from src.app.infrastructure.runtime import (
    get_rewrite_app_state_repository,
    get_rewrite_task_repository,
    get_storage_metadata_repository,
    get_task_service,
    get_task_snapshot_repository,
    reset_runtime_state,
)
from src.app.infrastructure.storage_reference_factory import build_result_handle_ref


def test_runtime_task_submission_persists_pending_result_metadata() -> None:
    service = get_task_service()

    task = service.submit_task(
        TaskSubmissionDraft(
            kind="characterization",
            dataset_id=None,
            definition_id=None,
            summary=None,
        )
    )
    storage_repository = get_storage_metadata_repository()

    assert storage_repository.get_storage_record("result_handle:pending:306") == (
        task.result_refs.metadata_records[0]
    )
    assert storage_repository.get_result_handle("task-result:306:primary") == (
        task.result_refs.result_handles[0]
    )


def test_runtime_bootstrap_persists_seeded_trace_payload_and_materialized_handles() -> None:
    service = get_task_service()
    storage_repository = get_storage_metadata_repository()

    task = service.get_task(303)

    assert task.result_refs.trace_payload is not None
    assert storage_repository.get_storage_record("trace_batch:88") == (
        task.result_refs.metadata_records[0]
    )
    assert storage_repository.get_trace_payload(task.result_refs.trace_payload.store_key) == (
        task.result_refs.trace_payload
    )
    assert storage_repository.get_result_handle("result:fluxonium-2025-031:fit-summary") == (
        task.result_refs.result_handles[0]
    )


def test_task_service_uses_persisted_task_repository_not_app_state_scaffold() -> None:
    app_state_repository = get_rewrite_app_state_repository()
    persisted_task = get_task_service().get_task(303)

    assert app_state_repository.list_tasks() == []
    assert app_state_repository.get_task(303) is None
    assert persisted_task.result_refs.trace_batch_id == 88
    assert persisted_task.result_refs.result_handles[0].handle_id == (
        "result:fluxonium-2025-031:fit-summary"
    )


def test_runtime_reset_prefers_persisted_result_handle_over_seed_defaults() -> None:
    initial_task = get_task_service().get_task(303)
    storage_repository = get_storage_metadata_repository()
    updated_result_handle = build_result_handle_ref(
        handle_id=initial_task.result_refs.result_handles[0].handle_id,
        kind=initial_task.result_refs.result_handles[0].kind,
        status=initial_task.result_refs.result_handles[0].status,
        label="Persisted fit summary override",
        metadata_record=replace(
            initial_task.result_refs.result_handles[0].metadata_record,
            version=9,
        ),
        payload_backend=initial_task.result_refs.result_handles[0].payload_backend,
        payload_format=initial_task.result_refs.result_handles[0].payload_format,
        payload_role=initial_task.result_refs.result_handles[0].payload_role,
        payload_locator="artifacts/persisted-fit-summary.json",
        provenance_task_id=initial_task.result_refs.result_handles[0].provenance_task_id,
        provenance=initial_task.result_refs.result_handles[0].provenance,
    )
    storage_repository.save_result_handle(updated_result_handle)

    reset_runtime_state()

    reloaded_task = get_task_service().get_task(303)

    assert reloaded_task.result_refs.result_handles[0].label == "Persisted fit summary override"
    assert reloaded_task.result_refs.result_handles[0].payload_locator == (
        "artifacts/persisted-fit-summary.json"
    )
    assert reloaded_task.result_refs.metadata_records[1].version == 9


def test_runtime_reset_prefers_persisted_task_snapshot_over_scaffold_defaults() -> None:
    task_snapshot_repository = get_task_snapshot_repository()
    initial_task = get_task_service().get_task(302)
    updated_task = replace(
        initial_task,
        status="failed",
        summary="Persisted task snapshot override",
        progress=replace(
            initial_task.progress,
            phase="failed",
            percent_complete=100,
            summary="Persisted failure summary.",
            updated_at="2026-03-12 11:05:00",
        ),
    )
    task_snapshot_repository.save_task_snapshot(updated_task)

    reset_runtime_state()

    reloaded_task = get_task_service().get_task(302)

    assert reloaded_task.status == "failed"
    assert reloaded_task.summary == "Persisted task snapshot override"
    assert reloaded_task.progress.phase == "failed"
    assert reloaded_task.progress.summary == "Persisted failure summary."


def test_runtime_reset_keeps_submitted_task_row_and_storage_refs() -> None:
    submitted_task = get_task_service().submit_task(
        TaskSubmissionDraft(
            kind="characterization",
            dataset_id=None,
            definition_id=None,
            summary=None,
        )
    )

    reset_runtime_state()

    reloaded_task = get_task_service().get_task(submitted_task.task_id)

    assert reloaded_task.task_id == submitted_task.task_id
    assert reloaded_task.status == "queued"
    assert reloaded_task.dataset_id == "fluxonium-2025-031"
    assert reloaded_task.result_refs.result_handles == submitted_task.result_refs.result_handles
    assert get_rewrite_task_repository().get_task(submitted_task.task_id) is not None
