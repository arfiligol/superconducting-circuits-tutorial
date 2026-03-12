from src.app.domain.tasks import TaskSubmissionDraft
from src.app.infrastructure.runtime import (
    get_storage_metadata_repository,
    get_task_service,
)


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
