from typing import cast

from sc_core.execution import (
    EXECUTION_CONTRACT_VERSION,
    TaskResultHandle,
    WorkerExecutionProvenance,
    build_task_failure_payload,
    build_task_start_payload,
    build_task_success_payload,
    build_worker_audit_summary,
)


def test_build_task_success_payload_contains_contract_and_result_refs() -> None:
    payload = build_task_success_payload(
        provenance=WorkerExecutionProvenance(
            lane="simulation",
            worker_task_name="post_processing_run_task",
            worker_pid=4321,
            completed_at="2026-03-12T10:30:00",
        ),
        summary_payload={"source_batch_id": 88},
        result_handle=TaskResultHandle(trace_batch_id=91),
    )
    details = cast(dict[str, object], payload["details"])
    result_refs = cast(dict[str, int], payload["result_refs"])

    assert payload["contract_version"] == EXECUTION_CONTRACT_VERSION
    assert payload["phase"] == "completed"
    assert payload["lane"] == "simulation"
    assert payload["worker_task_name"] == "post_processing_run_task"
    assert result_refs == {"trace_batch_id": 91}
    assert details["source_batch_id"] == 88


def test_build_task_start_and_failure_payloads_preserve_flat_runtime_shape() -> None:
    provenance = WorkerExecutionProvenance(
        lane="characterization",
        worker_task_name="characterization_failure_task",
        worker_pid=9876,
        started_at="2026-03-12T10:00:00",
    )

    start_payload = build_task_start_payload(provenance=provenance)
    failure_payload = build_task_failure_payload(
        provenance=WorkerExecutionProvenance(
            lane=provenance.lane,
            worker_task_name=provenance.worker_task_name,
            worker_pid=provenance.worker_pid,
        ),
        exc_type="RuntimeError",
        message="boom",
    )
    start_details = cast(dict[str, object], start_payload["details"])
    failure_details = cast(dict[str, object], failure_payload["details"])

    assert start_payload["contract_version"] == EXECUTION_CONTRACT_VERSION
    assert start_details["started_at"] == "2026-03-12T10:00:00"
    assert start_payload["stage_label"] == "characterization_failure_task"
    assert failure_payload["error_code"] == "worker_task_failed"
    assert failure_details["message"] == "boom"
    assert failure_details["lane"] == "characterization"


def test_build_worker_audit_summary_matches_runtime_phases() -> None:
    assert (
        build_worker_audit_summary(
            phase="running",
            worker_task_name="simulation_run_task",
            task_id=42,
        )
        == "Worker started simulation_run_task for task 42"
    )
