"""Commands for inspecting rewrite task state."""

from enum import Enum
from typing import Annotated, cast

import typer
from sc_backend import (
    BackendContractError,
    TaskKind,
    TaskLane,
    TaskStatus,
    TaskVisibilityScope,
)

from sc_cli.errors import exit_for_backend_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import render_task_detail, render_task_summaries
from sc_cli.runtime import get_task, list_tasks, submit_task

app = typer.Typer(help="Rewrite task helpers.", no_args_is_help=True)


class TaskStatusOption(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskLaneOption(str, Enum):
    SIMULATION = "simulation"
    CHARACTERIZATION = "characterization"


class TaskKindOption(str, Enum):
    SIMULATION = "simulation"
    POST_PROCESSING = "post_processing"
    CHARACTERIZATION = "characterization"


class TaskScopeOption(str, Enum):
    WORKSPACE = "workspace"
    OWNED = "owned"


@app.command("list")
def list_command(
    status: Annotated[
        TaskStatusOption | None,
        typer.Option("--status", help="Filter by task status."),
    ] = None,
    lane: Annotated[
        TaskLaneOption | None,
        typer.Option("--lane", help="Filter by task lane."),
    ] = None,
    scope: Annotated[
        TaskScopeOption,
        typer.Option("--scope", help="Task visibility scope."),
    ] = TaskScopeOption.WORKSPACE,
    dataset_id: Annotated[
        str | None,
        typer.Option("--dataset-id", help="Filter by dataset id."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", min=1, max=50, help="Maximum number of tasks to show."),
    ] = 20,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """List tasks from the rewrite integration scaffold."""
    try:
        tasks = list_tasks(
            status=None if status is None else cast(TaskStatus, status.value),
            lane=None if lane is None else cast(TaskLane, lane.value),
            scope=cast(TaskVisibilityScope, scope.value),
            dataset_id=dataset_id,
            limit=limit,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_task_summaries(tasks, output=output))


@app.command("show")
def show_command(
    task_id: Annotated[int, typer.Argument(min=1, help="Task id to inspect.")],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show one task from the rewrite integration scaffold."""
    try:
        task = get_task(task_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_task_detail(task, output=output))


@app.command("submit")
def submit_command(
    kind: Annotated[
        TaskKindOption,
        typer.Argument(help="Task kind to submit."),
    ],
    dataset_id: Annotated[
        str | None,
        typer.Option(
            "--dataset-id",
            help="Dataset id for dataset-driven tasks. Falls back to the active session dataset.",
        ),
    ] = None,
    definition_id: Annotated[
        int | None,
        typer.Option(
            "--definition-id",
            min=1,
            help="Circuit definition id required by simulation tasks.",
        ),
    ] = None,
    summary: Annotated[
        str | None,
        typer.Option("--summary", help="Optional human summary for the submitted task."),
    ] = None,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Submit one task through the rewrite task scaffold."""
    try:
        task = submit_task(
            kind=cast(TaskKind, kind.value),
            dataset_id=dataset_id,
            definition_id=definition_id,
            summary=summary,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_task_detail(task, output=output))
