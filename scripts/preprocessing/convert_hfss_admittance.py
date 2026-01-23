#!/usr/bin/env python3
"""CLI wrapper for HFSS admittance file conversion."""

import argparse
from pathlib import Path
from typing import NamedTuple

from sc_analysis.application.services.hfss_processing import process_and_write_hfss_file

DEFAULT_FILES = [
    "PF6FQ_Q0_Readout_Im_Y11.csv",
    "PF6FQ_Q0_XY_and_Readout_Im_Y11.csv",
    "PF6FQ_Q0_XY_Im_Y11.csv",
]


class ProgramArgs(NamedTuple):
    csv: list[Path]
    component_id: str | None
    output: Path | None


def parse_args() -> ProgramArgs:
    parser = argparse.ArgumentParser(
        description="Convert HFSS admittance CSV to preprocessed JSON."
    )
    parser.add_argument(
        "csv",
        nargs="*",
        type=Path,
        help="Path(s) to HFSS admittance CSV.",
    )
    parser.add_argument("--component-id", help="Override component identifier")
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination JSON file (defaults to data/preprocessed/<component_id>.json)",
    )
    args = parser.parse_args()
    return ProgramArgs(csv=args.csv, component_id=args.component_id, output=args.output)


def main() -> None:
    args = parse_args()
    input_files = args.csv if args.csv else [Path(f) for f in DEFAULT_FILES]

    if not input_files:
        print("No input files specified or default files found.")
        return

    for raw_path in input_files:
        process_and_write_hfss_file(
            file_path=raw_path,
            file_type="admittance",
            component_id=args.component_id,
            output_path=args.output,
        )


if __name__ == "__main__":
    main()
