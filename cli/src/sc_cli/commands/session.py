"""Commands for inspecting rewrite session state."""

from typing import Annotated

import typer
from sc_backend import BackendContractError

from sc_cli.errors import exit_for_backend_error, exit_with_usage_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import render_session
from sc_cli.runtime import get_session, set_active_dataset

app = typer.Typer(help="Rewrite session helpers.", no_args_is_help=True)


@app.command("show")
def show_command(output: OutputOption = OutputMode.TEXT) -> None:
    """Show the current rewrite session and workspace context."""
    try:
        session = get_session()
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_session(session, output=output))


@app.command("set-active-dataset")
def set_active_dataset_command(
    dataset_id: Annotated[
        str | None,
        typer.Argument(help="Dataset id to activate in the current session context."),
    ] = None,
    clear: Annotated[
        bool,
        typer.Option(
            "--clear",
            help="Clear the active dataset from the current session context.",
        ),
    ] = False,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Update the active dataset in the current rewrite session context."""
    if clear == (dataset_id is not None):
        exit_with_usage_error("Provide exactly one of DATASET_ID or --clear.")

    try:
        session = set_active_dataset(None if clear else dataset_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_session(session, output=output))
