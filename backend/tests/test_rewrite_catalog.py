import pytest
from fastapi.testclient import TestClient
from sc_core.storage import STORAGE_CONTRACT_VERSION
from src.app.infrastructure.runtime import reset_runtime_state
from src.app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_catalog_state() -> None:
    reset_runtime_state()


def test_list_dataset_catalog_only_returns_visible_workspace_rows() -> None:
    response = client.get("/datasets?limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert [row["dataset_id"] for row in payload["data"]["rows"]] == [
        "fluxonium-2025-031",
        "resonator-chip-002",
    ]
    assert payload["data"]["rows"][0]["allowed_actions"] == {
        "select": True,
        "update_profile": True,
        "publish": True,
        "archive": True,
    }
    assert payload["meta"]["limit"] == 10
    assert payload["meta"]["has_more"] is False
    assert payload["meta"]["next_cursor"] is None


def test_list_dataset_catalog_rebinds_with_active_workspace() -> None:
    client.patch("/session/active-workspace", json={"workspace_id": "ws-modeling"})

    response = client.get("/datasets")

    assert response.status_code == 200
    payload = response.json()
    assert [row["dataset_id"] for row in payload["data"]["rows"]] == ["transmon-coupler-014"]
    assert payload["data"]["rows"][0]["allowed_actions"] == {
        "select": True,
        "update_profile": True,
        "publish": False,
        "archive": False,
    }


def test_get_dataset_profile_and_metrics_return_dashboard_contract() -> None:
    profile_response = client.get("/datasets/fluxonium-2025-031/profile")

    assert profile_response.status_code == 200
    profile_payload = profile_response.json()
    assert profile_payload["ok"] is True
    assert profile_payload["data"] == {
        "dataset_id": "fluxonium-2025-031",
        "name": "Fluxonium sweep 031",
        "family": "Fluxonium",
        "owner_display_name": "Device Lab",
        "owner_user_id": "researcher-01",
        "workspace_id": "ws-device-lab",
        "visibility_scope": "private",
        "lifecycle_state": "active",
        "updated_at": "2026-03-14T10:20:00Z",
        "device_type": "Fluxonium",
        "capabilities": ["characterization", "simulation_review"],
        "source": "inferred",
        "status": "Ready",
        "allowed_actions": {
            "select": True,
            "update_profile": True,
            "publish": True,
            "archive": True,
        },
    }

    metrics_response = client.get("/datasets/fluxonium-2025-031/metrics-summary")

    assert metrics_response.status_code == 200
    metrics_payload = metrics_response.json()
    assert metrics_payload["data"]["rows"] == [
        {
            "metric_id": "metric-fluxonium-f01",
            "label": "Qubit Transition",
            "source_parameter": "Im(Y11)",
            "designated_metric": "f01",
            "tagged_at": "2026-03-14T11:05:00Z",
        },
        {
            "metric_id": "metric-fluxonium-anharmonicity",
            "label": "Anharmonicity",
            "source_parameter": "Im(Y12)",
            "designated_metric": "alpha",
            "tagged_at": "2026-03-14T11:08:00Z",
        },
    ]


def test_patch_dataset_profile_updates_canonical_profile_surface() -> None:
    response = client.patch(
        "/datasets/fluxonium-2025-031/profile",
        json={
            "device_type": "Fluxonium-X",
            "capabilities": ["characterization", "comparison"],
            "source": "manual",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["updated_fields"] == ["device_type", "capabilities", "source"]
    assert payload["data"]["dataset"]["device_type"] == "Fluxonium-X"
    assert payload["data"]["dataset"]["capabilities"] == ["characterization", "comparison"]
    assert payload["data"]["dataset"]["source"] == "manual"
    assert payload["data"]["dataset"]["updated_at"] == "2026-03-15T00:30:00Z"


def test_patch_dataset_profile_rejects_duplicate_capabilities_with_error_envelope() -> None:
    response = client.patch(
        "/datasets/fluxonium-2025-031/profile",
        json={
            "device_type": "Fluxonium-X",
            "capabilities": ["characterization", "characterization"],
            "source": "manual",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "ok": False,
        "error": {
            "code": "request_validation_failed",
            "category": "validation_error",
            "message": "capabilities must not contain duplicates.",
            "retryable": False,
        },
    }


def test_list_designs_returns_dataset_local_design_scope_rows() -> None:
    response = client.get("/datasets/fluxonium-2025-031/designs?limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["rows"] == [
        {
            "design_id": "design_flux_scan_a",
            "dataset_id": "fluxonium-2025-031",
            "name": "Flux Scan A",
            "source_coverage": {"measurement": 2, "layout_simulation": 1},
            "compare_readiness": "ready",
            "trace_count": 3,
            "updated_at": "2026-03-14T10:24:00Z",
        }
    ]
    assert payload["meta"]["next_cursor"] == "1"
    assert payload["meta"]["prev_cursor"] is None
    assert payload["meta"]["filter_echo"] == {
        "dataset_id": "fluxonium-2025-031",
        "search": None,
    }


def test_list_trace_metadata_keeps_summary_paths_small_and_filterable() -> None:
    response = client.get(
        "/datasets/fluxonium-2025-031/designs/design_flux_scan_a/traces"
        "?family=y_matrix&source_kind=measurement"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert [row["trace_id"] for row in payload["data"]["rows"]] == [
        "trace_flux_a_measurement",
        "trace_flux_a_phase",
    ]
    assert "preview_payload" not in payload["data"]["rows"][0]
    assert "payload_ref" not in payload["data"]["rows"][0]
    assert payload["meta"]["filter_echo"] == {
        "dataset_id": "fluxonium-2025-031",
        "design_id": "design_flux_scan_a",
        "search": None,
        "family": "y_matrix",
        "representation": None,
        "source_kind": "measurement",
        "trace_mode_group": None,
    }


def test_get_trace_detail_returns_preview_payload_and_provenance_handles() -> None:
    response = client.get(
        "/datasets/fluxonium-2025-031/designs/design_flux_scan_a/traces/trace_flux_a_measurement"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["axes"] == [
        {"name": "frequency", "unit": "GHz", "length": 401},
        {"name": "flux_bias", "unit": "Phi0", "length": 11},
    ]
    assert payload["data"]["preview_payload"]["kind"] == "sampled_series"
    assert payload["data"]["payload_ref"]["contract_version"] == STORAGE_CONTRACT_VERSION
    assert payload["data"]["result_handles"][0]["handle_id"] == "result:fluxonium-2025-031:fit-summary"
    assert payload["data"]["result_handles"][0]["provenance"] == {
        "source_dataset_id": "fluxonium-2025-031",
        "source_task_id": 303,
        "trace_batch_record": {
            "backend": "sqlite_metadata",
            "record_type": "trace_batch",
            "record_id": "trace_batch:88",
            "version": 1,
            "schema_version": "sqlite_metadata.v1",
        },
        "analysis_run_record": None,
    }


def test_dataset_surface_rejects_dataset_outside_active_workspace() -> None:
    response = client.get("/datasets/transmon-coupler-014/profile")

    assert response.status_code == 403
    assert response.json() == {
        "ok": False,
        "error": {
            "code": "dataset_not_visible_in_workspace",
            "category": "permission_denied",
            "message": "The selected dataset is not visible in the active workspace.",
            "retryable": False,
        },
    }
