"""Characterization-lane Huey stack and consumer entrypoint."""

from __future__ import annotations

from core.shared.persistence.startup_reconcile import (
    default_stale_timeout_seconds,
    run_startup_reconcile,
)
from worker.config import create_huey, resolve_huey_broker_path
from worker.runtime import build_consumer_parser, consume_queued_tasks

LANE_NAME = "characterization"
BROKER_PATH = resolve_huey_broker_path(LANE_NAME)
huey = create_huey(LANE_NAME)

from worker import characterization_tasks as _characterization_tasks  # noqa: E402,F401


def consume(
    *,
    max_tasks: int | None = None,
    idle_timeout: float = 5.0,
    poll_interval: float = 0.25,
    reconcile_stale_seconds: int | None = None,
) -> int:
    """Consume queued characterization-lane tasks serially."""
    return consume_queued_tasks(
        huey,
        lane_name=LANE_NAME,
        max_tasks=max_tasks,
        idle_timeout=idle_timeout,
        poll_interval=poll_interval,
        reconcile_stale_after_seconds=reconcile_stale_seconds,
    )


def main() -> None:
    """Run the characterization-lane consumer from the command line."""
    parser = build_consumer_parser(lane_name=LANE_NAME)
    args = parser.parse_args()
    reconcile_stale_seconds = (
        default_stale_timeout_seconds()
        if args.reconcile_stale_seconds is None
        else int(args.reconcile_stale_seconds)
    )
    reconcile_summary = run_startup_reconcile(
        source="worker:characterization",
        stale_after_seconds=reconcile_stale_seconds,
    )
    print(
        "characterization lane startup reconcile "
        f"stale_tasks={reconcile_summary.stale_task_ids} "
        f"failed_batches={reconcile_summary.failed_batch_ids} "
        f"orphan_batches={reconcile_summary.orphan_batch_ids}"
    )
    processed = consume(
        max_tasks=args.max_tasks,
        idle_timeout=args.idle_timeout,
        poll_interval=args.poll_interval,
        reconcile_stale_seconds=None,
    )
    print(f"characterization lane consumed {processed} task(s)")


if __name__ == "__main__":
    from worker.characterization_huey import main as entry_main

    entry_main()
