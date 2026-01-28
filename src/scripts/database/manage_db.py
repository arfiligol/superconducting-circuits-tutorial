#!/usr/bin/env python3
"""CLI for managing the SQLite database (List, Info, Delete)."""

import sys

import typer

from rich.console import Console
from rich.table import Table

from core.analysis.application.services.dataset_management import DatasetManagementService
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(add_completion=False)


@app.command("list")
def handle_list() -> None:
    """Handle 'list' subcommand."""
    service = DatasetManagementService()
    datasets = service.list_datasets()

    if not datasets:
        console.print("[yellow]No datasets found in database.[/yellow]")
        return

    table = Table(title=f"All Datasets ({len(datasets)})")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Origin", style="blue")
    table.add_column("Created At", style="magenta")
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


@app.command("info")
def handle_info(
    identifier: str = typer.Argument(..., help="Dataset ID or Name"),
) -> None:
    """Handle 'info' subcommand."""
    service = DatasetManagementService()
    dataset = service.get_dataset(identifier)

    if not dataset:
        console.print(f"[red]Dataset not found:[/red] {identifier}")
        sys.exit(1)

    console.print(f"[bold cyan]Dataset Details: {dataset.name}[/bold cyan]")
    console.print(f"ID: {dataset.id}")
    console.print(f"Origin: {dataset.origin}")
    console.print(f"Created: {dataset.created_at}")
    console.print(f"Tags: {', '.join(dataset.tags)}")
    console.print(f"Data Records: {dataset.data_records_count}")

    if dataset.parameters:
        console.print("\n[bold]Sweep Parameters:[/bold]")
        for k, v in dataset.parameters.items():
            console.print(f"  - {k}: {v}")

    if dataset.source_files:
        console.print("\n[bold]Source Files:[/bold]")
        for f in dataset.source_files:
            console.print(f"  - {f}")


@app.command("delete")
def handle_delete(
    identifier: str = typer.Argument(..., help="Dataset ID or Name"),
) -> None:
    """Handle 'delete' subcommand."""
    service = DatasetManagementService()
    # Confirm before deleting
    dataset = service.get_dataset(identifier)
    if not dataset:
        console.print(f"[red]Dataset not found:[/red] {identifier}")
        sys.exit(1)

    confirm = console.input(
        f"[bold red]Are you sure you want to DELETE dataset '{dataset.name}' (ID: {dataset.id})? [y/N]: [/bold red]"
    )
    if confirm.lower() != "y":
        console.print("Operation cancelled.")
        return

    if service.delete_dataset(identifier):
        console.print(f"[green]Successfully deleted dataset:[/green] {dataset.name}")
    else:
        # Should catch race condition
        console.print(f"[red]Failed to delete dataset[/red] {identifier}")


def main() -> None:
    setup_logging(level="WARNING")

    try:
        app()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        # import traceback; traceback.print_exc()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
