from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def _sample_definition_source(circuit_name: str) -> str:
    return (
        "circuit:\n"
        f"  name: {circuit_name}\n"
        "  family: fluxonium\n"
        "  elements:\n"
        "    junction:\n"
        "      ej_ghz: 8.45\n"
        "    shunt_inductor:\n"
        "      el_ghz: 0.42\n"
    )


def test_definition_authoring_catalog_to_editor_save_update_round_trip() -> None:
    catalog_response = client.get("/circuit-definitions")

    assert catalog_response.status_code == 200
    catalog_rows = catalog_response.json()
    assert len(catalog_rows) == 3
    assert set(catalog_rows[0]) == {
        "created_at",
        "definition_id",
        "element_count",
        "name",
        "preview_artifact_count",
        "validation_status",
    }

    detail_response = client.get(f"/circuit-definitions/{catalog_rows[0]['definition_id']}")
    assert detail_response.status_code == 200
    original_detail = detail_response.json()
    assert original_detail["definition_id"] == catalog_rows[0]["definition_id"]
    assert original_detail["preview_artifact_count"] == 3
    assert len(original_detail["preview_artifacts"]) == 3
    assert original_detail["validation_summary"] == {
        "status": "warning",
        "notice_count": 3,
        "warning_count": 1,
    }

    created_response = client.post(
        "/circuit-definitions",
        json={
            "name": "RewriteDefinitionAuthoringSmoke",
            "source_text": _sample_definition_source("rewrite_definition_authoring_smoke"),
        },
    )

    assert created_response.status_code == 201
    created_payload = created_response.json()
    created_detail = created_payload["definition"]
    created_definition_id = int(created_detail["definition_id"])
    assert created_payload["operation"] == "created"
    assert created_detail["name"] == "RewriteDefinitionAuthoringSmoke"
    assert created_detail["source_text"] == _sample_definition_source(
        "rewrite_definition_authoring_smoke"
    ).rstrip()
    assert '"circuit": "rewrite_definition_authoring_smoke"' in created_detail["normalized_output"]
    assert created_detail["preview_artifacts"] == [
        "definition.normalized.json",
        "schematic-input.yaml",
        "parameter-bundle.toml",
    ]

    created_detail_response = client.get(f"/circuit-definitions/{created_definition_id}")
    assert created_detail_response.status_code == 200
    assert created_detail_response.json() == created_detail

    updated_response = client.put(
        f"/circuit-definitions/{created_definition_id}",
        json={
            "name": "RewriteDefinitionAuthoringSmokeV2",
            "source_text": _sample_definition_source("rewrite_definition_authoring_smoke_v2"),
        },
    )

    assert updated_response.status_code == 200
    updated_payload = updated_response.json()
    updated_detail = updated_payload["definition"]
    assert updated_payload["operation"] == "updated"
    assert updated_detail["name"] == "RewriteDefinitionAuthoringSmokeV2"
    assert updated_detail["source_text"] == _sample_definition_source(
        "rewrite_definition_authoring_smoke_v2"
    ).rstrip()
    assert '"circuit": "rewrite_definition_authoring_smoke_v2"' in updated_detail["normalized_output"]
    assert updated_detail["validation_summary"]["status"] == "warning"
    assert updated_detail["preview_artifacts"] == created_detail["preview_artifacts"]

    refreshed_catalog_response = client.get("/circuit-definitions?sort_by=created_at&sort_order=desc")
    assert refreshed_catalog_response.status_code == 200
    refreshed_catalog_rows = refreshed_catalog_response.json()
    assert refreshed_catalog_rows[0]["definition_id"] == created_definition_id
    assert refreshed_catalog_rows[0]["name"] == "RewriteDefinitionAuthoringSmokeV2"
    assert "source_text" not in refreshed_catalog_rows[0]
    assert "normalized_output" not in refreshed_catalog_rows[0]
