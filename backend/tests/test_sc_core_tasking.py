import pytest
from sc_core.tasking import (
    LaneName,
    TaskSubmissionKind,
    WorkerTaskName,
    extract_parameters_payload,
    resolve_worker_task_route,
)


def test_extract_parameters_payload_returns_mapping_copy() -> None:
    payload = {
        "parameters": {
            "dataset_id": "fluxonium-2025-031",
            "retry": 2,
        },
        "ignored": "value",
    }

    extracted = extract_parameters_payload(payload)

    assert extracted == {
        "dataset_id": "fluxonium-2025-031",
        "retry": 2,
    }
    assert extracted is not payload["parameters"]


@pytest.mark.parametrize(
    ("task_kind", "request_is_valid", "has_trace_batch_id", "expected_lane", "expected_name"),
    [
        ("simulation", True, True, "simulation", "simulation_run_task"),
        ("simulation", True, False, "simulation", "simulation_smoke_task"),
        ("post_processing", True, True, "simulation", "post_processing_run_task"),
        ("post_processing", False, True, "simulation", "post_processing_smoke_task"),
        ("characterization", True, False, "characterization", "characterization_run_task"),
        ("characterization", False, False, "characterization", "characterization_smoke_task"),
    ],
)
def test_resolve_worker_task_route_matches_worker_lane_contract(
    task_kind: TaskSubmissionKind,
    request_is_valid: bool,
    has_trace_batch_id: bool,
    expected_lane: LaneName,
    expected_name: WorkerTaskName,
) -> None:
    route = resolve_worker_task_route(
        task_kind=task_kind,
        request_is_valid=request_is_valid,
        has_trace_batch_id=has_trace_batch_id,
    )

    assert route.lane == expected_lane
    assert route.worker_task_name == expected_name
    assert route.execution_mode == ("run" if expected_name.endswith("_run_task") else "smoke")


def test_resolve_worker_task_route_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="Unsupported task kind"):
        resolve_worker_task_route(
            task_kind="unsupported",  # type: ignore[arg-type] - intentional invalid contract probe
            request_is_valid=True,
            has_trace_batch_id=True,
        )
