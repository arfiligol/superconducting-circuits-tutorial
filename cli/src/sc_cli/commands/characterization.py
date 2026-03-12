"""Characterization-lane operator commands."""

from enum import Enum
from time import monotonic, sleep
from typing import Annotated, cast

import typer
from sc_backend import BackendContractError, TaskDetailResponse, TaskStatus, TaskVisibilityScope

from sc_cli.errors import exit_for_backend_error, exit_with_runtime_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import render_task_detail
from sc_cli.runtime import get_task, list_tasks, submit_task

app = typer.Typer(help="Operate on characterization-lane tasks.", no_args_is_help=True)


class TaskStatusOption(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskScopeOption(str, Enum):
    WORKSPACE = "workspace"
    OWNED = "owned"


class WaitStatusOption(str, Enum):
    TERMINAL = "terminal"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


TERMINAL_TASK_STATUSES = {"completed", "failed"}


@app.command("submit")
def submit_command(
    dataset_id: Annotated[
        str | None,
        typer.Option(
            "--dataset-id",
            help=(
                "Dataset id for the characterization task. "
                "Falls back to the active session dataset."
            ),
        ),
    ] = None,
    summary: Annotated[
        str | None,
        typer.Option("--summary", help="Optional human summary for the submitted task."),
    ] = None,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Submit a characterization task through the generic rewrite task contract."""
    try:
        task = submit_task(
            kind="characterization",
            dataset_id=dataset_id,
            definition_id=None,
            summary=summary,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_task_detail(task, output=output))


@app.command("show")
def show_command(
    task_id: Annotated[
        int,
        typer.Argument(min=1, help="Characterization-lane task id to inspect."),
    ],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show one characterization-lane task."""
    task = _get_characterization_task_or_exit(task_id=task_id, output=output)
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
    """Show the newest task in the characterization lane."""
    try:
        tasks = list_tasks(
            status=None if status is None else cast(TaskStatus, status.value),
            lane="characterization",
            scope=cast(TaskVisibilityScope, scope.value),
            dataset_id=dataset_id,
            limit=20,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    if not tasks:
        exit_with_runtime_error("No characterization-lane tasks matched the requested filters.")
    task = _get_characterization_task_or_exit(task_id=tasks[0].task_id, output=output)
    typer.echo(render_task_detail(task, output=output))


@app.command("wait")
def wait_command(
    task_id: Annotated[
        int,
        typer.Argument(min=1, help="Characterization-lane task id to follow."),
    ],
    until_status: Annotated[
        WaitStatusOption,
        typer.Option(
            "--until-status",
            help="Task status to wait for. Use terminal to wait for completed/failed.",
        ),
    ] = WaitStatusOption.TERMINAL,
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
    """Poll one characterization-lane task until it reaches the requested status."""
    deadline = monotonic() + timeout
    while True:
        task = _get_characterization_task_or_exit(task_id=task_id, output=output)
        if _has_reached_wait_target(task=task, until_status=until_status):
            typer.echo(render_task_detail(task, output=output))
            return
        if monotonic() >= deadline:
            exit_with_runtime_error(
                "Timed out waiting for characterization-lane task "
                f"{task_id} to reach {until_status.value}."
            )
        sleep(interval)


def _get_characterization_task_or_exit(
    *,
    task_id: int,
    output: OutputMode,
) -> TaskDetailResponse:
    try:
        task = get_task(task_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    if task.lane != "characterization":
        exit_with_runtime_error(f"Task {task_id} is not part of the characterization lane.")
    return task


def _has_reached_wait_target(
    *,
    task: TaskDetailResponse,
    until_status: WaitStatusOption,
) -> bool:
    if until_status is WaitStatusOption.TERMINAL:
        return task.status in TERMINAL_TASK_STATUSES
    return task.status == until_status.value
