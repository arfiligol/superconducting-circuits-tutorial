"""CLI to import HFSS generic S-Parameter CSVs to database."""

from pathlib import Path

import typer
from rich.console import Console

from core.analysis.application.services.database_import import import_hfss_to_database
from core.shared.logging import setup_logging

app = typer.Typer()
console = Console()


@app.command()
def main(
    csv_file: Path = typer.Argument(
        ...,
        help="Path to the generic S-Parameter CSV file payload (Re/Im/Phase/Mag).",
        exists=True,
    ),
) -> None:
    """Import generic HFSS S-Parameter CSV into the analysis database."""
    setup_logging(level="WARNING")

    try:
        # Determine dataset name automatically
        from core.analysis.application.preprocessing.naming import strip_dataset_suffix

        dataset_name = strip_dataset_suffix(csv_file.stem)
        console.print(f"Importing '{csv_file.name}' as '{dataset_name}'...")

        # Process and save using centralized importer
        import_hfss_to_database(
            file_path=csv_file,
            file_type="s_parameters",
            dataset_name=dataset_name,
            tags=None,
        )
        console.print(f"[green]Successfully imported {csv_file.name}[/green]")

    except Exception as e:
        console.print(f"[red]ERROR Failed to import {csv_file}: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
