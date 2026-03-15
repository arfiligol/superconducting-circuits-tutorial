from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sc_core.execution import (
    build_task_control_audit_payload,
    build_task_control_event_log,
    build_task_control_history_event,
)
from sc_core.tasking import (
    REDACTED_RUNTIME_METADATA_VALUE,
    TERMINAL_TASK_STATES,
    allowed_task_runtime_transitions,
    build_lane_processor_summaries,
    build_processor_heartbeat,
    build_task_retry_lineage,
    build_task_state_matrix,
    can_transition_task_state,
    evaluate_task_control_action,
    is_terminal_task_state,
    resolve_worker_task_route,
    summarize_lane_processors,
)


def _utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def test_task_state_matrix_keeps_terminal_states_immutable() -> None:
    matrix = build_task_state_matrix()

    assert matrix["queued"] == ("cancelled", "dispatching")
    assert "termination_requested" in matrix["running"]
    assert allowed_task_runtime_transitions("completed") == ()
    assert is_terminal_task_state("completed") is True
    assert is_terminal_task_state("running") is False
    assert TERMINAL_TASK_STATES == {"completed", "failed", "cancelled", "terminated"}
    assert can_transition_task_state("running", "termination_requested") is True
    assert can_transition_task_state("completed", "failed") is False
    assert can_transition_task_state("terminated", "terminated") is True


def test_control_semantics_keep_cancel_terminate_and_retry_distinct() -> None:
    cancel_running = evaluate_task_control_action("cancel", current_state="running")
    assert cancel_running.accepted is True
    assert cancel_running.requested_state == "cancellation_requested"
    assert cancel_running.creates_new_task_lineage is False

    terminate_cancel_pending = evaluate_task_control_action(
        "terminate",
        current_state="cancellation_requested",
    )
    assert terminate_cancel_pending.accepted is True
    assert terminate_cancel_pending.requested_state == "termination_requested"

    reject_cancel_terminal = evaluate_task_control_action("cancel", current_state="completed")
    assert reject_cancel_terminal.accepted is False
    assert reject_cancel_terminal.rejection_reason == "task_already_terminal"
    assert reject_cancel_terminal.terminal_state_immutable is True

    retry_failed = evaluate_task_control_action("retry", current_state="failed")
    assert retry_failed.accepted is True
    assert retry_failed.creates_new_task_lineage is True
    assert retry_failed.requested_state is None

    lineage = build_task_retry_lineage(
        source_task_id=41,
        source_task_state="failed",
        root_task_id=7,
        prior_retry_attempt=2,
    )
    assert lineage.root_task_id == 7
    assert lineage.parent_task_id == 41
    assert lineage.retry_attempt == 3
    assert lineage.source_terminal_state == "failed"


def test_post_processing_lane_and_processor_summary_are_lane_scoped() -> None:
    route = resolve_worker_task_route(
        task_kind="post_processing",
        request_is_valid=True,
        has_trace_batch_id=True,
    )
    assert route.lane == "post_processing"

    now = _utc(2026, 3, 15, 12, 0)
    heartbeats = [
        build_processor_heartbeat(
            processor_id="sim-1",
            lane="simulation",
            state="healthy",
            last_heartbeat_at=now - timedelta(seconds=10),
            runtime_metadata={"version": "1.2.0", "host": {"name": "secret-host"}},
        ),
        build_processor_heartbeat(
            processor_id="sim-2",
            lane="simulation",
            state="busy",
            current_task_id=88,
            last_heartbeat_at=now - timedelta(seconds=15),
            runtime_metadata={"capacity": 2},
        ),
        build_processor_heartbeat(
            processor_id="char-1",
            lane="characterization",
            state="healthy",
            last_heartbeat_at=now - timedelta(seconds=180),
            runtime_metadata={"build": "abc123"},
        ),
        build_processor_heartbeat(
            processor_id="post-1",
            lane="post_processing",
            state="degraded",
            last_heartbeat_at=now - timedelta(seconds=5),
            runtime_metadata={"warnings": ["slow-io"], "env": b"token"},
        ),
    ]

    simulation_summary = summarize_lane_processors(
        heartbeats,
        lane="simulation",
        recorded_at=now,
        offline_after_seconds=90,
    )
    assert simulation_summary.healthy_processors == 1
    assert simulation_summary.busy_processors == 1
    assert simulation_summary.offline_processors == 0

    characterization_summary = summarize_lane_processors(
        heartbeats,
        lane="characterization",
        recorded_at=now,
        offline_after_seconds=90,
    )
    assert characterization_summary.offline_processors == 1
    assert characterization_summary.healthy_processors == 0

    summaries = build_lane_processor_summaries(
        heartbeats,
        recorded_at=now,
        offline_after_seconds=90,
    )
    assert [summary.lane for summary in summaries] == [
        "characterization",
        "post_processing",
        "simulation",
    ]

    post_payload = heartbeats[-1].to_payload(recorded_at=now, offline_after_seconds=90)
    assert post_payload["runtime_metadata"] == {
        "warnings": ["slow-io"],
        "env": REDACTED_RUNTIME_METADATA_VALUE,
    }


def test_task_control_audit_and_history_payloads_are_redaction_safe() -> None:
    recorded_at = _utc(2026, 3, 15, 12, 30)
    decision = evaluate_task_control_action("retry", current_state="terminated")
    lineage = build_task_retry_lineage(
        source_task_id=91,
        source_task_state="terminated",
        prior_retry_attempt=0,
    )

    audit_payload = build_task_control_audit_payload(
        decision=decision,
        recorded_at=recorded_at,
        lineage=lineage,
        runtime_metadata={
            "processor_version": "2026.03",
            "host": {"name": "hidden"},
            "labels": ["safe", "ops"],
        },
    )
    assert audit_payload["outcome"] == "accepted"
    assert audit_payload["runtime_metadata"] == {
        "processor_version": "2026.03",
        "host": REDACTED_RUNTIME_METADATA_VALUE,
        "labels": ["safe", "ops"],
    }
    assert audit_payload["retry_lineage"] == {
        "source_task_id": 91,
        "root_task_id": 91,
        "parent_task_id": 91,
        "retry_attempt": 1,
        "source_terminal_state": "terminated",
    }

    event_log = build_task_control_event_log(
        task_id=91,
        decision=decision,
        recorded_at=recorded_at,
        lineage=lineage,
        runtime_metadata={"host": {"name": "hidden"}},
    )
    assert event_log.action_kind == "task.retried"
    assert event_log.resource_kind == "task"
    assert event_log.payload["runtime_metadata"] == {
        "host": REDACTED_RUNTIME_METADATA_VALUE,
    }

    history_event = build_task_control_history_event(
        decision=decision,
        occurred_at=recorded_at,
        lineage=lineage,
    )
    assert history_event.event_type == "task_retried"
    assert history_event.level == "info"
    assert history_event.metadata["creates_new_task_lineage"] is True
