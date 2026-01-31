#!/usr/bin/env python3
"""CLI for managing the SQLite database (Multi-model)."""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from core.analysis.application.services.data_record_management import (
    DataRecordManagementService,
)
from core.analysis.application.services.dataset_management import DatasetManagementService
from core.analysis.application.services.parameter_management import ParameterManagementService
from core.analysis.application.services.tag_management import TagManagementService
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="Manage SQLite database entities.", add_completion=False)

# =======================
# DATASET COMMANDS
# =======================
dataset_app = typer.Typer(help="Manage Datasets")
app.add_typer(dataset_app, name="dataset-record")


@dataset_app.command("list")
def list_datasets() -> None:
    """List all datasets."""
    service = DatasetManagementService()
    datasets = service.list_datasets()

    if not datasets:
        console.print("[yellow]No datasets found.[/yellow]")
        return

    table = Table(title=f"Datasets ({len(datasets)})")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Origin", style="blue")
    table.add_column("Created", style="magenta")
    table.add_column("Tags", style="yellow")

    for ds in datasets:
        table.add_row(
            str(ds.id),
            ds.name,
            ds.origin or "-",
            ds.created_at.strftime("%Y-%m-%d %H:%M"),
            ", ".join(ds.tags) if ds.tags else "-",
        )
    console.print(table)


@dataset_app.command("info")
def get_dataset(identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")]) -> None:
    """Show dataset details."""
    service = DatasetManagementService()
    dataset = service.get_dataset(identifier)

    if not dataset:
        console.print(f"[red]Dataset not found:[/red] {identifier}")
        raise typer.Exit(code=1)

    console.print(f"[bold cyan]Dataset: {dataset.name}[/bold cyan]")
    console.print(f"ID: {dataset.id}")
    console.print(f"Origin: {dataset.origin}")
    console.print(f"Tags: {', '.join(dataset.tags)}")
    console.print(f"Records: {dataset.data_records_count}")

    if dataset.parameters:
        console.print("[bold]Sweep Params:[/bold]")
        for k, v in dataset.parameters.items():
            console.print(f"  {k}: {v}")

    if dataset.source_files:
        console.print("[bold]Source Files:[/bold]")
        for f in dataset.source_files:
            console.print(f"  {f}")


@dataset_app.command("delete")
def delete_dataset(
    identifiers: Annotated[list[str], typer.Argument(help="Dataset IDs or Names")],
) -> None:
    """Delete datasets (Cascades to DataRecords/Params)."""
    service = DatasetManagementService()

    # Resolve all datasets first
    targets = []
    missing = []

    for identifier in identifiers:
        ds = service.get_dataset(identifier)
        if ds:
            targets.append(ds)
        else:
            missing.append(identifier)

    if missing:
        console.print(f"[yellow]Skipping not found:[/yellow] {', '.join(missing)}")

    if not targets:
        console.print("[red]No valid datasets specified.[/red]")
        raise typer.Exit(code=1)

    # List targets
    console.print("[bold red]The following datasets will be PERMANENTLY deleted:[/bold red]")
    for ds in targets:
        console.print(f" - {ds.name} (ID: {ds.id})")

    confirm = console.input(f"\n[bold red]Delete {len(targets)} datasets? [y/N]: [/bold red]")
    if confirm.lower() != "y":
        return

    deleted_count = 0
    for ds in targets:
        if service.delete_dataset(str(ds.id)):
            console.print(f"[green]Deleted:[/green] {ds.name}")
            deleted_count += 1

    console.print(f"Total deleted: {deleted_count}")


@dataset_app.command("auto-reorder")
def auto_reorder_datasets() -> None:
    """Auto-reorder Dataset IDs to be sequential."""
    service = DatasetManagementService()
    count = service.auto_reorder()
    console.print(f"[green]Reordered {count} datasets.[/green]")


# =======================
# TAG COMMANDS
# =======================
tag_app = typer.Typer(help="Manage Tags")
app.add_typer(tag_app, name="tag")


@tag_app.command("list")
def list_tags() -> None:
    """List all tags."""
    service = TagManagementService()
    tags = service.list_tags()

    if not tags:
        console.print("[yellow]No tags found.[/yellow]")
        return

    table = Table(title=f"Tags ({len(tags)})")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="green")

    for t in tags:
        table.add_row(str(t.id), t.name)
    console.print(table)


@tag_app.command("create")
def create_tag(name: Annotated[str, typer.Argument(help="Tag Name")]) -> None:
    """Create a new tag."""
    service = TagManagementService()
    tag = service.create_tag(name)
    console.print(f"[green]Tag ready:[/green] {tag.name} (ID: {tag.id})")


@tag_app.command("update")
def update_tag(
    identifier: Annotated[str, typer.Argument(help="Existing Tag ID or Name")],
    name: Annotated[str, typer.Argument(help="New Name")],
) -> None:
    """Rename a tag."""
    service = TagManagementService()
    updated = service.update_tag(identifier, name)
    if updated:
        console.print(f"[green]Updated tag:[/green] {updated.name} (ID: {updated.id})")
    else:
        console.print(f"[red]Tag not found:[/red] {identifier}")
        raise typer.Exit(code=1)


