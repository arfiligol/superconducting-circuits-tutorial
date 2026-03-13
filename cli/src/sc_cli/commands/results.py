"""Persisted task result reference inspection commands."""

from typing import Annotated

import typer
from sc_backend import TaskDetailResponse

from sc_cli.errors import exit_with_runtime_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import (
    render_task_result_handles,
    render_task_result_refs,
    render_task_trace_payload,
)
from sc_cli.runtime import get_task
from sc_cli.task_operator import get_task_or_exit

app = typer.Typer(help="Inspect persisted task result references.", no_args_is_help=True)


@app.command("show")
def show_command(
    task_id: Annotated[int, typer.Argument(min=1, help="Task id whose result refs to inspect.")],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show persisted result-reference state for one task."""
    task = _get_task_or_exit(task_id=task_id, output=output)
    typer.echo(render_task_result_refs(task, output=output))


@app.command("trace")
def trace_command(
    task_id: Annotated[int, typer.Argument(min=1, help="Task id whose trace payload to inspect.")],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show the persisted trace payload reference for one task."""
    task = _get_task_or_exit(task_id=task_id, output=output)
    if task.result_refs.trace_payload is None:
        exit_with_runtime_error(f"Task {task_id} does not expose a persisted trace payload.")
    typer.echo(render_task_trace_payload(task, output=output))


@app.command("handles")
def handles_command(
    task_id: Annotated[int, typer.Argument(min=1, help="Task id whose result handles to inspect.")],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show persisted result handles for one task."""
    task = _get_task_or_exit(task_id=task_id, output=output)
    if not task.result_refs.result_handles:
        exit_with_runtime_error(f"Task {task_id} does not expose persisted result handles.")
    typer.echo(render_task_result_handles(task, output=output))


def _get_task_or_exit(
    *,
    task_id: int,
    output: OutputMode,
) -> TaskDetailResponse:
    return get_task_or_exit(task_id=task_id, output=output, get_task_fn=get_task)
