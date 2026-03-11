"""Commands for inspecting rewrite session state."""

import typer
from sc_backend import BackendContractError

from sc_cli.errors import exit_for_backend_error
from sc_cli.presenters import render_session
from sc_cli.runtime import get_session

app = typer.Typer(help="Rewrite session helpers.", no_args_is_help=True)


@app.command("show")
def show_command() -> None:
    """Show the current rewrite session and workspace context."""
    try:
        session = get_session()
    except BackendContractError as error:
        exit_for_backend_error(error)
    typer.echo(render_session(session))
