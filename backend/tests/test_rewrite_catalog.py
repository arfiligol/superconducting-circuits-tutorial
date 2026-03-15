import pytest
from src.app.domain.datasets import (
    CharacterizationResultBrowseQuery,
    CharacterizationTaggingRequest,
    DatasetProfileUpdate,
    DesignBrowseQuery,
    TraceBrowseQuery,
)
from src.app.infrastructure.rewrite_app_state_repository import InMemoryRewriteAppStateRepository
from src.app.infrastructure.rewrite_catalog_repository import InMemoryRewriteCatalogRepository
from src.app.services.dataset_service import DatasetService
from src.app.services.service_errors import ServiceError


@pytest.fixture
def app_state_repository() -> InMemoryRewriteAppStateRepository:
    return InMemoryRewriteAppStateRepository()


@pytest.fixture
def catalog_repository() -> InMemoryRewriteCatalogRepository:
    return InMemoryRewriteCatalogRepository()


@pytest.fixture
def dataset_service(
    app_state_repository: InMemoryRewriteAppStateRepository,
    catalog_repository: InMemoryRewriteCatalogRepository,
) -> DatasetService:
    return DatasetService(
        repository=catalog_repository,
        session_repository=app_state_repository,
    )


def test_dataset_service_lists_visible_catalog_rows_for_active_workspace(
    dataset_service: DatasetService,
) -> None:
    rows = dataset_service.list_dataset_catalog()

    assert [row.dataset_id for row in rows] == [
        "fluxonium-2025-031",
        "resonator-chip-002",
    ]
    assert rows[0].allowed_actions.select is True
    assert rows[0].allowed_actions.update_profile is True
    assert rows[0].allowed_actions.publish is True
    assert rows[0].allowed_actions.archive is True


def test_dataset_service_rebinds_catalog_visibility_after_workspace_switch(
    dataset_service: DatasetService,
    app_state_repository: InMemoryRewriteAppStateRepository,
) -> None:
    app_state_repository.set_active_workspace_id("ws-modeling")

    rows = dataset_service.list_dataset_catalog()

    assert [row.dataset_id for row in rows] == ["transmon-coupler-014"]
    assert rows[0].allowed_actions.publish is False
    assert rows[0].allowed_actions.archive is False


def test_dataset_service_reads_and_updates_dashboard_profile_surface(
    dataset_service: DatasetService,
) -> None:
    profile = dataset_service.get_dataset_profile("fluxonium-2025-031")

    assert profile.dataset_id == "fluxonium-2025-031"
    assert profile.device_type == "Fluxonium"
    assert profile.capabilities == ("characterization", "simulation_review")

    result = dataset_service.update_dataset_profile(
        "fluxonium-2025-031",
        DatasetProfileUpdate(
            device_type="Fluxonium-X",
            capabilities=("characterization", "comparison"),
            source="manual",
        ),
    )

    assert result.updated_fields == ("device_type", "capabilities", "source")
    assert result.dataset.device_type == "Fluxonium-X"
    assert result.dataset.capabilities == ("characterization", "comparison")
    assert result.dataset.source == "manual"
    assert result.dataset.allowed_actions.update_profile is True


def test_dataset_service_exposes_tagged_metrics_and_summary_first_browse_contract(
    dataset_service: DatasetService,
) -> None:
    metrics = dataset_service.list_tagged_core_metrics("fluxonium-2025-031")
    designs = dataset_service.list_designs(
        "fluxonium-2025-031",
        DesignBrowseQuery(search="Flux Scan A"),
    )
    trace_rows = dataset_service.list_trace_metadata(
        "fluxonium-2025-031",
        "design_flux_scan_a",
        TraceBrowseQuery(family="y_matrix", source_kind="measurement"),
    )
    trace_detail = dataset_service.get_trace_detail(
        "fluxonium-2025-031",
        "design_flux_scan_a",
        "trace_flux_a_measurement",
    )

    assert [metric.metric_id for metric in metrics] == [
        "metric-fluxonium-f01",
        "metric-fluxonium-anharmonicity",
    ]
    assert [design.design_id for design in designs] == ["design_flux_scan_a"]
    assert designs[0].compare_readiness == "ready"

    assert [row.trace_id for row in trace_rows] == [
        "trace_flux_a_measurement",
        "trace_flux_a_phase",
    ]
    assert not hasattr(trace_rows[0], "preview_payload")
    assert not hasattr(trace_rows[0], "payload_ref")

    assert trace_detail.trace_id == "trace_flux_a_measurement"
    assert trace_detail.preview_payload["kind"] == "sampled_series"
    assert trace_detail.payload_ref is not None
    assert trace_detail.payload_ref.store_key.endswith("batch_4.zarr")
    assert trace_detail.result_handles[0].handle_id == "result:fluxonium-2025-031:fit-summary"


