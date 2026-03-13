"""Small proof commands that exercise the shared core package."""

import typer
from sc_core import DEFAULT_PREVIEW_ARTIFACTS

from sc_cli.presenters import render_preview_artifacts

app = typer.Typer(help="Shared core package helpers.", no_args_is_help=True)


@app.command("preview-artifacts")
def preview_artifacts() -> None:
    """Show the preview artifacts published by sc_core."""
    typer.echo(render_preview_artifacts(DEFAULT_PREVIEW_ARTIFACTS))
