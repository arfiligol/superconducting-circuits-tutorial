import pytest
from fastapi.testclient import TestClient
from src.app.infrastructure.runtime import reset_runtime_state
from src.app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_catalog_state() -> None:
    reset_runtime_state()


def test_list_datasets_returns_seeded_summaries() -> None:
    response = client.get("/datasets")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["dataset_id"] == "fluxonium-2025-031"
    assert payload[0]["device_type"] == "Unspecified"
    assert payload[0]["capability_count"] == 0
    assert payload[0]["tag_count"] == 3


def test_list_datasets_supports_family_filter_and_name_sort() -> None:
    filtered = client.get("/datasets?family=Fluxonium")
    assert filtered.status_code == 200
    assert [item["dataset_id"] for item in filtered.json()] == ["fluxonium-2025-031"]

    sorted_response = client.get("/datasets?sort_by=name&sort_order=asc")
    assert sorted_response.status_code == 200
    assert [item["name"] for item in sorted_response.json()] == [
        "Coupler detuning 014",
        "Fluxonium sweep 031",
    ]


def test_get_dataset_returns_detail_payload() -> None:
    response = client.get("/datasets/fluxonium-2025-031")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Fluxonium sweep 031"
    assert payload["preview_columns"] == ["frequency", "bias", "T1", "fit"]
    assert payload["metrics"] == {
        "capability_count": 0,
        "tag_count": 3,
        "preview_row_count": 3,
        "artifact_count": 4,
        "lineage_depth": 4,
    }


def test_patch_dataset_metadata_updates_seeded_dataset() -> None:
    response = client.patch(
        "/datasets/fluxonium-2025-031/metadata",
        json={
            "device_type": "Fluxonium",
            "capabilities": ["t1", "spectroscopy"],
            "source": "reviewed",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated_fields"] == ["device_type", "capabilities", "source"]
    assert payload["dataset"]["device_type"] == "Fluxonium"
    assert payload["dataset"]["capabilities"] == ["t1", "spectroscopy"]
    assert payload["dataset"]["source"] == "reviewed"
    assert payload["dataset"]["metrics"]["capability_count"] == 2


def test_patch_dataset_metadata_rejects_duplicate_capabilities() -> None:
    response = client.patch(
        "/datasets/fluxonium-2025-031/metadata",
        json={
            "device_type": "Fluxonium",
            "capabilities": ["t1", "t1"],
            "source": "reviewed",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_failed"
    assert response.json()["error"]["category"] == "validation"


def test_get_dataset_returns_not_found_for_missing_id() -> None:
    response = client.get("/datasets/missing-dataset")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "dataset_not_found"


def test_list_circuit_definitions_returns_seeded_summaries() -> None:
    response = client.get("/circuit-definitions")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["name"] == "FloatingQubitWithXYLine"
    assert payload[0]["validation_status"] == "warning"
    assert payload[0]["preview_artifact_count"] == 3


def test_list_circuit_definitions_supports_search_and_sort() -> None:
    response = client.get("/circuit-definitions?search=Fluxonium&sort_by=name&sort_order=asc")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["FluxoniumReadoutChain"]


def test_get_circuit_definition_returns_detail_payload() -> None:
    response = client.get("/circuit-definitions/18")

    assert response.status_code == 200
    payload = response.json()
    assert payload["definition_id"] == 18
    assert payload["preview_artifacts"] == [
        "definition.normalized.json",
        "schematic-input.yaml",
        "parameter-bundle.toml",
    ]
    assert payload["validation_summary"] == {
        "status": "warning",
        "notice_count": 3,
        "warning_count": 1,
    }
    assert '"family": "fluxonium"' in payload["normalized_output"]


def test_create_update_and_delete_circuit_definition_flow() -> None:
    created = client.post(
        "/circuit-definitions",
        json={
            "name": "ReadoutPreview",
            "source_text": "circuit:\n  name: readout_preview\n  family: readout\n",
        },
    )

    assert created.status_code == 201
    created_payload = created.json()
    definition_id = int(created_payload["definition"]["definition_id"])
    assert created_payload["operation"] == "created"
    assert created_payload["definition"]["name"] == "ReadoutPreview"
    assert '"circuit": "readout_preview"' in created_payload["definition"]["normalized_output"]

    updated = client.put(
        f"/circuit-definitions/{definition_id}",
        json={
            "name": "ReadoutPreviewV2",
            "source_text": "circuit:\n  name: readout_preview_v2\n  family: readout\n",
        },
    )
    assert updated.status_code == 200
    updated_payload = updated.json()
    assert updated_payload["operation"] == "updated"
    assert updated_payload["definition"]["name"] == "ReadoutPreviewV2"
    assert '"circuit": "readout_preview_v2"' in updated_payload["definition"]["normalized_output"]

    deleted = client.delete(f"/circuit-definitions/{definition_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/circuit-definitions/{definition_id}")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "circuit_definition_not_found"


def test_create_circuit_definition_rejects_blank_name() -> None:
    response = client.post(
        "/circuit-definitions",
        json={
            "name": "   ",
            "source_text": "circuit:\n  name: readout_preview\n  family: readout\n",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_failed"
