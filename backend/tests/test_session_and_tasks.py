from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)


def test_get_session_returns_dev_stub_and_active_dataset() -> None:
    response = client.get("/session")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "rewrite-local-session"
    assert payload["auth"]["state"] == "authenticated"
    assert payload["auth"]["mode"] == "development_stub"
    assert payload["auth"]["can_submit_tasks"] is True
    assert payload["active_dataset"]["dataset_id"] == "fluxonium-2025-031"


def test_patch_session_active_dataset_updates_context() -> None:
    response = client.patch("/session/active-dataset", json={"dataset_id": "transmon-coupler-014"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_dataset"]["dataset_id"] == "transmon-coupler-014"
    assert payload["active_dataset"]["family"] == "Transmon"


def test_patch_session_active_dataset_can_clear_selection() -> None:
    response = client.patch("/session/active-dataset", json={"dataset_id": None})

    assert response.status_code == 200
    assert response.json()["active_dataset"] is None


def test_patch_session_active_dataset_rejects_missing_dataset() -> None:
    response = client.patch("/session/active-dataset", json={"dataset_id": "missing-dataset"})

    assert response.status_code == 404


def test_list_tasks_returns_seeded_summaries() -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    payload = response.json()
    assert [task["task_id"] for task in payload] == [301, 302, 303]
    assert payload[0]["status"] == "running"


def test_list_tasks_supports_filters_and_limit() -> None:
    response = client.get(
        "/tasks?status=queued&lane=characterization&dataset_id=transmon-coupler-014&limit=1"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "task_id": 302,
            "kind": "characterization",
            "lane": "characterization",
            "status": "queued",
            "submitted_at": "2026-03-12 08:40:00",
            "submitted_by": "Rewrite Local User",
            "dataset_id": "transmon-coupler-014",
            "definition_id": None,
            "summary": "Coupler dataset characterization is queued.",
        }
    ]


def test_get_task_returns_detail_payload() -> None:
    response = client.get("/tasks/303")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task_id"] == 303
    assert payload["queue_backend"] == "in_memory_scaffold"
    assert payload["worker_task_name"] == "post_processing_run_task"
    assert payload["result_refs"]["trace_batch_id"] == 88


def test_get_task_returns_not_found_for_missing_task() -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_submit_characterization_task_uses_active_dataset() -> None:
    response = client.post("/tasks", json={"kind": "characterization"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["operation"] == "submitted"
    assert payload["task"]["task_id"] == 304
    assert payload["task"]["dataset_id"] == "fluxonium-2025-031"
    assert payload["task"]["submitted_from_active_dataset"] is True
    assert payload["task"]["worker_task_name"] == "characterization_smoke_task"


def test_submit_simulation_task_returns_queued_task_detail() -> None:
    response = client.post(
        "/tasks",
        json={
            "kind": "simulation",
            "definition_id": 18,
            "summary": "Queue one fluxonium simulation preview.",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["task"]["task_id"] == 304
    assert payload["task"]["lane"] == "simulation"
    assert payload["task"]["definition_id"] == 18
    assert payload["task"]["summary"] == "Queue one fluxonium simulation preview."
    assert payload["task"]["worker_task_name"] == "simulation_smoke_task"


def test_submit_simulation_task_requires_definition_id() -> None:
    response = client.post("/tasks", json={"kind": "simulation"})

    assert response.status_code == 422
    assert response.json()["detail"] == "Simulation tasks require definition_id."


def test_submit_post_processing_task_requires_dataset_context() -> None:
    cleared = client.patch("/session/active-dataset", json={"dataset_id": None})
    assert cleared.status_code == 200

    response = client.post("/tasks", json={"kind": "post_processing"})

    assert response.status_code == 422
    assert (
        response.json()["detail"]
        == "post_processing tasks require dataset_id or an active dataset."
    )
