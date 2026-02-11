"""Plot resonance-frequency maps grouped by qubit and structure."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal

import plotly.graph_objects as go
import typer

from core.shared.persistence import get_unit_of_work
from core.shared.persistence.database import DATABASE_PATH

app = typer.Typer(add_completion=False, help="Resonance map plotting commands.")

AggregationMode = Literal["first", "mean", "min", "max"]
RenderMode = Literal["heatmap", "table"]


def _default_output_path(stem: str) -> Path:
    reports_dir = DATABASE_PATH.parent / "processed" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return reports_dir / f"{stem}_{stamp}.html"


def _infer_qubit_label(dataset_name: str) -> str:
    for token in dataset_name.replace("-", "_").split("_"):
        upper = token.upper()
        if len(upper) >= 2 and upper[0] == "Q" and upper[1:].isdigit():
            return upper
    return dataset_name


def _infer_structure_label(dataset_name: str) -> str:
    normalized = dataset_name.lower()
    if "xy_and_readout" in normalized or ("xy" in normalized and "readout" in normalized):
        return "XY + Readout"
    if "readout" in normalized:
        return "Readout"
    if "xy" in normalized:
        return "XY"
    return dataset_name


def _parse_qubit_sort_key(label: str) -> tuple[int, str]:
    text = label.strip().upper()
    if len(text) >= 2 and text[0] == "Q" and text[1:].isdigit():
        return (0, f"{int(text[1:]):06d}")
    return (1, text.casefold())


def _to_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _select_frequency(
    candidates: list[dict[str, float]],
    target_l_jun_nh: float | None,
    aggregate: AggregationMode,
) -> tuple[float, str]:
    ordered = sorted(candidates, key=lambda row: row["l_jun_nh"])
    if target_l_jun_nh is not None:
        chosen = min(ordered, key=lambda row: abs(row["l_jun_nh"] - target_l_jun_nh))
        return chosen["f_resonance_ghz"], f"{chosen['l_jun_nh']:.6g}"

    if aggregate == "first":
        chosen = ordered[0]
        return chosen["f_resonance_ghz"], f"{chosen['l_jun_nh']:.6g}"

    values = [row["f_resonance_ghz"] for row in ordered]
    if aggregate == "mean":
        return sum(values) / len(values), "mean"
    if aggregate == "min":
        return min(values), "min"
    if aggregate == "max":
        return max(values), "max"
    raise ValueError(f"Unsupported aggregate mode: {aggregate}")


def _load_rows(dataset_filters: list[str]) -> tuple[list[dict[str, object]], list[str]]:
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
            raw_values = record.values if isinstance(record.values, list) else []

            for l_jun_raw, freq_raw in zip(axis_values, raw_values, strict=False):
                l_jun_nh = _to_float(l_jun_raw)
                freq_ghz = _to_float(freq_raw)
                if l_jun_nh is None or freq_ghz is None:
                    continue
                rows.append(
                    {
                        "dataset_id": int(record.dataset_id),
                        "dataset_name": dataset_name,
                        "mode": mode_name,
                        "l_jun_nh": l_jun_nh,
                        "f_resonance_ghz": freq_ghz,
                        "qubit": _infer_qubit_label(dataset_name),
                        "structure": _infer_structure_label(dataset_name),
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
            "structure": "Readout",
        },
        {
            "dataset_id": 102,
            "dataset_name": "PF6FQ_Q0_XY",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4909,
            "qubit": "Q0",
            "structure": "XY",
        },
        {
            "dataset_id": 103,
            "dataset_name": "PF6FQ_Q0_XY_and_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4235,
            "qubit": "Q0",
            "structure": "XY + Readout",
        },
        {
            "dataset_id": 201,
            "dataset_name": "PF6FQ_Q1_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4088,
            "qubit": "Q1",
            "structure": "Readout",
        },
        {
            "dataset_id": 202,
            "dataset_name": "PF6FQ_Q1_XY",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4947,
            "qubit": "Q1",
            "structure": "XY",
        },
        {
            "dataset_id": 203,
            "dataset_name": "PF6FQ_Q1_XY_and_Readout",
            "mode": "Mode 1",
            "l_jun_nh": 0.10,
            "f_resonance_ghz": 4.4049,
            "qubit": "Q1",
            "structure": "XY + Readout",
        },
    ]


def _build_matrix(
    rows: list[dict[str, object]],
    mode: str,
    target_l_jun_nh: float | None,
    aggregate: AggregationMode,
) -> tuple[list[str], list[str], list[list[float | None]], list[list[str]]]:
    mode_rows = [row for row in rows if str(row["mode"]).casefold() == mode.casefold()]
    if not mode_rows:
        raise ValueError(f"No rows found for mode '{mode}'.")

    grouped: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
    for row in mode_rows:
        grouped[(str(row["qubit"]), str(row["structure"]))].append(
            {
                "l_jun_nh": float(row["l_jun_nh"]),
                "f_resonance_ghz": float(row["f_resonance_ghz"]),
            }
        )

    qubits = sorted({key[0] for key in grouped}, key=_parse_qubit_sort_key)
    preferred = ["Readout", "XY", "XY + Readout"]
    others = sorted({key[1] for key in grouped if key[1] not in preferred})
    structures = preferred + others

    z_matrix: list[list[float | None]] = []
    meta_matrix: list[list[str]] = []
    for structure in structures:
        z_row: list[float | None] = []
        meta_row: list[str] = []
        for qubit in qubits:
            candidates = grouped.get((qubit, structure), [])
            if not candidates:
                z_row.append(None)
                meta_row.append("-")
                continue
            freq, selected = _select_frequency(candidates, target_l_jun_nh, aggregate)
            z_row.append(freq)
            meta_row.append(selected)
        z_matrix.append(z_row)
        meta_matrix.append(meta_row)

    return qubits, structures, z_matrix, meta_matrix


def _build_heatmap_figure(
    qubits: list[str],
    structures: list[str],
    z_matrix: list[list[float | None]],
    selected_meta: list[list[str]],
    title: str,
) -> go.Figure:
    custom_data = []
    for structure_idx in range(len(structures)):
        custom_data.append(
            [[selected_meta[structure_idx][qubit_idx]] for qubit_idx in range(len(qubits))]
        )

    fig = go.Figure(
        data=[
            go.Heatmap(
                x=qubits,
                y=structures,
                z=z_matrix,
                colorscale="Viridis",
                colorbar={"title": "f_resonance (GHz)"},
                customdata=custom_data,
                hovertemplate=(
                    "Qubit=%{x}<br>"
                    "Structure=%{y}<br>"
                    "f_resonance=%{z:.6g} GHz<br>"
                    "L_jun selector=%{customdata[0]}<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(
        title={"text": title, "x": 0.01},
        template="plotly_white",
        xaxis_title="Qubit",
        yaxis_title="Structure",
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
        height=max(320, 120 + 42 * len(structures)),
    )
    return fig


def _build_table_figure(
    qubits: list[str],
    structures: list[str],
    z_matrix: list[list[float | None]],
    title: str,
) -> go.Figure:
    headers = ["Qubit", *structures]
    columns: list[list[str]] = [[qubit for qubit in qubits]]
    for structure_idx in range(len(structures)):
        columns.append(
            [
                f"{z_matrix[structure_idx][qubit_idx]:.12g}"
                if z_matrix[structure_idx][qubit_idx] is not None
                else "-"
                for qubit_idx in range(len(qubits))
            ]
        )

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
        height=max(300, 90 + 30 * len(qubits)),
    )
    return fig


@app.command("resonance-map")
def main(
    dataset: Annotated[
        list[str] | None,
        typer.Option(
            "--dataset",
            "-d",
            help="Dataset filter by ID or name. Repeat option to include multiple datasets.",
        ),
    ] = None,
    mode: Annotated[str, typer.Option(help="Mode label, e.g. 'Mode 1'.")] = "Mode 1",
    l_jun_nh: Annotated[
        float | None,
        typer.Option(
            "--l-jun-nh",
            help="Target L_jun (nH). Uses nearest point per cell when provided.",
        ),
    ] = None,
    aggregate: Annotated[
        AggregationMode,
        typer.Option(
            "--aggregate",
            case_sensitive=False,
            help="Aggregation rule when --l-jun-nh is not provided.",
        ),
    ] = "first",
    render: Annotated[
        RenderMode,
        typer.Option(
            "--render",
            case_sensitive=False,
            help="Render type: comparison table (default) or 2D heatmap.",
        ),
    ] = "table",
    title: Annotated[
        str,
        typer.Option(
            "--title",
            help="Custom figure title.",
        ),
    ] = "Different Qubit Structure Frequency Comparison Table",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output HTML file path."),
    ] = None,
    png_output: Annotated[
        Path | None,
        typer.Option("--png-output", help="Optional PNG output path (requires kaleido)."),
    ] = None,
    show: Annotated[
        bool,
        typer.Option("--show/--no-show", help="Open interactive preview in browser."),
    ] = True,
    save_html: Annotated[
        bool,
        typer.Option("--save-html/--no-save-html", help="Save output as HTML file."),
    ] = False,
    mock_on_empty: Annotated[
        bool,
        typer.Option(
            "--mock-on-empty/--no-mock-on-empty",
            help="Use mock data when DB has no matching resonance records.",
        ),
    ] = True,
) -> None:
    """Plot qubit-structure resonance comparison table (or optional heatmap)."""
    rows, missing_filters = _load_rows(dataset or [])
    if missing_filters:
        typer.echo(f"Warning: unknown dataset filters ignored: {', '.join(missing_filters)}")

    used_mock = False
    if not rows and mock_on_empty:
        rows = _mock_rows()
        used_mock = True

    if not rows:
        typer.echo("No resonance rows found. Nothing to render.")
        raise typer.Exit(code=1)

    qubits, structures, z_matrix, selected_meta = _build_matrix(
        rows=rows,
        mode=mode,
        target_l_jun_nh=l_jun_nh,
        aggregate=aggregate,
    )
    if used_mock:
        title = f"{title} (mock data)"
    if l_jun_nh is None:
        title = f"{title} | mode={mode}, aggregate={aggregate}"
    else:
        title = f"{title} | mode={mode}, target L_jun={l_jun_nh:.6g} nH"

    fig = (
        _build_heatmap_figure(qubits, structures, z_matrix, selected_meta, title)
        if render == "heatmap"
        else _build_table_figure(qubits, structures, z_matrix, title)
    )

    if show:
        fig.show()

    if save_html:
        default_output = _default_output_path(f"resonance_map_{render}")
        output_path = output or default_output
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