@tag_app.command("delete")
def delete_tag(identifier: Annotated[str, typer.Argument(help="Tag ID or Name")]) -> None:
    """Delete a tag (Removes tag, keeps datasets)."""
    service = TagManagementService()
    # Confirm
    tag = service.get_tag(identifier)
    if not tag:
        console.print(f"[red]Not found:[/red] {identifier}")
        raise typer.Exit(code=1)

    confirm = console.input(f"[bold red]Delete tag '{tag.name}'? [y/N]: [/bold red]")
    if confirm.lower() != "y":
        return

    if service.delete_tag(identifier):
        console.print(f"[green]Deleted tag:[/green] {tag.name}")


@tag_app.command("auto-reorder")
def auto_reorder_tags() -> None:
    """Auto-reorder Tag IDs to be sequential."""
    service = TagManagementService()
    count = service.auto_reorder()
    console.print(f"[green]Reordered {count} tags.[/green]")


# =======================
# DATA RECORD COMMANDS
# =======================
data_app = typer.Typer(help="Manage Data Records")
app.add_typer(data_app, name="data-record")


@data_app.command("list")
def list_data() -> None:
    """List all data records."""
    service = DataRecordManagementService()
    records = service.list_records()

    if not records:
        console.print("[yellow]No data records found.[/yellow]")
        return

    table = Table(title=f"Data Records ({len(records)})")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Dataset ID", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Param", style="blue")
    table.add_column("Rep", style="dim")

    for r in records:
        table.add_row(str(r.id), str(r.dataset_id), r.data_type, r.parameter, r.representation)
    console.print(table)


@data_app.command("info")
def get_data(id: Annotated[int, typer.Argument(help="DataRecord ID")]) -> None:
    """Show details for a data record."""
    service = DataRecordManagementService()
    record = service.get_record(id)
    if not record:
        console.print(f"[red]Not found:[/red] {id}")
        raise typer.Exit(code=1)

    console.print(f"[bold cyan]DataRecord {record.id}[/bold cyan]")
    console.print(f"Dataset ID: {record.dataset_id}")
    console.print(f"Type: {record.data_type} / {record.parameter}")
    console.print(f"Representation: {record.representation}")
    console.print(f"Axes: {len(record.axes)} axis defs")
    console.print(f"Values: {len(record.values) if isinstance(record.values, list) else 'Complex'}")


@data_app.command("delete")
def delete_data(id: Annotated[int, typer.Argument(help="DataRecord ID")]) -> None:
    """Delete a data record."""
    service = DataRecordManagementService()
    # Confirm
    record = service.get_record(id)
    if not record:
        console.print(f"[red]Not found:[/red] {id}")
        raise typer.Exit(code=1)

    confirm = console.input(f"[bold red]Delete DataRecord {id}? [y/N]: [/bold red]")
    if confirm.lower() != "y":
        return

    if service.delete_record(id):
        console.print(f"[green]Deleted DataRecord:[/green] {id}")


@data_app.command("auto-reorder")
def auto_reorder_data() -> None:
    """Auto-reorder DataRecord IDs to be sequential."""
    service = DataRecordManagementService()
    count = service.auto_reorder()
    console.print(f"[green]Reordered {count} data records.[/green]")


# =======================
# PARAMETER COMMANDS
# =======================
param_app = typer.Typer(help="Manage Derived Parameters")
app.add_typer(param_app, name="derived-parameter")


@param_app.command("list")
def list_params() -> None:
    """List all derived parameters."""
    service = ParameterManagementService()
    params = service.list_params()

    if not params:
        console.print("[yellow]No parameters found.[/yellow]")
        return

    table = Table(title=f"Parameters ({len(params)})")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Dataset ID", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Value", style="blue")
    table.add_column("Unit", style="dim")

    for p in params:
        table.add_row(str(p.id), str(p.dataset_id), p.name, f"{p.value:.4g}", p.unit or "-")
    console.print(table)


@param_app.command("info")
def get_param(id: Annotated[int, typer.Argument(help="Parameter ID")]) -> None:
    """Show details for a parameter."""
    service = ParameterManagementService()
    param = service.get_param(id)
    if not param:
        console.print(f"[red]Not found:[/red] {id}")
        raise typer.Exit(code=1)

    console.print(f"[bold cyan]Parameter {param.id}[/bold cyan]")
    console.print(f"Dataset ID: {param.dataset_id}")
    console.print(f"Name: {param.name}")
    console.print(f"Value: {param.value} {param.unit or ''}")
    console.print(f"Device: {param.device_type}")
    console.print(f"Method: {param.method or '-'}")
    console.print(f"Extra: {param.extra}")


@param_app.command("delete")
def delete_param(id: Annotated[int, typer.Argument(help="Parameter ID")]) -> None:
    """Delete a derived parameter."""
    service = ParameterManagementService()
    param = service.get_param(id)
    if not param:
        console.print(f"[red]Not found:[/red] {id}")
        raise typer.Exit(code=1)

    confirm = console.input(
        f"[bold red]Delete Parameter '{param.name}' (ID: {id})? [y/N]: [/bold red]"
    )
    if confirm.lower() != "y":
        return

    if service.delete_param(id):
        console.print(f"[green]Deleted Parameter:[/green] {id}")


@param_app.command("auto-reorder")
def auto_reorder_params() -> None:
    """Auto-reorder Parameter IDs to be sequential."""
    service = ParameterManagementService()
    count = service.auto_reorder()
    console.print(f"[green]Reordered {count} parameters.[/green]")


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
