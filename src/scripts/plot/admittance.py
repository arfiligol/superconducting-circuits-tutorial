"""Plot admittance datasets from SQLite records."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated

import numpy as np
import plotly.graph_objects as go
import typer

from core.analysis.application.services.squid_fitting import resolve_dataset
from core.shared.persistence import DataRecord, get_unit_of_work
from core.shared.persistence.database import DATABASE_PATH

app = typer.Typer(add_completion=False, help="Admittance plotting commands.")


def _default_output_path(stem: str) -> Path:
    reports_dir = DATABASE_PATH.parent / "processed" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return reports_dir / f"{stem}_{stamp}.html"


def _find_admittance_record(records: list[DataRecord], parameter: str) -> DataRecord | None:
    target_parameter = parameter.upper()
    for record in records:
        if len(record.axes) != 2:
            continue
        if record.representation.lower() != "imaginary":
            continue
        if record.parameter.upper() != target_parameter:
            continue
        if "y" not in record.data_type.lower():
            continue
        return record
    return None


def _to_matrix(record: DataRecord) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axis_freq, axis_l_jun = record.axes
    freq = np.asarray(axis_freq.get("values", []), dtype=float)
    l_jun = np.asarray(axis_l_jun.get("values", []), dtype=float)
    matrix = np.asarray(record.values, dtype=float)

    if matrix.ndim != 2:
        raise ValueError("Expected a 2D matrix in DataRecord.values.")
    if matrix.shape != (len(freq), len(l_jun)):
        raise ValueError(
            f"Matrix shape mismatch. values={matrix.shape}, freq={len(freq)}, l_jun={len(l_jun)}."
        )
    return freq, l_jun, matrix


def _filter_frequency_window(
    freq: np.ndarray,
    matrix: np.ndarray,
    freq_min: float | None,
    freq_max: float | None,
) -> tuple[np.ndarray, np.ndarray]:
    mask = np.ones(len(freq), dtype=bool)
    if freq_min is not None:
        mask &= freq >= freq_min
    if freq_max is not None:
        mask &= freq <= freq_max
    filtered_freq = freq[mask]
    filtered_matrix = matrix[mask, :]
    if filtered_freq.size == 0:
        raise ValueError("No points remain after applying frequency window.")
    return filtered_freq, filtered_matrix


def _zero_crossings(
    freq: np.ndarray,
    matrix: np.ndarray,
    l_jun: np.ndarray,
) -> tuple[list[float], list[float]]:
    marker_x: list[float] = []
    marker_y: list[float] = []
    for col_idx, l_value in enumerate(l_jun):
        ys = matrix[:, col_idx]
        for idx in range(len(ys) - 1):
            y1, y2 = float(ys[idx]), float(ys[idx + 1])
            f1, f2 = float(freq[idx]), float(freq[idx + 1])
            if y1 == 0.0:
                marker_x.append(float(l_value))
                marker_y.append(f1)
                continue
            if y1 * y2 < 0.0:
                denom = y2 - y1
                f_cross = f1 if denom == 0 else f1 - y1 * (f2 - f1) / denom
                marker_x.append(float(l_value))
                marker_y.append(float(f_cross))
    return marker_x, marker_y


def _build_lines(
    dataset_name: str,
    freq: np.ndarray,
    l_jun: np.ndarray,
    matrix: np.ndarray,
    show_zeros: bool,
    title: str | None,
) -> go.Figure:
    fig = go.Figure()
    max_lines = 20
    if len(l_jun) <= max_lines:
        selected_indices = list(range(len(l_jun)))
    else:
        selected_indices = sorted({int(i) for i in np.linspace(0, len(l_jun) - 1, max_lines)})

    for col_idx in selected_indices:
        l_value = l_jun[col_idx]
        fig.add_trace(
            go.Scatter(
                x=freq.tolist(),
                y=matrix[:, col_idx].tolist(),
                mode="lines",
                name=f"L_jun={l_value:.6g} nH",
            )
        )

    fig.add_hline(y=0.0, line_dash="dash", line_color="#666")

    if show_zeros:
        _, marker_y = _zero_crossings(freq, matrix, l_jun)
        fig.add_trace(
            go.Scatter(
                x=marker_y,
                y=[0.0] * len(marker_y),
                mode="markers",
                marker={"symbol": "x", "size": 7, "color": "#ff4d4f"},
                name="Im(Y)=0",
            )
        )

    fig.update_layout(
        title=title or f"{dataset_name}: Admittance Lines",
        template="plotly_white",
        xaxis_title="Frequency (GHz)",
        yaxis_title="Im(Y)",
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
    )
    return fig


def _render_figure(
    fig: go.Figure,
    show: bool,
    save_html: bool,
    output_path: Path | None,
    default_stem: str,
) -> None:
    if show:
        fig.show()

    if save_html:
        output = output_path or _default_output_path(default_stem)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output), include_plotlyjs="cdn")
        typer.echo(f"HTML written: {output.resolve()}")


@app.command("admittance")
def main(
    datasets: Annotated[
        list[str],
        typer.Argument(help="Dataset names or IDs."),
    ],
    parameter: Annotated[
        str,
        typer.Option("--parameter", help="Admittance parameter to plot."),
    ] = "Y11",
    show_zeros: Annotated[
        bool,
        typer.Option("--show-zeros/--no-show-zeros", help="Mark Im(Y)=0 crossings."),
    ] = False,
    freq_min: Annotated[
        float | None,
        typer.Option("--freq-min", help="Minimum frequency (GHz)."),
    ] = None,
    freq_max: Annotated[
        float | None,
        typer.Option("--freq-max", help="Maximum frequency (GHz)."),
    ] = None,
    title: Annotated[
        str | None,
        typer.Option("--title", help="Custom figure title."),
    ] = None,
    show: Annotated[
        bool,
        typer.Option("--show/--no-show", help="Open interactive preview in browser."),
    ] = True,
    save_html: Annotated[
        bool,
        typer.Option("--save-html/--no-save-html", help="Save output as HTML."),
    ] = False,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output HTML path."),
    ] = None,
) -> None:
    """Plot Im(Y) records as line views."""
    if not datasets:
        typer.echo("Error: No datasets specified.")
        raise typer.Exit(code=1)

    with get_unit_of_work() as uow:
        for token in datasets:
            dataset = resolve_dataset(token)
            if dataset is None or dataset.id is None:
                typer.echo(f"Skip: dataset not found ({token}).")
                continue

            records = uow.data_records.list_by_dataset(int(dataset.id))
            record = _find_admittance_record(records, parameter)
            if record is None:
                typer.echo(
                    f"Skip: Y imaginary record not found for dataset '{dataset.name}' "
                    f"(parameter={parameter})."
                )
                continue

            try:
                freq, l_jun, matrix = _to_matrix(record)
                freq, matrix = _filter_frequency_window(freq, matrix, freq_min, freq_max)
            except Exception as exc:
                typer.echo(f"Skip: invalid data in dataset '{dataset.name}': {exc}")
                continue

            lines = _build_lines(dataset.name, freq, l_jun, matrix, show_zeros, title)
            lines_output = None
            if output is not None and len(datasets) == 1:
                lines_output = output
            elif output is not None:
                lines_output = output.with_stem(f"{output.stem}_{dataset.name}_lines")
            _render_figure(
                lines,
                show=show,
                save_html=save_html,
                output_path=lines_output,
                default_stem=f"plot_admittance_{dataset.name}_lines",
            )


if __name__ == "__main__":
    app()
