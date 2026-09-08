#!/usr/bin/env python3
"""Heuristic Pluto notebook reactivity preflight.

This script checks raw `.jl` Pluto notebooks for one common reactivity failure:
the same global name being defined in more than one cell. It is intentionally
conservative and does not replace Pluto's own syntax/dependency analysis.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

CELL_MARKER = re.compile(r"^# [╔╟]═╡ (?P<id>[0-9a-fA-F-]{36}|[0-9a-fA-F-]+)")
CELL_ORDER = "# ╔═╡ Cell order:"
IDENT = r"[A-Za-z_][A-Za-z_0-9!]*"
ASSIGN_OP = r"(?:=|\+=|-=|\*=|/=|//=|%=|\^=|\.=)"


@dataclass(frozen=True)
class Definition:
    name: str
    cell_id: str
    line: int
    code: str
    kind: str


@dataclass
class Cell:
    cell_id: str
    start_line: int
    lines: list[tuple[int, str]] = field(default_factory=list)


def split_cells(text: str) -> list[Cell]:
    cells: list[Cell] = []
    current: Cell | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if raw_line == CELL_ORDER:
            break

        marker = CELL_MARKER.match(raw_line)
        if marker:
            current = Cell(cell_id=marker.group("id"), start_line=line_number)
            cells.append(current)
            continue

        if current is not None:
            current.lines.append((line_number, raw_line))

    return cells


def strip_line_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False

    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char == "#" and not in_single and not in_double:
            return line[:index]

    return line


def update_delimiter_depth(line: str, depth: int) -> int:
    in_single = False
    in_double = False
    escaped = False

    for char in line:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if in_single or in_double:
            continue
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)

    return depth


def block_opener(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None

    patterns = [
        (r"^(?:mutable\s+struct|struct)\b", "local"),
        (r"^(?:baremodule|module)\b", "local"),
        (r"^function\b", "local"),
        (r"^macro\b", "local"),
        (r"^let\b", "local"),
        (r"^for\b", "local"),
        (r"^while\b", "local"),
        (r"^quote\b", "local"),
        (r"^begin\b", "transparent"),
        (r"^if\b", "transparent"),
        (r"^try\b", "transparent"),
    ]
    for pattern, kind in patterns:
        if re.search(pattern, stripped):
            return kind
    return None


def parse_lhs_names(lhs: str) -> list[str]:
    lhs = lhs.strip()
    lhs = re.sub(r"^(?:const|global)\s+", "", lhs)
    lhs = lhs.strip("() ")

    if not lhs:
        return []

    names: list[str] = []
    for part in lhs.split(","):
        candidate = part.strip()
        if re.fullmatch(IDENT, candidate):
            names.append(candidate)
    return names


def definitions_in_cell(cell: Cell) -> list[Definition]:
    definitions: list[Definition] = []
    block_stack: list[str] = []
    in_triple_string: str | None = None
    delimiter_depth = 0

    for line_number, raw_line in cell.lines:
        line = raw_line.rstrip("\n")

        triple_count = line.count('"""')
        single_triple_count = line.count("'''")
        if in_triple_string:
            token = in_triple_string
            if line.count(token) % 2 == 1:
                in_triple_string = None
            continue
        if triple_count % 2 == 1:
            in_triple_string = '"""'
            continue
        if single_triple_count % 2 == 1:
            in_triple_string = "'''"
            continue

        code = strip_line_comment(line).strip()
        if not code:
            continue

        while delimiter_depth == 0 and re.match(r"^end\b", code) and block_stack:
            block_stack.pop()
            code = re.sub(r"^end\b", "", code, count=1).strip()
            if not code:
                break
        if not code:
            continue

        local_depth = sum(1 for kind in block_stack if kind == "local")

        if local_depth == 0 and delimiter_depth == 0:
            bind_match = re.search(r"@bind\s+(" + IDENT + r")\b", code)
            if bind_match:
                definitions.append(
                    Definition(
                        name=bind_match.group(1),
                        cell_id=cell.cell_id,
                        line=line_number,
                        code=raw_line.strip(),
                        kind="@bind",
                    )
                )

            function_match = re.match(
                r"^(?:function\s+(" + IDENT + r")\b|(" + IDENT + r")\s*\([^=]*\)\s*=)",
                code,
            )
            if function_match:
                name = function_match.group(1) or function_match.group(2)
                definitions.append(
                    Definition(
                        name=name,
                        cell_id=cell.cell_id,
                        line=line_number,
                        code=raw_line.strip(),
                        kind="function",
                    )
                )

            type_match = re.match(
                r"^(?:mutable\s+struct|struct|module|baremodule|macro)\s+(" + IDENT + r")\b",
                code,
            )
            if type_match:
                definitions.append(
                    Definition(
                        name=type_match.group(1),
                        cell_id=cell.cell_id,
                        line=line_number,
                        code=raw_line.strip(),
                        kind="type/module/macro",
                    )
                )

            assign_match = re.match(r"^(.+?)\s*" + ASSIGN_OP + r"(?!=)", code)
            if assign_match and not re.search(r"[\]\.]\s*$", assign_match.group(1)):
                for name in parse_lhs_names(assign_match.group(1)):
                    definitions.append(
                        Definition(
                            name=name,
                            cell_id=cell.cell_id,
                            line=line_number,
                            code=raw_line.strip(),
                            kind="assignment",
                        )
                    )

        opener = block_opener(code)
        if delimiter_depth == 0 and opener:
            block_stack.append(opener)

        delimiter_depth = update_delimiter_depth(code, delimiter_depth)

    return definitions


