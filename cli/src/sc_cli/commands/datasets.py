"""Commands for inspecting rewrite dataset state."""

from enum import Enum
from typing import Annotated, cast

import typer
from sc_backend import BackendContractError, DatasetSortBy, DatasetStatus, SortOrder

from sc_cli.errors import exit_for_backend_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import render_dataset_summaries
from sc_cli.runtime import list_datasets

app = typer.Typer(help="Rewrite dataset helpers.", no_args_is_help=True)


class DatasetStatusOption(str, Enum):
    READY = "Ready"
    QUEUED = "Queued"
    REVIEW = "Review"


class DatasetSortByOption(str, Enum):
    UPDATED_AT = "updated_at"
    NAME = "name"
    SAMPLES = "samples"


class SortOrderOption(str, Enum):
    ASC = "asc"
    DESC = "desc"


@app.command("list")
def list_command(
    family: Annotated[
        str | None,
        typer.Option("--family", help="Filter by dataset family."),
    ] = None,
    status: Annotated[
        DatasetStatusOption | None,
        typer.Option("--status", help="Filter by dataset status."),
    ] = None,
    sort_by: Annotated[
        DatasetSortByOption,
        typer.Option("--sort-by", help="Sort datasets by one contract field."),
    ] = DatasetSortByOption.UPDATED_AT,
    sort_order: Annotated[
        SortOrderOption,
        typer.Option("--sort-order", help="Sort direction."),
    ] = SortOrderOption.DESC,
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """List datasets from the rewrite integration scaffold."""
    try:
        datasets = list_datasets(
            family=family,
            status=None if status is None else cast(DatasetStatus, status.value),
            sort_by=cast(DatasetSortBy, sort_by.value),
            sort_order=cast(SortOrder, sort_order.value),
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_dataset_summaries(datasets, output=output))
