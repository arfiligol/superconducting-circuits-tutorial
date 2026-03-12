import pytest
from fastapi.testclient import TestClient
from sc_core.storage import STORAGE_CONTRACT_VERSION
from src.app.domain.tasks import TaskLifecycleUpdate
from src.app.infrastructure.runtime import (
    get_task_service,
    reset_runtime_state,
)
from src.app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_app_state() -> None:
    reset_runtime_state()


def test_get_session_returns_dev_stub_and_active_dataset() -> None:
    response = client.get("/session")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "rewrite-local-session"
    assert payload["auth"]["state"] == "authenticated"
    assert payload["auth"]["mode"] == "development_stub"
    assert payload["auth"]["can_submit_tasks"] is True
    assert payload["identity"]["user_id"] == "researcher-01"
    assert payload["workspace"]["workspace_id"] == "ws-device-lab"
    assert payload["workspace"]["default_task_scope"] == "workspace"
    assert payload["workspace"]["active_dataset"]["dataset_id"] == "fluxonium-2025-031"
    assert payload["workspace"]["active_dataset"]["owner"] == "Device Lab"


def test_patch_session_active_dataset_updates_context() -> None:
    response = client.patch("/session/active-dataset", json={"dataset_id": "transmon-coupler-014"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace"]["active_dataset"]["dataset_id"] == "transmon-coupler-014"
    assert payload["workspace"]["active_dataset"]["family"] == "Transmon"


def test_patch_session_active_dataset_can_clear_selection() -> None:
    response = client.patch("/session/active-dataset", json={"dataset_id": None})

    assert response.status_code == 200
    assert response.json()["workspace"]["active_dataset"] is None


def test_patch_session_active_dataset_rejects_missing_dataset() -> None:
    response = client.patch("/session/active-dataset", json={"dataset_id": "missing-dataset"})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "dataset_not_found"
    assert response.json()["error"]["category"] == "not_found"


def test_list_tasks_returns_seeded_summaries() -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    payload = response.json()
    assert [task["task_id"] for task in payload] == [301, 302, 303]
    assert payload[0]["status"] == "running"
    assert payload[0]["workspace_slug"] == "device-lab"
    assert payload[0]["execution_mode"] == "run"


def test_list_tasks_hides_tasks_outside_session_visibility() -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    task_ids = [task["task_id"] for task in response.json()]
    assert 304 not in task_ids
    assert 305 not in task_ids


def test_list_tasks_supports_filters_scope_and_limit() -> None:
    response = client.get(
        "/tasks?status=completed&lane=simulation&scope=owned&dataset_id=fluxonium-2025-031&limit=1"
    )

    assert response.status_code == 200
    assert response.json()[0]["task_id"] == 303
    assert response.json()[0]["visibility_scope"] == "owned"

    workspace_response = client.get(
        "/tasks?status=queued&lane=characterization&scope=workspace&dataset_id=transmon-coupler-014&limit=1"
    )
    assert workspace_response.status_code == 200
    assert workspace_response.json()[0]["task_id"] == 302
    assert workspace_response.json()[0]["visibility_scope"] == "workspace"


def test_get_task_returns_detail_payload() -> None:
    response = client.get("/tasks/303")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task_id"] == 303
    assert payload["queue_backend"] == "in_memory_scaffold"
    assert payload["worker_task_name"] == "post_processing_run_task"
    assert payload["visibility_scope"] == "owned"
    assert payload["request_ready"] is True
    assert payload["dispatch"] == {
        "dispatch_key": "dispatch:303:post_processing_run_task",
        "status": "completed",
        "submission_source": "active_dataset",
        "accepted_at": "2026-03-11 19:05:00",
        "last_updated_at": "2026-03-11 19:18:00",
    }
    assert payload["result_refs"]["trace_batch_id"] == 88
    assert payload["result_refs"]["metadata_records"] == [
        {
            "backend": "sqlite_metadata",
            "record_type": "trace_batch",
            "record_id": "trace_batch:88",
            "version": 1,
            "schema_version": "sqlite_metadata.v1",
        },
        {
            "backend": "sqlite_metadata",
            "record_type": "result_handle",
            "record_id": "result_handle:501",
            "version": 2,
            "schema_version": "sqlite_metadata.v1",
        },
    ]
    assert payload["result_refs"]["trace_payload"] == {
        "contract_version": STORAGE_CONTRACT_VERSION,
        "backend": "local_zarr",
        "payload_role": "task_output",
        "store_key": "datasets/fluxonium-2025-031/trace-batches/88.zarr",
        "store_uri": "trace_store/datasets/fluxonium-2025-031/trace-batches/88.zarr",
        "group_path": "trace_batches/88",
        "array_path": "signals/iq_real",
        "dtype": "float64",
        "shape": [184, 1024],
        "chunk_shape": [16, 1024],
        "schema_version": "1.0",
    }
    assert payload["result_refs"]["result_handles"][0]["handle_id"] == (
        "result:fluxonium-2025-031:fit-summary"
    )
    assert payload["result_refs"]["result_handles"][0]["contract_version"] == (
        STORAGE_CONTRACT_VERSION
    )
    assert payload["result_refs"]["result_handles"][0]["payload_role"] == "report_artifact"
    assert payload["result_refs"]["result_handles"][0]["provenance_task_id"] == 303
    assert payload["result_refs"]["result_handles"][0]["provenance"] == {
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


def test_get_task_returns_not_found_for_missing_task() -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "task_not_found"


def test_get_task_returns_not_found_for_hidden_task() -> None:
    response = client.get("/tasks/304")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "task_not_found"


def test_submit_characterization_task_uses_active_dataset() -> None:
    response = client.post("/tasks", json={"kind": "characterization"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["operation"] == "submitted"
    assert payload["task"]["task_id"] == 306
    assert payload["task"]["dataset_id"] == "fluxonium-2025-031"
    assert payload["task"]["submitted_from_active_dataset"] is True
    assert payload["task"]["workspace_id"] == "ws-device-lab"
    assert payload["task"]["owner_user_id"] == "researcher-01"
    assert payload["task"]["worker_task_name"] == "characterization_run_task"
    assert payload["task"]["execution_mode"] == "run"
    assert payload["task"]["request_ready"] is True
    assert payload["task"]["dispatch"] == {
        "dispatch_key": "dispatch:306:characterization_run_task",
        "status": "accepted",
        "submission_source": "active_dataset",
        "accepted_at": "2026-03-12 10:30:00",
        "last_updated_at": "2026-03-12 10:30:00",
    }
    assert payload["task"]["result_refs"]["trace_payload"] is None
    assert payload["task"]["result_refs"]["result_handles"] == [
        {
            "contract_version": STORAGE_CONTRACT_VERSION,
            "handle_id": "task-result:306:primary",
            "kind": "characterization_report",
            "status": "pending",
            "label": "Pending characterization report",
            "metadata_record": {
                "backend": "sqlite_metadata",
                "record_type": "result_handle",
                "record_id": "result_handle:pending:306",
                "version": 1,
                "schema_version": "sqlite_metadata.v1",
            },
            "payload_backend": None,
            "payload_format": None,
            "payload_role": None,
            "payload_locator": None,
            "provenance_task_id": 306,
            "provenance": {
                "source_dataset_id": "fluxonium-2025-031",
                "source_task_id": 306,
                "trace_batch_record": None,
                "analysis_run_record": None,
            },
        }
    ]


def test_submit_characterization_task_with_explicit_dataset_sets_dispatch_source() -> None:
    response = client.post(
        "/tasks",
        json={"kind": "characterization", "dataset_id": "transmon-coupler-014"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["task"]["dataset_id"] == "transmon-coupler-014"
    assert payload["task"]["submitted_from_active_dataset"] is False
    assert payload["task"]["dispatch"]["submission_source"] == "explicit_dataset"
    assert payload["task"]["dispatch"]["dispatch_key"] == (
        "dispatch:306:characterization_run_task"
    )


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
    assert payload["task"]["task_id"] == 306
    assert payload["task"]["lane"] == "simulation"
    assert payload["task"]["definition_id"] == 18
    assert payload["task"]["summary"] == "Queue one fluxonium simulation preview."
    assert payload["task"]["worker_task_name"] == "simulation_smoke_task"
    assert payload["task"]["execution_mode"] == "smoke"
    assert payload["task"]["request_ready"] is False
    assert payload["task"]["dispatch"] == {
        "dispatch_key": "dispatch:306:simulation_smoke_task",
        "status": "accepted",
        "submission_source": "active_dataset",
        "accepted_at": "2026-03-12 10:30:00",
        "last_updated_at": "2026-03-12 10:30:00",
    }
    assert payload["task"]["result_refs"]["metadata_records"] == [
        {
            "backend": "sqlite_metadata",
            "record_type": "result_handle",
            "record_id": "result_handle:pending:306",
            "version": 1,
            "schema_version": "sqlite_metadata.v1",
        }
    ]
    assert payload["task"]["result_refs"]["result_handles"][0]["kind"] == "simulation_trace"
    assert payload["task"]["result_refs"]["result_handles"][0]["contract_version"] == (
        STORAGE_CONTRACT_VERSION
    )


def test_submitted_task_survives_runtime_reset_in_task_routes() -> None:
    response = client.post("/tasks", json={"kind": "characterization"})

    assert response.status_code == 201
    created_task = response.json()["task"]

    reset_runtime_state()

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert [task["task_id"] for task in list_response.json()][:2] == [306, 301]

    detail_response = client.get("/tasks/306")
    assert detail_response.status_code == 200
    reloaded_task = detail_response.json()
    assert reloaded_task["task_id"] == created_task["task_id"]
    assert reloaded_task["dataset_id"] == created_task["dataset_id"]
    assert reloaded_task["status"] == "queued"
    assert reloaded_task["dispatch"] == created_task["dispatch"]
    assert reloaded_task["result_refs"]["result_handles"] == created_task["result_refs"][
        "result_handles"
    ]


def test_task_lifecycle_service_updates_flow_through_task_routes() -> None:
    updated_task = get_task_service().update_task_lifecycle(
        TaskLifecycleUpdate(
            task_id=302,
            status="failed",
            progress_percent_complete=100,
            progress_summary="Persisted failure summary.",
            progress_updated_at="2026-03-12 11:05:00",
            summary="Persisted task snapshot override",
        )
    )
    assert updated_task.status == "failed"

    reset_runtime_state()

    list_response = client.get("/tasks?status=failed&scope=workspace")
    assert list_response.status_code == 200
    assert list_response.json()[0]["task_id"] == 302

    detail_response = client.get("/tasks/302")
    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["status"] == "failed"
    assert payload["summary"] == "Persisted task snapshot override"
    assert payload["dispatch"]["status"] == "failed"
    assert payload["dispatch"]["last_updated_at"] == "2026-03-12 11:05:00"
    assert payload["progress"]["phase"] == "failed"
    assert payload["progress"]["summary"] == "Persisted failure summary."


def test_submit_simulation_task_requires_definition_id() -> None:
    response = client.post("/tasks", json={"kind": "simulation"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "simulation_definition_required"
    assert response.json()["error"]["category"] == "validation"


def test_submit_post_processing_task_requires_dataset_context() -> None:
    cleared = client.patch("/session/active-dataset", json={"dataset_id": None})
    assert cleared.status_code == 200

    response = client.post("/tasks", json={"kind": "post_processing"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "dataset_context_required"
    assert response.json()["error"]["category"] == "validation"
