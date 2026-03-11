"""Thin adapters for canonical circuit-definition workflows."""

from pathlib import Path
from typing import Annotated

import typer
from sc_backend import BackendContractError
from sc_core import inspect_circuit_definition_source

from sc_cli.errors import exit_for_backend_error, exit_with_runtime_error, exit_with_usage_error
from sc_cli.presenters import render_circuit_definition_detail, render_circuit_definition_inspection
from sc_cli.runtime import get_circuit_definition

app = typer.Typer(help="Canonical circuit-definition helpers.", no_args_is_help=True)


@app.command("inspect")
def inspect_command(
    source_file: Annotated[
        Path | None,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to a circuit-definition draft file.",
        ),
    ] = None,
    definition_id: Annotated[
        int | None,
        typer.Option(
            "--definition-id",
            min=1,
            help="Inspect one persisted rewrite circuit definition by id.",
        ),
    ] = None,
) -> None:
    """Inspect a draft file through sc_core or a persisted rewrite definition by id."""
    if (source_file is None) == (definition_id is None):
        exit_with_usage_error("Provide exactly one of SOURCE_FILE or --definition-id.")

    if definition_id is not None:
        try:
            definition = get_circuit_definition(definition_id)
        except BackendContractError as error:
            exit_for_backend_error(error)
        typer.echo(render_circuit_definition_detail(definition))
        return

    assert source_file is not None
    try:
        source_text = source_file.read_text(encoding="utf-8")
    except OSError as error:
        exit_with_runtime_error(f"Could not read {source_file}: {error}")
    inspection = inspect_circuit_definition_source(source_text)
    typer.echo(render_circuit_definition_inspection(source_file, inspection))
