"""Thin adapters for canonical circuit-definition workflows."""

from enum import Enum
from pathlib import Path
from typing import Annotated, cast

import typer
from sc_backend import BackendContractError, CircuitDefinitionSortBy, SortOrder
from sc_core import inspect_circuit_definition_source

from sc_cli.errors import exit_for_backend_error, exit_with_runtime_error, exit_with_usage_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import (
    render_circuit_definition_delete_result,
    render_circuit_definition_detail,
    render_circuit_definition_inspection,
    render_circuit_definition_summaries,
)
from sc_cli.runtime import (
    create_circuit_definition,
    delete_circuit_definition,
    get_circuit_definition,
    list_circuit_definitions,
    update_circuit_definition,
)

app = typer.Typer(help="Canonical circuit-definition helpers.", no_args_is_help=True)


class CircuitDefinitionSortOption(str, Enum):
    CREATED_AT = "created_at"
    NAME = "name"
    ELEMENT_COUNT = "element_count"


class SortOrderOption(str, Enum):
    ASC = "asc"
    DESC = "desc"


@app.command("list")
def list_command(
    search: Annotated[
        str | None,
        typer.Option("--search", help="Case-insensitive name substring filter."),
    ] = None,
    sort_by: Annotated[
        CircuitDefinitionSortOption,
        typer.Option("--sort-by", help="Sort field for persisted circuit definitions."),
    ] = CircuitDefinitionSortOption.CREATED_AT,
    sort_order: Annotated[
        SortOrderOption,
        typer.Option("--sort-order", help="Sort direction."),
    ] = SortOrderOption.DESC,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """List persisted rewrite circuit definitions."""
    try:
        definitions = list_circuit_definitions(
            search=search,
            sort_by=cast(CircuitDefinitionSortBy, sort_by.value),
            sort_order=cast(SortOrder, sort_order.value),
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_circuit_definition_summaries(definitions, output=output))


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
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Inspect a draft file through sc_core or a persisted rewrite definition by id."""
    if (source_file is None) == (definition_id is None):
        exit_with_usage_error("Provide exactly one of SOURCE_FILE or --definition-id.")

    if definition_id is not None:
        try:
            definition = get_circuit_definition(definition_id)
        except BackendContractError as error:
            exit_for_backend_error(error, output=output)
        typer.echo(render_circuit_definition_detail(definition, output=output))
        return

    assert source_file is not None
    try:
        source_text = source_file.read_text(encoding="utf-8")
    except OSError as error:
        exit_with_runtime_error(f"Could not read {source_file}: {error}")
    inspection = inspect_circuit_definition_source(source_text)
    typer.echo(render_circuit_definition_inspection(source_file, inspection, output=output))


@app.command("create")
def create_command(
    source_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to a circuit-definition source file to persist.",
        ),
    ],
    name: Annotated[
        str,
        typer.Option("--name", help="Display name for the persisted circuit definition."),
    ],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Create one persisted rewrite circuit definition from a local source file."""
    try:
        source_text = source_file.read_text(encoding="utf-8")
    except OSError as error:
        exit_with_runtime_error(f"Could not read {source_file}: {error}")

    try:
        definition = create_circuit_definition(name=name, source_text=source_text)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_circuit_definition_detail(definition, output=output))


@app.command("update")
def update_command(
    definition_id: Annotated[
        int,
        typer.Argument(min=1, help="Persisted circuit-definition id to update."),
    ],
    source_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to a replacement circuit-definition source file.",
        ),
    ],
    name: Annotated[
        str,
        typer.Option("--name", help="Display name for the updated circuit definition."),
    ],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Update one persisted rewrite circuit definition from a local source file."""
    try:
        source_text = source_file.read_text(encoding="utf-8")
    except OSError as error:
        exit_with_runtime_error(f"Could not read {source_file}: {error}")

    try:
        definition = update_circuit_definition(
            definition_id,
            name=name,
            source_text=source_text,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_circuit_definition_detail(definition, output=output))


@app.command("delete")
def delete_command(
    definition_id: Annotated[
        int,
        typer.Argument(min=1, help="Persisted circuit-definition id to delete."),
    ],
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            help="Confirm deletion of the persisted circuit definition.",
        ),
    ] = False,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Delete one persisted rewrite circuit definition."""
    if not yes:
        exit_with_usage_error("Pass --yes to delete a persisted circuit definition.")

    try:
        delete_circuit_definition(definition_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_circuit_definition_delete_result(definition_id, output=output))
