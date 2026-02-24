#!/usr/bin/env python3
"""CLI wrapper for HFSS scattering data conversion (Phase, Re, Im, Mag) (DB Only)."""

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
        typer.Argument(help="Path(s) to HFSS S-Parameter or Phase CSV."),
    ] = None,
    dataset_name: Annotated[
        str | None,
        typer.Option("--dataset-name", help="Override dataset name"),
    ] = DEFAULT_DATASET_NAME,
    tags: Annotated[
        str,
        typer.Option(help="Comma-separated tags for database record"),
    ] = "",
    match_keywords: Annotated[
        str,
        typer.Option(
            "--match",
            help="Comma-separated keywords to filter files (e.g., 'Phase,S21,deg,rad,re,im,mag'). ",
        ),
    ] = "Phase,S21,deg,rad,re,im,mag,S11",
) -> None:
    """
    Import HFSS scattering matrix CSV to SQLite database.

    Supports both single files and directories.
    - If a directory is provided, scans for all *.csv files.
    - AUTOMATICALLY SKIPS datasets that already exist in the database (by name).
    - --dataset-name is ignored in batch/directory mode.
    - --tags are applied to all NEWLY imported datasets in this run.
    - --match filters files in directories to only those containing any of the keywords.
    """
    setup_logging(level="INFO")

    # Use CLI args if provided, otherwise fall back to USER CONFIGURATION
    input_files = csv if csv else [Path(f) for f in DEFAULT_INPUT_FILES]

    if not input_files:
        typer.echo("No input files specified in CLI arguments or USER CONFIGURATION.")
        return

    # Expand directories to files
    processed_files: list[Path] = []

    keywords = [k.strip().lower() for k in match_keywords.split(",") if k.strip()]

    for path in input_files:
        if path.is_dir():
            for f in path.glob("*.csv"):
                # Check if file matches any of the keywords
                if not keywords or any(k in f.name.lower() for k in keywords):
                    processed_files.append(f)
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
        if dataset_name and len(processed_files) == 1:
            target_name = dataset_name
        else:
            if dataset_name and len(processed_files) > 1:
                typer.echo("Warning: --dataset-name ignored for batch processing. Using filenames.")
                dataset_name = None
            target_name = strip_dataset_suffix(raw_path.stem)

        typer.echo(f"Importing '{raw_path.name}' as '{target_name}'...")
        import_hfss_to_database(
            file_path=raw_path,
            file_type="scattering",
            dataset_name=target_name,
            tags=tag_list,
        )


if __name__ == "__main__":
    app()
