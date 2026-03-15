from fastapi.testclient import TestClient

from src.app.domain.audit import AuditRecord
from src.app.infrastructure.runtime import get_task_audit_repository
from src.app.main import app

client = TestClient(app)


def test_audit_list_returns_workspace_scoped_rows_and_meta() -> None:
    client.post("/tasks", json={"kind": "characterization"})
    client.post("/tasks/301/cancel")

    response = client.get("/audit-logs?limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert [row["action_kind"] for row in payload["data"]["rows"]] == [
        "task.cancel_requested",
        "task.submitted",
    ]
    assert payload["data"]["rows"][0]["workspace_id"] == "ws-device-lab"
    assert payload["data"]["rows"][0]["actor_summary"] == {
        "user_id": "researcher-01",
        "display_name": "Rewrite Local User",
    }
    assert payload["meta"]["limit"] == 10
    assert payload["meta"]["filter_echo"]["workspace_id"] == "ws-device-lab"


def test_audit_list_supports_filters_and_cursor_navigation() -> None:
    client.post("/tasks", json={"kind": "characterization"})
    client.post("/tasks/301/cancel")
    client.post("/tasks/301/terminate")

    first_page = client.get("/audit-logs?limit=1")
    assert first_page.status_code == 200
    first_row = first_page.json()["data"]["rows"][0]

    filtered = client.get("/audit-logs?action_kind=task.cancel_requested&resource_kind=task")
    assert filtered.status_code == 200
    assert [row["action_kind"] for row in filtered.json()["data"]["rows"]] == [
        "task.cancel_requested"
    ]

    second_page = client.get(f"/audit-logs?limit=2&after={first_row['audit_id']}")
    assert second_page.status_code == 200
    assert [row["action_kind"] for row in second_page.json()["data"]["rows"]] == [
        "task.cancel_requested",
        "task.submitted",
    ]


def test_audit_detail_returns_redacted_payload() -> None:
    repository = get_task_audit_repository()
    repository.append(
        AuditRecord(
            audit_id="audit:manual:redaction",
            occurred_at="2026-03-16T09:00:00Z",
            actor_user_id="researcher-01",
            actor_display_name="Rewrite Local User",
            session_id="rewrite-local-session",
            correlation_id="corr:redaction",
            workspace_id="ws-device-lab",
            action_kind="task.submitted",
            resource_kind="task",
            resource_id="999",
            outcome="accepted",
            payload={
                "safe_field": "visible",
                "api_token": "secret-value",
                "nested": {"password": "secret", "safe_nested": "kept"},
            },
            debug_ref="debug:redaction",
        )
    )

    response = client.get("/audit-logs/audit:manual:redaction")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["correlation_id"] == "corr:redaction"
    assert payload["data"]["debug_ref"] == "debug:redaction"
    assert payload["data"]["payload"] == {
        "safe_field": "visible",
        "api_token": "[redacted]",
        "nested": {"password": "[redacted]", "safe_nested": "kept"},
    }


def test_audit_export_summary_returns_read_surface() -> None:
    client.post("/tasks", json={"kind": "characterization"})

    response = client.get("/audit-logs/export-summary?action_kind=task.submitted")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["status"] == "completed"
    assert payload["data"]["workspace_id"] == "ws-device-lab"
    assert payload["data"]["filter_echo"] == {
        "workspace_id": "ws-device-lab",
        "actor_user_id": None,
        "action_kind": "task.submitted",
        "resource_kind": None,
        "outcome": None,
    }
    assert payload["data"]["artifact_ref"]["backend"] == "audit_export_preview"


def test_audit_query_denies_member_without_governance_permission() -> None:
    switch_response = client.patch("/session/active-workspace", json={"workspace_id": "ws-modeling"})
    assert switch_response.status_code == 200

    response = client.get("/audit-logs")

    assert response.status_code == 403
    assert response.json()["ok"] is False
    assert response.json()["error"]["code"] == "audit_access_denied"

    export_response = client.get("/audit-logs/export-summary")
    assert export_response.status_code == 403
    assert export_response.json()["error"]["code"] == "audit_export_denied"


def test_audit_query_denies_cross_workspace_access_for_non_admin() -> None:
    client.post("/tasks", json={"kind": "characterization"})

    response = client.get("/audit-logs?workspace_id=ws-modeling")

    assert response.status_code == 403
    assert response.json()["ok"] is False
    assert response.json()["error"]["code"] == "audit_access_denied"


def test_audit_detail_returns_not_found_for_missing_record() -> None:
    response = client.get("/audit-logs/audit:missing")

    assert response.status_code == 404
    assert response.json()["ok"] is False
    assert response.json()["error"]["code"] == "audit_record_not_found"


def test_audit_query_rejects_invalid_cursor_combination() -> None:
    response = client.get("/audit-logs?after=audit-1&before=audit-2")

    assert response.status_code == 400
    assert response.json()["ok"] is False
    assert response.json()["error"]["code"] == "audit_query_invalid"
