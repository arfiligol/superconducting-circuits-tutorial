"""Simulation-lane Huey stack and consumer entrypoint."""

from __future__ import annotations

from worker.config import create_huey, resolve_huey_broker_path
from worker.runtime import build_consumer_parser, consume_queued_tasks

LANE_NAME = "simulation"
BROKER_PATH = resolve_huey_broker_path(LANE_NAME)
huey = create_huey(LANE_NAME)

from worker import simulation_tasks as _simulation_tasks  # noqa: E402,F401


def consume(
    *,
    max_tasks: int | None = None,
    idle_timeout: float = 5.0,
    poll_interval: float = 0.25,
    reconcile_stale_seconds: int | None = None,
) -> int:
    """Consume queued simulation-lane tasks serially."""
    return consume_queued_tasks(
        huey,
        lane_name=LANE_NAME,
        max_tasks=max_tasks,
        idle_timeout=idle_timeout,
        poll_interval=poll_interval,
        reconcile_stale_after_seconds=reconcile_stale_seconds,
    )


def main() -> None:
    """Run the simulation-lane consumer from the command line."""
    parser = build_consumer_parser(lane_name=LANE_NAME)
    args = parser.parse_args()
    processed = consume(
        max_tasks=args.max_tasks,
        idle_timeout=args.idle_timeout,
        poll_interval=args.poll_interval,
        reconcile_stale_seconds=args.reconcile_stale_seconds,
    )
    print(f"simulation lane consumed {processed} task(s)")


if __name__ == "__main__":
    from worker.simulation_huey import main as entry_main

    entry_main()
