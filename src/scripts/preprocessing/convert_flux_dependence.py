#!/usr/bin/env python3
"""CLI for converting Flux Dependence VNA data (DB Only)."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from core.analysis.application.preprocessing.flux_dependence import parse_flux_dependence_txt
from core.analysis.application.services.database_service import save_dataset_payload_to_db
from core.shared.logging import get_logger, setup_logging

logger = get_logger(__name__)
app = typer.Typer(add_completion=False)


@app.command()
def main(
    txt: Annotated[
        Optional[list[Path]],
        typer.Argument(help="Path(s) to Flux Dependence TXT file."),
    ] = None,
    dataset_name: Annotated[
        Optional[str],
        typer.Option("--dataset-name", help="Override dataset name"),
    ] = None,
    tags: Annotated[
        str,
        typer.Option(help="Comma-separated tags for database record"),
    ] = "",
) -> None:
    """Convert Flux Dependence TXT to SQLite database."""
    setup_logging(level="INFO")
    input_files = txt if txt else []
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    if not input_files:
        typer.echo("No input files specified.")
        return

    for txt_path in input_files:
        if not txt_path.exists():
            logger.error("File not found: %s", txt_path)
            continue

        name = dataset_name or txt_path.stem

        try:
            # Parse
            payload = parse_flux_dependence_txt(txt_path, name)

            # Save to DB
            save_dataset_payload_to_db(payload, name, tag_list)

        except Exception as e:
            logger.error("Failed to process %s: %s", txt_path, e)
            logger.debug("Traceback:", exc_info=True)


if __name__ == "__main__":
    app()
