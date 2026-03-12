"""Simulation-lane operator commands."""

from enum import Enum
from time import monotonic, sleep
from typing import Annotated, cast

import typer
from sc_backend import BackendContractError, TaskDetailResponse, TaskStatus, TaskVisibilityScope

from sc_cli.errors import exit_for_backend_error, exit_with_runtime_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import render_task_detail
from sc_cli.runtime import get_task, list_tasks, submit_task

app = typer.Typer(help="Operate on simulation-lane tasks.", no_args_is_help=True)


class TaskStatusOption(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskScopeOption(str, Enum):
    WORKSPACE = "workspace"
    OWNED = "owned"


TERMINAL_TASK_STATUSES = {"completed", "failed"}


@app.command("submit")
def submit_command(
    definition_id: Annotated[
        int,
        typer.Option("--definition-id", min=1, help="Circuit definition id to simulate."),
    ],
    dataset_id: Annotated[
        str | None,
        typer.Option(
            "--dataset-id",
            help="Dataset id for the simulation task. Falls back to the active session dataset.",
        ),
    ] = None,
    summary: Annotated[
        str | None,
        typer.Option("--summary", help="Optional human summary for the submitted task."),
    ] = None,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Submit a simulation task through the generic rewrite task contract."""
    try:
        task = submit_task(
            kind="simulation",
            dataset_id=dataset_id,
            definition_id=definition_id,
            summary=summary,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_task_detail(task, output=output))


@app.command("show")
def show_command(
    task_id: Annotated[int, typer.Argument(min=1, help="Simulation-lane task id to inspect.")],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show one simulation-lane task."""
    task = _get_simulation_task_or_exit(task_id=task_id, output=output)
    typer.echo(render_task_detail(task, output=output))


@app.command("latest")
def latest_command(
    status: Annotated[
        TaskStatusOption | None,
        typer.Option("--status", help="Filter by task status."),
    ] = None,
    scope: Annotated[
        TaskScopeOption,
        typer.Option("--scope", help="Task visibility scope."),
    ] = TaskScopeOption.WORKSPACE,
    dataset_id: Annotated[
        str | None,
        typer.Option("--dataset-id", help="Filter by dataset id."),
    ] = None,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show the newest task in the simulation lane."""
    try:
        tasks = list_tasks(
            status=None if status is None else cast(TaskStatus, status.value),
            lane="simulation",
            scope=cast(TaskVisibilityScope, scope.value),
            dataset_id=dataset_id,
            limit=20,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    if not tasks:
        exit_with_runtime_error("No simulation-lane tasks matched the requested filters.")
    task = _get_simulation_task_or_exit(task_id=tasks[0].task_id, output=output)
    typer.echo(render_task_detail(task, output=output))


@app.command("wait")
def wait_command(
    task_id: Annotated[int, typer.Argument(min=1, help="Simulation-lane task id to follow.")],
    interval: Annotated[
        float,
        typer.Option("--interval", min=0.1, help="Polling interval in seconds."),
    ] = 1.0,
    timeout: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="Maximum wait time in seconds."),
    ] = 30.0,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Poll one simulation-lane task until it reaches a terminal state or times out."""
    deadline = monotonic() + timeout
    while True:
        task = _get_simulation_task_or_exit(task_id=task_id, output=output)
        if task.status in TERMINAL_TASK_STATUSES:
            typer.echo(render_task_detail(task, output=output))
            return
        if monotonic() >= deadline:
            exit_with_runtime_error(
                f"Timed out waiting for simulation-lane task {task_id} to reach a terminal state."
            )
        sleep(interval)


def _get_simulation_task_or_exit(
    *,
    task_id: int,
    output: OutputMode,
) -> TaskDetailResponse:
    try:
        task = get_task(task_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    if task.lane != "simulation":
        exit_with_runtime_error(f"Task {task_id} is not part of the simulation lane.")
    return task
