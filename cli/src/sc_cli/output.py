"""Shared CLI output-mode declarations."""

from enum import Enum
from typing import Annotated

import typer


class OutputMode(str, Enum):
    TEXT = "text"
    JSON = "json"


OutputOption = Annotated[
    OutputMode,
    typer.Option(
        "--output",
        case_sensitive=False,
        help="Output format: text (default) or json.",
    ),
]
