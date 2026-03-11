"""Thin adapters for canonical circuit-definition workflows."""

from pathlib import Path
from typing import Annotated

import typer
from sc_core import inspect_circuit_definition_source

from sc_cli.presenters import render_circuit_definition_inspection

app = typer.Typer(help="Canonical circuit-definition helpers.", no_args_is_help=True)


@app.command("inspect")
def inspect_command(
    source_file: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to a circuit-definition draft file.",
        ),
    ],
) -> None:
    """Inspect a circuit-definition source file through sc_core."""
    inspection = inspect_circuit_definition_source(source_file.read_text(encoding="utf-8"))
    typer.echo(render_circuit_definition_inspection(source_file, inspection))
