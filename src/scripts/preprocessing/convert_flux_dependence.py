#!/usr/bin/env python3
"""CLI for converting Flux Dependence VNA data (DB Only)."""

import argparse
from pathlib import Path
from typing import NamedTuple

from core.analysis.application.preprocessing.flux_dependence import parse_flux_dependence_txt
from core.analysis.application.services.database_service import save_component_record_to_db
from core.shared.logging import get_logger, setup_logging

logger = get_logger(__name__)


class ProgramArgs(NamedTuple):
    txt: list[Path]
    component_id: str | None
    tags: list[str]


def parse_args() -> ProgramArgs:
    parser = argparse.ArgumentParser(description="Convert Flux Dependence TXT to SQLite database.")
    parser.add_argument(
        "txt",
        nargs="+",
        type=Path,
        help="Path(s) to Flux Dependence TXT file.",
    )
    parser.add_argument(
        "--component-id",
        help="Override component identifier",
    )
    parser.add_argument(
        "--tags",
        type=str,
        help="Comma-separated tags for database record",
        default="",
    )
    args = parser.parse_args()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    return ProgramArgs(
        txt=args.txt,
        component_id=args.component_id,
        tags=tags,
    )


def main() -> None:
    setup_logging(level="INFO")
    args = parse_args()

    for txt_path in args.txt:
        if not txt_path.exists():
            logger.error(f"File not found: {txt_path}")
            continue

        name = args.component_id or txt_path.stem

        try:
            # Parse
            record = parse_flux_dependence_txt(txt_path, name)

            # Save to DB
            save_component_record_to_db(record, name, args.tags)

        except Exception as e:
            logger.error(f"Failed to process {txt_path}: {e}")
            logger.debug("Traceback:", exc_info=True)


if __name__ == "__main__":
    main()
