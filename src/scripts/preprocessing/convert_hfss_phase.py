#!/usr/bin/env python3
"""CLI wrapper for HFSS phase file conversion (DB Only)."""

import argparse
from pathlib import Path
from typing import NamedTuple

from core.analysis.application.services.database_import import import_hfss_to_database
from core.shared.logging import setup_logging

# ==========================================
#           USER CONFIGURATION
# ==========================================
# List of HFSS CSV files to process if no command line arguments are provided
DEFAULT_INPUT_FILES = [
    "LJPAL658_v3_S11_Phase_Deg.csv",
]

# Override the component ID (e.g., "MyComponent"). Set to None to use filename.
DEFAULT_COMPONENT_ID: str | None = None
# ==========================================


class ProgramArgs(NamedTuple):
    csv: list[Path]
    component_id: str | None
    tags: list[str]


def parse_args() -> ProgramArgs:
    parser = argparse.ArgumentParser(description="Import HFSS phase CSV to SQLite database.")
    parser.add_argument(
        "csv",
        nargs="*",
        type=Path,
        help="Path(s) to HFSS phase CSV.",
    )
    parser.add_argument(
        "--component-id",
        help="Override component identifier",
        default=DEFAULT_COMPONENT_ID,
    )
    parser.add_argument(
        "--tags",
        type=str,
        help="Comma-separated tags for database record",
        default="",
    )
    args = parser.parse_args()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    return ProgramArgs(csv=args.csv, component_id=args.component_id, tags=tags)


def main() -> None:
    setup_logging(level="INFO")

    args = parse_args()
    # Use CLI args if provided, otherwise fall back to USER CONFIGURATION
    input_files = args.csv if args.csv else [Path(f) for f in DEFAULT_INPUT_FILES]

    if not input_files:
        print("No input files specified in CLI arguments or USER CONFIGURATION.")
        return

    for raw_path in input_files:
        import_hfss_to_database(
            file_path=raw_path,
            file_type="phase",
            dataset_name=args.component_id,
            tags=args.tags,
        )


if __name__ == "__main__":
    main()
