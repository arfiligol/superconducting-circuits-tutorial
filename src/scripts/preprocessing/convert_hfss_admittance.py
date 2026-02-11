#!/usr/bin/env python3
"""CLI wrapper for HFSS admittance file conversion (DB Only)."""

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
    "PF6FQ_Q0_Readout_Im_Y11.csv",
    "PF6FQ_Q0_XY_and_Readout_Im_Y11.csv",
    "PF6FQ_Q0_XY_Im_Y11.csv",
]

# Override the dataset name (e.g., "MyDataset"). Set to None to use filename.
DEFAULT_DATASET_NAME: str | None = None
# ==========================================

app = typer.Typer(add_completion=False)


@app.command()
def main(
    csv: Annotated[
        list[Path] | None,
        typer.Argument(help="Path(s) to HFSS admittance CSV files or directories."),
    ] = None,
    dataset_name: Annotated[
        str | None,
        typer.Option("--dataset-name", help="Override dataset name (Single file only)"),
    ] = DEFAULT_DATASET_NAME,
    tags: Annotated[
        str,
        typer.Option(help="Comma-separated tags for database record"),
    ] = "",
) -> None:
    """
    Import HFSS admittance CSV to SQLite database.

    Supports both single files and directories.
    - If a directory is provided, scans for all *.csv files.
    - AUTOMATICALLY SKIPS datasets that already exist in the database (by name).
    - --dataset-name is ignored in batch/directory mode.
    - --tags are applied to all NEWLY imported datasets in this run.
    """
    setup_logging(level="INFO")

    # Use CLI args if provided, otherwise fall back to USER CONFIGURATION
    input_files = csv if csv else [Path(f) for f in DEFAULT_INPUT_FILES]

    # Filter out empty paths if logic requires, but Path(f) is robust.
    # Check if files exist or just pass to import function
    if not input_files:
        typer.echo("No input files specified in CLI arguments or USER CONFIGURATION.")
        return

    # Expand directories to files
    processed_files: list[Path] = []
    for path in input_files:
        if path.is_dir():
            processed_files.extend(path.glob("*.csv"))
        else:
            processed_files.append(path)

    # Sort for deterministic processing order
    processed_files.sort()

    if not processed_files:
        typer.echo("No CSV files found.")
        return

    from core.analysis.application.preprocessing.naming import strip_dataset_suffix
    from core.shared.persistence import get_unit_of_work

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    # Processing loop with existence check
    for raw_path in processed_files:
        # Determine target dataset name
        # If user specified --dataset-name, use it (ONLY valid for single file)
        if dataset_name and len(processed_files) == 1:
            target_name = dataset_name
        else:
            # For batch mode, we ignore --dataset-name to avoid naming collisions
            if dataset_name and len(processed_files) > 1:
                typer.echo("Warning: --dataset-name ignored for batch processing. Using filenames.")
                dataset_name = None  # Reset to prevent misuse in loop
            target_name = strip_dataset_suffix(raw_path.stem)

        # Check if dataset exists in DB
        with get_unit_of_work() as uow:
            existing = uow.datasets.get_by_name(target_name)

        if existing:
            typer.echo(f"Skipping '{target_name}' (already exists)")
            continue

        typer.echo(f"Importing '{raw_path.name}' as '{target_name}'...")
        import_hfss_to_database(
            file_path=raw_path,
            file_type="admittance",
            # We pass specific name here to ensure consistency
            dataset_name=target_name,
            tags=tag_list,
        )


if __name__ == "__main__":
    app()
