#!/usr/bin/env python3
"""CLI wrapper for HFSS phase file conversion."""

import argparse
from pathlib import Path
from typing import NamedTuple

from sc_analysis.application.services.hfss_processing import process_and_write_hfss_file

DEFAULT_FILES = ["LJPAL658_v3_S11_Phase_Deg.csv"]


class HFSSArgs(NamedTuple):
    csv: list[Path]
    component_id: str | None
    output: Path | None


def parse_args() -> HFSSArgs:
    parser = argparse.ArgumentParser(description="Convert HFSS phase CSV to preprocessed JSON.")
    parser.add_argument(
        "csv",
        nargs="*",
        type=Path,
        help="Path(s) to HFSS phase CSV.",
    )
    parser.add_argument("--component-id", help="Override component identifier")
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination JSON file (defaults to data/preprocessed/<component_id>.json)",
    )
    args = parser.parse_args()
    return HFSSArgs(csv=args.csv, component_id=args.component_id, output=args.output)


def main() -> None:
    args = parse_args()
    input_files = args.csv if args.csv else [Path(f) for f in DEFAULT_FILES]

    if not input_files:
        print("No input files specified or default files found.")
        return

    for raw_path in input_files:
        process_and_write_hfss_file(
            file_path=raw_path,
            file_type="phase",
            component_id=args.component_id,
            output_path=args.output,
        )


if __name__ == "__main__":
    main()