def test_dataset_service_exposes_characterization_result_summary_and_detail_surfaces(
    dataset_service: DatasetService,
) -> None:
    result_rows = dataset_service.list_characterization_results(
        "fluxonium-2025-031",
        "design_flux_scan_a",
        CharacterizationResultBrowseQuery(status="completed"),
    )
    result_detail = dataset_service.get_characterization_result(
        "fluxonium-2025-031",
        "design_flux_scan_a",
        "char-fit-flux-a-01",
    )

    assert [row.result_id for row in result_rows] == ["char-fit-flux-a-01"]
    assert result_rows[0].dataset_id == "fluxonium-2025-031"
    assert result_rows[0].design_id == "design_flux_scan_a"
    assert result_rows[0].status == "completed"
    assert result_rows[0].provenance_summary == "Measurement batch #4 + layout batch #2"

    assert result_detail.result_id == "char-fit-flux-a-01"
    assert result_detail.analysis_id == "admittance_extraction"
    assert result_detail.input_trace_ids == (
        "trace_flux_a_measurement",
        "trace_flux_a_layout",
    )
    assert result_detail.payload["fit_table"][0]["parameter"] == "f01"
    assert result_detail.artifact_refs[0].artifact_id == "artifact-fit-table-flux-a-01"


def test_dataset_service_applies_identify_tagging_and_updates_dashboard_metrics_summary(
    dataset_service: DatasetService,
) -> None:
    detail_before = dataset_service.get_characterization_result(
        "resonator-chip-002",
        "design_resonator_temp",
        "char-resonator-temp-qi",
    )

    assert detail_before.identify_surface.applied_tags == ()
    assert detail_before.identify_surface.source_parameters[0].current_designated_metric is None

    result = dataset_service.apply_characterization_tagging(
        "resonator-chip-002",
        "design_resonator_temp",
        "char-resonator-temp-qi",
        CharacterizationTaggingRequest(
            artifact_id="artifact-resonator-temp-table",
            source_parameter="Qi_low_temp",
            designated_metric="qi_low_temp",
        ),
    )

    detail_after = dataset_service.get_characterization_result(
        "resonator-chip-002",
        "design_resonator_temp",
        "char-resonator-temp-qi",
    )
    metrics = dataset_service.list_tagged_core_metrics("resonator-chip-002")

    assert result.tagging_status == "applied"
    assert result.tagged_metric.metric_id == "metric-resonator-chip-002-qi-low-temp"
    assert detail_after.identify_surface.applied_tags[0].designated_metric == "qi_low_temp"
    assert (
        detail_after.identify_surface.source_parameters[0].current_designated_metric
        == "qi_low_temp"
    )
    assert [metric.metric_id for metric in metrics] == [
        "metric-resonator-chip-002-qi-low-temp",
    ]
    assert metrics[0].label == "Low Temperature Qi"


def test_dataset_service_rejects_invisible_dataset_outside_active_workspace(
    dataset_service: DatasetService,
) -> None:
    with pytest.raises(ServiceError) as exc_info:
        dataset_service.get_dataset_profile("transmon-coupler-014")

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "dataset_not_visible_in_workspace"
    assert exc_info.value.category == "permission_denied"
