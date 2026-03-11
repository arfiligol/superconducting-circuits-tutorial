from sc_core.circuit_definitions import DEFAULT_PREVIEW_ARTIFACTS, inspect_circuit_definition_source
from sc_core.execution import TaskResultHandle
from src.app.domain.circuit_definitions import CircuitDefinitionDraft
from src.app.infrastructure.rewrite_app_state_repository import InMemoryRewriteAppStateRepository
from src.app.infrastructure.rewrite_catalog_repository import InMemoryRewriteCatalogRepository


def test_packaged_sc_core_import_is_available_to_backend() -> None:
    inspection = inspect_circuit_definition_source(
        "circuit:\n  name: backend_probe\n  family: fluxonium\n"
    )

    assert inspection.circuit_name == "backend_probe"
    assert inspection.family == "fluxonium"
    assert inspection.normalized_output.startswith("{\n")


def test_repository_creation_uses_sc_core_inspection_contract() -> None:
    repository = InMemoryRewriteCatalogRepository()
    source_text = "circuit:\n  name: packaged_boundary\n  family: readout\n  elements:\n    port:\n"

    created = repository.create_circuit_definition(
        CircuitDefinitionDraft(name="PackagedBoundary", source_text=source_text)
    )
    inspection = inspect_circuit_definition_source(source_text)

    assert created.element_count == inspection.element_count
    assert created.normalized_output == inspection.normalized_output
    assert created.preview_artifacts == DEFAULT_PREVIEW_ARTIFACTS
    assert tuple((notice.level, notice.message) for notice in created.validation_notices) == tuple(
        (notice.level, notice.message) for notice in inspection.validation_notices
    )


def test_backend_task_result_refs_use_shared_execution_and_storage_contracts() -> None:
    repository = InMemoryRewriteAppStateRepository()

    task = repository.get_task(303)

    assert task is not None
    assert task.result_refs.result_handle == TaskResultHandle(trace_batch_id=88)
    assert task.result_refs.storage_linkage().to_payload() == {"trace_batch_id": 88}
