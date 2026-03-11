"""Commands for inspecting rewrite session state."""

import typer

from sc_cli.presenters import render_session
from sc_cli.runtime import get_session

app = typer.Typer(help="Rewrite session helpers.", no_args_is_help=True)


@app.command("show")
def show_command() -> None:
    """Show the current rewrite session and workspace context."""
    typer.echo(render_session(get_session()))
