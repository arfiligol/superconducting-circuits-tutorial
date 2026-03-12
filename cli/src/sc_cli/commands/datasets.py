"""Commands for inspecting rewrite dataset state."""

from enum import Enum
from typing import Annotated, cast

import typer
from sc_backend import BackendContractError, DatasetSortBy, DatasetStatus, SortOrder

from sc_cli.errors import exit_for_backend_error
from sc_cli.output import OutputMode, OutputOption
from sc_cli.presenters import (
    render_dataset_detail,
    render_dataset_metadata_update,
    render_dataset_summaries,
)
from sc_cli.runtime import get_dataset, list_datasets, update_dataset_metadata

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


@app.command("show")
def show_command(
    dataset_id: Annotated[
        str,
        typer.Argument(help="Dataset id to inspect."),
    ],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Show one dataset from the rewrite integration scaffold."""
    try:
        dataset = get_dataset(dataset_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_dataset_detail(dataset, output=output))


@app.command("set-metadata")
def set_metadata_command(
    dataset_id: Annotated[
        str,
        typer.Argument(help="Dataset id to update."),
    ],
    device_type: Annotated[
        str,
        typer.Option("--device-type", help="Device type metadata value."),
    ],
    source: Annotated[
        str,
        typer.Option("--source", help="Dataset source metadata value."),
    ],
    capabilities: Annotated[
        list[str],
        typer.Option(
            "--capability",
            help="Capability metadata value. Repeat to provide multiple capabilities.",
        ),
    ],
    output: OutputOption = OutputMode.TEXT,
) -> None:
    """Update dataset metadata through the rewrite dataset scaffold."""
    try:
        result = update_dataset_metadata(
            dataset_id,
            device_type=device_type,
            capabilities=tuple(capabilities),
            source=source,
        )
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)
    typer.echo(render_dataset_metadata_update(result, output=output))
