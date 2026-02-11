#!/usr/bin/env python3
"""CLI wrapper for HFSS phase file conversion (DB Only)."""

from pathlib import Path
from typing import Annotated

import typer

from core.analysis.application.services.database_import import import_hfss_to_database
from core.shared.logging import setup_logging

# ==========================================
#           USER CONFIGURATION
# ==========================================
# List of HFSS CSV files to process if no command line arguments are provided
DEFAULT_INPUT_FILES = [
    "LJPAL658_v3_S11_Phase_Deg.csv",
]

# Override the dataset name (e.g., "MyDataset"). Set to None to use filename.
DEFAULT_DATASET_NAME: str | None = None
# ==========================================

app = typer.Typer(add_completion=False)


@app.command()
def main(
    csv: Annotated[
        list[Path] | None,
        typer.Argument(help="Path(s) to HFSS phase CSV."),
    ] = None,
    dataset_name: Annotated[
        str | None,
        typer.Option("--dataset-name", help="Override dataset name"),
    ] = DEFAULT_DATASET_NAME,
    tags: Annotated[
        str,
        typer.Option(help="Comma-separated tags for database record"),
    ] = "",
) -> None:
    """Import HFSS phase CSV to SQLite database."""
    setup_logging(level="INFO")

    # Use CLI args if provided, otherwise fall back to USER CONFIGURATION
    input_files = csv if csv else [Path(f) for f in DEFAULT_INPUT_FILES]

    if not input_files:
        typer.echo("No input files specified in CLI arguments or USER CONFIGURATION.")
        return

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    for raw_path in input_files:
        import_hfss_to_database(
            file_path=raw_path,
            file_type="phase",
            dataset_name=dataset_name,
            tags=tag_list,
        )


if __name__ == "__main__":
    app()
