"""Sandbox: preview resonance sweep tables from analysis_result DataRecords."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Annotated

import plotly.graph_objects as go
import typer

from core.shared.persistence import get_unit_of_work
from core.shared.persistence.database import DATABASE_PATH

app = typer.Typer(add_completion=False, help="Preview resonance sweep table with Plotly.")


def _default_output_path() -> Path:
    reports_dir = DATABASE_PATH.parent / "processed" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return reports_dir / f"resonance_sweep_table_preview_{stamp}.html"


def _infer_qubit_label(dataset_name: str) -> str:
    for token in dataset_name.replace("-", "_").split("_"):
        token_upper = token.upper()
        if len(token_upper) >= 2 and token_upper[0] == "Q" and token_upper[1:].isdigit():
            return token_upper
    return dataset_name


def _infer_line_group(dataset_name: str) -> str:
    normalized = dataset_name.lower()
    if "xy_and_readout" in normalized or ("xy" in normalized and "readout" in normalized):
        return "XY + Readout"
    if "readout" in normalized:
        return "Readout"
    if "xy" in normalized:
        return "XY"
    return dataset_name


def _to_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _load_resonance_rows(dataset_filters: list[str]) -> tuple[list[dict[str, object]], list[str]]:
    missing_filters: list[str] = []
    with get_unit_of_work() as uow:
        dataset_map = {
            int(dataset.id): dataset.name
            for dataset in uow.datasets.list_all()
            if dataset.id is not None
        }

        selected_ids: set[int] | None = None
        if dataset_filters:
            selected_ids = set()
            for token in dataset_filters:
                if token.isdigit():
                    selected_ids.add(int(token))
                    continue
                dataset = uow.datasets.get_by_name(token)
                if dataset and dataset.id is not None:
                    selected_ids.add(int(dataset.id))
                else:
                    missing_filters.append(token)

        rows: list[dict[str, object]] = []
        for record in uow.data_records.list_all():
            if record.data_type != "analysis_result":
                continue
            if record.parameter != "f_resonance":
                continue
            if selected_ids is not None and record.dataset_id not in selected_ids:
                continue

            dataset_name = dataset_map.get(record.dataset_id, f"<missing:{record.dataset_id}>")
            mode_name = record.representation

            if not record.axes:
                continue
            axis = record.axes[0]
            axis_values = axis.get("values", [])
            resonance_values = record.values if isinstance(record.values, list) else []

            for l_jun_raw, freq_raw in zip(axis_values, resonance_values, strict=False):
                l_jun = _to_float(l_jun_raw)
                freq = _to_float(freq_raw)
                if l_jun is None or freq is None:
                    continue
                rows.append(
                    {
                        "dataset_id": int(record.dataset_id),
                        "dataset_name": dataset_name,
                        "mode": mode_name,
                        "l_jun_nh": l_jun,
                        "f_resonance_ghz": freq,
                        "qubit": _infer_qubit_label(dataset_name),
                        "line": _infer_line_group(dataset_name),
                    }
                )

    rows.sort(
        key=lambda row: (
            str(row["dataset_name"]).casefold(),
            str(row["mode"]).casefold(),
            float(row["l_jun_nh"]),
        )
    )
    return rows, missing_filters


def _mock_rows() -> list[dict[str, object]]:
    return [
        {
            "dataset_id": 101,
            "dataset_name": "PF6FQ_Q0_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4253,
            "qubit": "Q0",
            "line": "Readout",
        },
        {
            "dataset_id": 102,
            "dataset_name": "PF6FQ_Q0_XY",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4909,
            "qubit": "Q0",
            "line": "XY",
        },
        {
            "dataset_id": 103,
            "dataset_name": "PF6FQ_Q0_XY_and_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4235,
            "qubit": "Q0",
            "line": "XY + Readout",
        },
        {
            "dataset_id": 201,
            "dataset_name": "PF6FQ_Q1_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4088,
            "qubit": "Q1",
            "line": "Readout",
        },
        {
            "dataset_id": 202,
            "dataset_name": "PF6FQ_Q1_XY",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4947,
            "qubit": "Q1",
            "line": "XY",
        },
        {
            "dataset_id": 203,
            "dataset_name": "PF6FQ_Q1_XY_and_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4049,
            "qubit": "Q1",
            "line": "XY + Readout",
        },
    ]


def _build_long_table(rows: list[dict[str, object]], title: str) -> go.Figure:
    headers = [
        "Dataset",
        "Dataset ID",
        "Mode",
        "L_jun (nH)",
        "f_resonance (GHz)",
        "Qubit",
        "Line",
    ]
    values = [
        [str(row["dataset_name"]) for row in rows],
        [str(row["dataset_id"]) for row in rows],
        [str(row["mode"]) for row in rows],
        [f"{float(row['l_jun_nh']):.6g}" for row in rows],
        [f"{float(row['f_resonance_ghz']):.12g}" for row in rows],
        [str(row["qubit"]) for row in rows],
        [str(row["line"]) for row in rows],
    ]
    return _build_table(headers, values, title)


def _build_pivot_table(
    rows: list[dict[str, object]],
    mode: str,
    l_jun_nh: float | None,
    title: str,
) -> go.Figure:
    mode_rows = [row for row in rows if str(row["mode"]).casefold() == mode.casefold()]
    if not mode_rows:
        raise ValueError(f"No rows found for mode '{mode}'.")

    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in mode_rows:
        grouped[(str(row["qubit"]), str(row["line"]))].append(row)

    cell_map: dict[tuple[str, str], float] = {}
    for key, candidates in grouped.items():
        ordered = sorted(candidates, key=lambda row: float(row["l_jun_nh"]))
        if l_jun_nh is None:
            chosen = ordered[0]
        else:
            chosen = min(ordered, key=lambda row: abs(float(row["l_jun_nh"]) - l_jun_nh))
        cell_map[key] = float(chosen["f_resonance_ghz"])

    qubits = sorted({key[0] for key in cell_map})
    preferred_lines = ["Readout", "XY", "XY + Readout"]
    other_lines = sorted({key[1] for key in cell_map if key[1] not in preferred_lines})
    lines = preferred_lines + other_lines

    headers = ["Qubit", *lines]
    columns: list[list[str]] = [[qubit for qubit in qubits]]
    for line in lines:
        columns.append(
            [
                f"{cell_map[(qubit, line)]:.12g}" if (qubit, line) in cell_map else "-"
                for qubit in qubits
            ]
        )

    subtitle = (
        f"{title} | mode={mode}"
        if l_jun_nh is None
        else f"{title} | mode={mode}, target L_jun={l_jun_nh:.6g} nH"
    )
    return _build_table(headers, columns, subtitle)


def _build_table(headers: list[str], columns: list[list[str]], title: str) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Table(
                header={
                    "values": headers,
                    "align": "left",
                    "fill_color": "#2f3e46",
                    "font": {"color": "white", "size": 13},
                    "height": 30,
                },
                cells={
                    "values": columns,
                    "align": "left",
                    "fill_color": [["#f8f9fa", "#ffffff"] * 200],
                    "font": {"size": 12, "color": "#1f2933"},
                    "height": 28,
                },
            )
        ]
    )
    fig.update_layout(
        title={"text": title, "x": 0.01},
        template="plotly_white",
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
        height=max(300, 90 + 30 * max(1, len(columns[0]))),
    )
    return fig


@app.command()
def main(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output HTML file path. Defaults to data/processed/reports/...",
        ),
    ] = None,
    png_output: Annotated[
        Path | None,
        typer.Option(
            "--png-output",
            help="Optional PNG output path (requires kaleido).",
        ),
    ] = None,
    dataset: Annotated[
        list[str] | None,
        typer.Option(
            "--dataset",
            "-d",
            help="Dataset filter by ID or name. Repeat option to include multiple datasets.",
        ),
    ] = None,
    mode: Annotated[
        str,
        typer.Option(
            "--mode",
            help="Mode label used in pivot mode.",
        ),
    ] = "Mode 1",
    l_jun_nh: Annotated[
        float | None,
        typer.Option(
            "--l-jun-nh",
            help="Target L_jun (nH) used to pick values in pivot mode.",
        ),
    ] = None,
    pivot: Annotated[
        bool,
        typer.Option(
            "--pivot/--long",
            help="Render pivot table (Qubit x Line) or long table.",
        ),
    ] = True,
    mock_on_empty: Annotated[
        bool,
        typer.Option(
            "--mock-on-empty/--no-mock-on-empty",
            help="Render mock rows when no resonance sweep exists in DB.",
        ),
    ] = True,
    show: Annotated[
        bool,
        typer.Option(
            "--show/--no-show",
            help="Open interactive Plotly preview in browser (fig.show()).",
        ),
    ] = True,
    save_html: Annotated[
        bool,
        typer.Option(
            "--save-html/--no-save-html",
            help="Save HTML output file.",
        ),
    ] = False,
) -> None:
    """Render resonance-frequency table from analysis_result DataRecords."""
    rows, missing_filters = _load_resonance_rows(dataset or [])
    if missing_filters:
        typer.echo(f"Warning: unknown dataset filters ignored: {', '.join(missing_filters)}")

    used_mock = False
    if not rows and mock_on_empty:
        rows = _mock_rows()
        used_mock = True

    if not rows:
        typer.echo("No resonance sweep rows found. Nothing to render.")
        raise typer.Exit(code=1)

    title = "Resonance Sweep Table Preview"
    if used_mock:
        title += " (mock data)"
    fig = (
        _build_pivot_table(rows, mode=mode, l_jun_nh=l_jun_nh, title=title)
        if pivot
        else _build_long_table(rows, title=title)
    )

    if show:
        fig.show()

    if save_html:
        output_path = output or _default_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path), include_plotlyjs="cdn")
        typer.echo(f"HTML written: {output_path.resolve()}")

    if png_output:
        png_output.parent.mkdir(parents=True, exist_ok=True)
        try:
            fig.write_image(str(png_output), width=1800, scale=2)
            typer.echo(f"PNG written: {png_output.resolve()}")
        except Exception as exc:  # pragma: no cover - dependency dependent
            typer.echo(f"PNG export skipped (kaleido missing or failed): {exc}")


if __name__ == "__main__":
    app()