def find_duplicate_definitions(cells: Iterable[Cell]) -> dict[str, list[Definition]]:
    by_name: dict[str, list[Definition]] = {}
    for cell in cells:
        seen_in_cell: set[str] = set()
        for definition in definitions_in_cell(cell):
            if definition.name in seen_in_cell:
                continue
            seen_in_cell.add(definition.name)
            by_name.setdefault(definition.name, []).append(definition)

    return {
        name: defs
        for name, defs in sorted(by_name.items())
        if len({definition.cell_id for definition in defs}) > 1
    }


def find_layout_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    uses_widecell = "WideCell" in text or "wide_figure_cell" in text
    uses_plutoui = "using PlutoUI" in text or "import PlutoUI" in text
    uses_plotly = any(
        token in text
        for token in (
            "PlotlyJS",
            "PlutoPlotly",
            "PlotlyBase",
            "PlotlyFigureConfig",
            "SuperconductingCircuitsVisualizer",
        )
    )

    if uses_plotly and not uses_widecell:
        warnings.append(
            "Plotly-style output detected without PlutoUI WideCell; "
            "large figures should be returned through WideCell."
        )
    if uses_widecell and not uses_plutoui:
        warnings.append("WideCell detected without `using PlutoUI` or `import PlutoUI`.")
    return warnings


def render_text(path: Path, duplicates: dict[str, list[Definition]], warnings: list[str]) -> str:
    lines: list[str] = []
    if not duplicates:
        lines.append(f"{path}: no duplicate global definitions found")
    else:
        lines.append(f"{path}: duplicate global definitions found:")
        for name, definitions in duplicates.items():
            lines.append(f"- {name}")
            for definition in definitions:
                lines.append(
                    f"  line {definition.line}, cell {definition.cell_id}, "
                    f"{definition.kind}: {definition.code}"
                )

    if warnings:
        lines.append(f"{path}: layout warnings:")
        for warning in warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path, help="Path to a Pluto `.jl` notebook")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit nonzero when layout warnings are found",
    )
    args = parser.parse_args(argv)

    text = args.notebook.read_text(encoding="utf-8")
    cells = split_cells(text)
    duplicates = find_duplicate_definitions(cells)
    warnings = find_layout_warnings(text)

    if args.json:
        payload = {
            "path": str(args.notebook),
            "duplicate_global_definitions": {
                name: [definition.__dict__ for definition in definitions]
                for name, definitions in duplicates.items()
            },
            "layout_warnings": warnings,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(args.notebook, duplicates, warnings))

    return 1 if duplicates or (args.fail_on_warnings and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
