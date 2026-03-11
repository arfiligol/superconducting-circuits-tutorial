from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)


def test_list_datasets_returns_seeded_summaries() -> None:
    response = client.get("/datasets")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["dataset_id"] == "fluxonium-2025-031"


def test_get_dataset_returns_detail_payload() -> None:
    response = client.get("/datasets/fluxonium-2025-031")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Fluxonium sweep 031"
    assert payload["preview_columns"] == ["frequency", "bias", "T1", "fit"]


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
    assert payload["device_type"] == "Fluxonium"
    assert payload["capabilities"] == ["t1", "spectroscopy"]
    assert payload["source"] == "reviewed"


def test_list_circuit_definitions_returns_seeded_summaries() -> None:
    response = client.get("/circuit-definitions")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["name"] == "FloatingQubitWithXYLine"


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
    definition_id = int(created_payload["definition_id"])
    assert created_payload["name"] == "ReadoutPreview"

    updated = client.put(
        f"/circuit-definitions/{definition_id}",
        json={
            "name": "ReadoutPreviewV2",
            "source_text": "circuit:\n  name: readout_preview_v2\n  family: readout\n",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "ReadoutPreviewV2"

    deleted = client.delete(f"/circuit-definitions/{definition_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/circuit-definitions/{definition_id}")
    assert missing.status_code == 404
