"""WS9 persisted task CLI commands under `sc sim ...`."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Annotated, Any

import typer

from app.services.auth_service import (
    bootstrap_admin_credentials,
    ensure_bootstrap_admin,
    get_active_user_by_username,
)
from app.services.execution_context import ActorContext, UseCaseContext
from app.services.latest_result_lookup import require_task
from app.services.post_processing_task_contract import build_post_processing_submission
from app.services.simulation_submission import build_simulation_submission
from app.services.task_submission import create_api_task, require_design
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord, TaskRecord
from core.simulation.domain.circuit import (
    CircuitDefinition,
    FrequencyRange,
    SimulationConfig,
    parse_circuit_definition_source,
)


@dataclass(frozen=True)
class ResolvedCliActor:
    """Resolved local actor used for CLI task submission."""

    username: str
    actor: ActorContext


def _stable_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=True)


def _hash_schema_source(source: Any) -> str:
    normalized = source if isinstance(source, str) else _stable_json(source)
    return f"sha256:{sha256(normalized.encode('utf-8')).hexdigest()}"


def _hash_stable_json(payload: dict[str, Any]) -> str:
    return f"sha256:{sha256(_stable_json(payload).encode('utf-8')).hexdigest()}"


def _echo_progress(message: str) -> None:
    typer.echo(message, err=True)


def _emit_summary(summary: dict[str, Any]) -> None:
    typer.echo(_stable_json(summary))


def _resolve_cli_actor(username: str | None) -> ResolvedCliActor:
    normalized_username = str(username or "").strip()
    if not normalized_username:
        raise typer.BadParameter(
            "Pass --username or set SC_CLI_USERNAME so CLI tasks have a real actor."
        )

    bootstrap_username, _bootstrap_password = bootstrap_admin_credentials()
    if normalized_username == bootstrap_username:
        user = ensure_bootstrap_admin()
    else:
        user = get_active_user_by_username(normalized_username)
        if user is None:
            raise typer.BadParameter(
                f"Active local user '{normalized_username}' was not found.",
            )

    if user.id is None:
        raise typer.BadParameter(f"Local user '{normalized_username}' is missing an ID.")

    return ResolvedCliActor(
        username=user.username,
        actor=ActorContext(
            actor_id=int(user.id),
            requested_by="cli",
            role=user.role,
            auth_source="cli_local",
            metadata={"username": user.username},
        ),
    )


def _load_circuit_definition(circuit_id: int) -> tuple[CircuitRecord, CircuitDefinition]:
    with get_unit_of_work() as uow:
        record = uow.circuits.get(int(circuit_id))
    if record is None:
        raise typer.BadParameter(f"Circuit ID {circuit_id} was not found.")
    try:
        definition = parse_circuit_definition_source(record.definition_json)
    except Exception as exc:  # pragma: no cover - defensive validation path
        raise typer.BadParameter(
            f"Circuit ID {circuit_id} contains an invalid definition.",
        ) from exc
    return record, definition


def _task_progress_signature(task: TaskRecord) -> str:
    progress_payload = dict(task.progress_payload)
    error_payload = dict(task.error_payload)
    return "|".join(
        (
            str(task.status),
            str(progress_payload.get("recorded_at", "")),
            str(progress_payload.get("summary", "")),
            str(progress_payload.get("warning", "")),
            str(error_payload.get("summary", "")),
            task.completed_at.isoformat() if task.completed_at is not None else "",
        )
    )


def _render_task_progress(task: TaskRecord) -> str:
    status = str(task.status)
    if status == "completed":
        payload = dict(task.result_summary_payload)
    elif status == "failed":
        payload = dict(task.error_payload)
    else:
        payload = dict(task.progress_payload)

    phase = str(payload.get("phase", status)).strip() or status
    summary = str(payload.get("summary", "")).strip()
    warning = str(payload.get("warning", "")).strip()
    details = payload.get("details")
    detail_suffix = ""
    if isinstance(details, dict) and details.get("analysis_run_id") is not None:
        detail_suffix = f" analysis_run_id={details['analysis_run_id']}"
    elif task.trace_batch_id is not None:
        detail_suffix = f" trace_batch_id={task.trace_batch_id}"
    base = f"[task {int(task.id or 0)}] {phase}: {summary or status}"
    if warning:
        base = f"{base} warning={warning}"
    if detail_suffix:
        base = f"{base}{detail_suffix}"
    return base


def _wait_for_task(
    *,
    task_id: int,
    poll_interval: float,
    timeout_seconds: float | None,
) -> TaskRecord:
    started_at = time.monotonic()
    last_signature: str | None = None
    while True:
        task = require_task(task_id)
        signature = _task_progress_signature(task)
        if signature != last_signature:
            last_signature = signature
            _echo_progress(_render_task_progress(task))
        if str(task.status) in {"completed", "failed"}:
            return task
        if timeout_seconds is not None and (time.monotonic() - started_at) >= timeout_seconds:
            raise TimeoutError(f"Timed out while waiting for task {task_id}.")
        time.sleep(max(0.05, poll_interval))


def _task_summary(
    *,
    task: TaskRecord,
    actor_username: str,
    dispatched_lane: str,
    worker_task_name: str,
    dedupe_hit: bool,
    waited: bool,
    source_batch_id: int | None = None,
    timed_out: bool = False,
) -> dict[str, Any]:
    error_payload = dict(task.error_payload)
    error_details = error_payload.get("details")
    error_message = None
    if isinstance(error_details, dict):
        error_message = error_details.get("message")
    return {
        "actor_username": actor_username,
        "dedupe_hit": dedupe_hit,
        "design_id": int(task.design_id),
        "dispatched_lane": dispatched_lane,
        "error_code": error_payload.get("error_code"),
        "error_message": error_message,
        "error_summary": error_payload.get("summary"),
        "force_rerun": bool(task.dedupe_key is None and not dedupe_hit),
        "source_batch_id": source_batch_id,
        "status": "timeout" if timed_out else str(task.status),
        "task_id": int(task.id or 0),
        "trace_batch_id": task.trace_batch_id,
        "waited": waited,
        "worker_task_name": worker_task_name,
    }


def run(
    design_id: Annotated[int, typer.Option("--design-id", help="Design ID for the task.")],
    circuit_id: Annotated[
        int | None,
        typer.Option(
            "--circuit-id",
            help="Circuit ID to load. Defaults to the design ID for current local workflows.",
        ),
    ] = None,
    username: Annotated[
        str | None,
        typer.Option(
            "--username",
            envvar="SC_CLI_USERNAME",
            help="Local username for actor context.",
        ),
    ] = None,
    start_ghz: Annotated[float, typer.Option("--start-ghz", help="Start frequency in GHz.")] = 4.0,
    stop_ghz: Annotated[float, typer.Option("--stop-ghz", help="Stop frequency in GHz.")] = 8.0,
    points: Annotated[int, typer.Option("--points", help="Frequency point count.")] = 401,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait/--detach",
            help="Wait for task completion (default) or return immediately after enqueue.",
        ),
    ] = True,
    force_rerun: Annotated[
        bool,
        typer.Option("--force-rerun", help="Bypass soft dedupe and enqueue a fresh task."),
    ] = False,
    poll_interval: Annotated[
        float,
        typer.Option("--poll-interval", help="Polling interval in seconds for --wait."),
    ] = 0.5,
    timeout_seconds: Annotated[
        float | None,
        typer.Option("--timeout-seconds", help="Optional wait timeout in seconds."),
    ] = None,
) -> None:
    """Create a persisted simulation task and optionally wait for completion."""
    resolved_actor = _resolve_cli_actor(username)
    design = require_design(int(design_id))
    resolved_circuit_id = int(circuit_id) if circuit_id is not None else int(design_id)
    circuit_record, circuit_definition = _load_circuit_definition(resolved_circuit_id)
    freq_range = FrequencyRange(
        start_ghz=float(start_ghz),
        stop_ghz=float(stop_ghz),
        points=int(points),
    )
    config = SimulationConfig()
    config_snapshot = {
        "setup_kind": "circuit_simulation.raw",
        "setup_version": "1.0",
        "freq_range": freq_range.model_dump(mode="json"),
        "config": config.model_dump(mode="json"),
    }
    context = UseCaseContext(
        actor=resolved_actor.actor,
        source="cli",
        force_rerun=bool(force_rerun),
        metadata={"flow": "simulation", "design_id": int(design_id)},
    )
    submission = build_simulation_submission(
        design_id=int(design_id),
        design_name=str(design.name),
        circuit=circuit_definition,
        freq_range=freq_range,
        config=config,
        config_snapshot=config_snapshot,
        source_meta={"origin": "cli", "submitted_via": "sc sim run", "storage": "trace_store"},
        schema_source_hash=_hash_schema_source(circuit_record.definition_json),
        simulation_setup_hash=_hash_stable_json(config_snapshot),
        sweep_setup_payload=None,
        sweep_setup_hash=None,
        context=context,
        force_rerun=bool(force_rerun),
    )
    submitted = create_api_task(
        task_kind="simulation",
        design_id=int(design_id),
        request_payload=submission.api_request.model_dump(mode="json", exclude={"force_rerun"}),
        actor=resolved_actor.actor,
        force_rerun=bool(force_rerun),
        source="cli",
    )
    _echo_progress(
        f"[task {int(submitted.task.id or 0)}] queued in lane={submitted.dispatch.lane} "
        f"worker={submitted.dispatch.worker_task_name} actor={resolved_actor.username}"
    )

    if not wait:
        _emit_summary(
            _task_summary(
                task=submitted.task,
                actor_username=resolved_actor.username,
                dispatched_lane=submitted.dispatch.lane,
                worker_task_name=submitted.dispatch.worker_task_name,
                dedupe_hit=submitted.dedupe_hit,
                waited=False,
            )
        )
        raise typer.Exit(code=0)

    try:
        task = _wait_for_task(
            task_id=int(submitted.task.id or 0),
            poll_interval=float(poll_interval),
            timeout_seconds=timeout_seconds,
        )
    except TimeoutError as exc:
        timed_out_task = require_task(int(submitted.task.id or 0))
        _echo_progress(str(exc))
        _emit_summary(
            _task_summary(
                task=timed_out_task,
                actor_username=resolved_actor.username,
                dispatched_lane=submitted.dispatch.lane,
                worker_task_name=submitted.dispatch.worker_task_name,
                dedupe_hit=submitted.dedupe_hit,
                waited=True,
                timed_out=True,
            )
        )
        raise typer.Exit(code=2) from exc

    summary = _task_summary(
        task=task,
        actor_username=resolved_actor.username,
        dispatched_lane=submitted.dispatch.lane,
        worker_task_name=submitted.dispatch.worker_task_name,
        dedupe_hit=submitted.dedupe_hit,
        waited=True,
    )
    _echo_progress(_render_task_progress(task))
    _emit_summary(summary)
    raise typer.Exit(code=0 if str(task.status) == "completed" else 1)


def post_process(
    design_id: Annotated[int, typer.Option("--design-id", help="Design ID for the task.")],
    source_batch_id: Annotated[
        int,
        typer.Option("--source-batch-id", help="Persisted raw simulation batch to rerun from."),
    ],
    username: Annotated[
        str | None,
        typer.Option(
            "--username",
            envvar="SC_CLI_USERNAME",
            help="Local username for actor context.",
        ),
    ] = None,
    circuit_id: Annotated[
        int | None,
        typer.Option("--circuit-id", help="Optional circuit ID for post-processing helpers."),
    ] = None,
    input_source: Annotated[
        str,
        typer.Option("--input-source", help="Post-processing input family."),
    ] = "raw_y",
    mode_filter: Annotated[str, typer.Option("--mode-filter", help="Trace mode filter.")] = "base",
    mode_token: Annotated[str, typer.Option("--mode-token", help="Mode token to process.")] = "0",
    reference_impedance_ohm: Annotated[
        float,
        typer.Option("--reference-impedance-ohm", help="Reference impedance in ohms."),
    ] = 50.0,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait/--detach",
            help="Wait for task completion (default) or return immediately after enqueue.",
        ),
    ] = True,
    force_rerun: Annotated[
        bool,
        typer.Option("--force-rerun", help="Bypass soft dedupe and enqueue a fresh task."),
    ] = False,
    poll_interval: Annotated[
        float,
        typer.Option("--poll-interval", help="Polling interval in seconds for --wait."),
    ] = 0.5,
    timeout_seconds: Annotated[
        float | None,
        typer.Option("--timeout-seconds", help="Optional wait timeout in seconds."),
    ] = None,
) -> None:
    """Rerun post-processing from a persisted raw simulation batch."""
    resolved_actor = _resolve_cli_actor(username)
    require_design(int(design_id))
    circuit_definition: CircuitDefinition | None = None
    if circuit_id is not None:
        _circuit_record, circuit_definition = _load_circuit_definition(int(circuit_id))
    context = UseCaseContext(
        actor=resolved_actor.actor,
        source="cli",
        force_rerun=bool(force_rerun),
        metadata={"flow": "post_processing", "design_id": int(design_id)},
    )
    submission = build_post_processing_submission(
        design_id=int(design_id),
        source_batch_id=int(source_batch_id),
        input_source=str(input_source),
        mode_filter=str(mode_filter),
        mode_token=str(mode_token),
        reference_impedance_ohm=float(reference_impedance_ohm),
        step_sequence=[],
        termination_plan_payload=None,
        circuit_definition=circuit_definition,
        context=context,
        force_rerun=bool(force_rerun),
    )
    submitted = create_api_task(
        task_kind="post_processing",
        design_id=int(design_id),
        request_payload=submission.api_request.model_dump(mode="json", exclude={"force_rerun"}),
        actor=resolved_actor.actor,
        force_rerun=bool(force_rerun),
        source="cli",
    )
    _echo_progress(
        f"[task {int(submitted.task.id or 0)}] queued in lane={submitted.dispatch.lane} "
        f"worker={submitted.dispatch.worker_task_name} actor={resolved_actor.username} "
        f"source_batch_id={int(source_batch_id)}"
    )

    if not wait:
        _emit_summary(
            _task_summary(
                task=submitted.task,
                actor_username=resolved_actor.username,
                dispatched_lane=submitted.dispatch.lane,
                worker_task_name=submitted.dispatch.worker_task_name,
                dedupe_hit=submitted.dedupe_hit,
                waited=False,
                source_batch_id=int(source_batch_id),
            )
        )
        raise typer.Exit(code=0)

    try:
        task = _wait_for_task(
            task_id=int(submitted.task.id or 0),
            poll_interval=float(poll_interval),
            timeout_seconds=timeout_seconds,
        )
    except TimeoutError as exc:
        timed_out_task = require_task(int(submitted.task.id or 0))
        _echo_progress(str(exc))
        _emit_summary(
            _task_summary(
                task=timed_out_task,
                actor_username=resolved_actor.username,
                dispatched_lane=submitted.dispatch.lane,
                worker_task_name=submitted.dispatch.worker_task_name,
                dedupe_hit=submitted.dedupe_hit,
                waited=True,
                source_batch_id=int(source_batch_id),
                timed_out=True,
            )
        )
        raise typer.Exit(code=2) from exc

    summary = _task_summary(
        task=task,
        actor_username=resolved_actor.username,
        dispatched_lane=submitted.dispatch.lane,
        worker_task_name=submitted.dispatch.worker_task_name,
        dedupe_hit=submitted.dedupe_hit,
        waited=True,
        source_batch_id=int(source_batch_id),
    )
    _echo_progress(_render_task_progress(task))
    _emit_summary(summary)
    raise typer.Exit(code=0 if str(task.status) == "completed" else 1)
