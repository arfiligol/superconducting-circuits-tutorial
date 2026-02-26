"""Plot flux-dependence datasets from SQLite records."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal

import numpy as np
import plotly.graph_objects as go
import typer
from plotly.subplots import make_subplots

from core.analysis.application.services.squid_fitting import resolve_dataset
from core.shared.persistence import DataRecord, get_unit_of_work
from core.shared.persistence.database import DATABASE_PATH

app = typer.Typer(add_completion=False, help="Flux dependence plotting commands.")

ViewMode = Literal["amplitude", "phase", "combined", "all"]
PhaseUnit = Literal["rad", "deg"]


def _default_output_path(stem: str) -> Path:
    reports_dir = DATABASE_PATH.parent / "processed" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return reports_dir / f"{stem}_{stamp}.html"


def _find_record(
    records: list[DataRecord],
    parameter: str,
    representation: str,
) -> DataRecord | None:
    target_parameter = parameter.upper()
    target_repr = representation.lower()
    for record in records:
        if len(record.axes) != 2:
            continue
        if record.parameter.upper() != target_parameter:
            continue
        if record.representation.lower() != target_repr:
            continue
        return record
    return None


def _to_matrix(record: DataRecord) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axis_freq, axis_bias = record.axes
    freq = np.asarray(axis_freq.get("values", []), dtype=float)
    bias = np.asarray(axis_bias.get("values", []), dtype=float)
    matrix = np.asarray(record.values, dtype=float)

    if matrix.ndim != 2:
        raise ValueError("Expected a 2D matrix in DataRecord.values.")
    if matrix.shape != (len(freq), len(bias)):
        raise ValueError(
            f"Matrix shape mismatch. values={matrix.shape}, freq={len(freq)}, bias={len(bias)}."
        )
    return freq, bias, matrix


def _wrap_phase(values: np.ndarray, phase_unit: PhaseUnit) -> np.ndarray:
    if phase_unit == "deg":
        return ((values + 180.0) % 360.0) - 180.0
    return ((values + np.pi) % (2.0 * np.pi)) - np.pi


def _phase_axis_label(phase_unit: PhaseUnit) -> str:
    return "Phase (deg)" if phase_unit == "deg" else "Phase (rad)"


def _select_representations(view: ViewMode) -> list[str]:
    if view == "amplitude":
        return ["amplitude"]
    if view == "phase":
        return ["phase"]
    return ["amplitude", "phase"]


def _build_single_heatmap(
    dataset_name: str,
    representation: str,
    freq: np.ndarray,
    bias: np.ndarray,
    matrix: np.ndarray,
    device: str | None,
) -> go.Figure:
    value_label = "Amplitude" if representation == "amplitude" else "Phase"
    title_device = device or dataset_name
    fig = go.Figure(
        data=[
            go.Heatmap(
                x=bias.tolist(),
                y=freq.tolist(),
                z=matrix.tolist(),
                colorscale="Viridis",
                colorbar={"title": value_label},
            )
        ]
    )
    fig.update_layout(
        title=f"{title_device}: {representation.capitalize()} Heatmap",
        template="plotly_white",
        xaxis_title="Bias",
        yaxis_title="Frequency (GHz)",
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
    )
    return fig


def _build_combined_heatmap(
    dataset_name: str,
    freq: np.ndarray,
    bias: np.ndarray,
    amplitude: np.ndarray | None,
    phase: np.ndarray | None,
    device: str | None,
) -> go.Figure:
    traces = []
    titles = []
    if amplitude is not None:
        traces.append(("Amplitude", amplitude))
        titles.append("Amplitude")
    if phase is not None:
        traces.append(("Phase", phase))
        titles.append("Phase")

    figure = make_subplots(rows=1, cols=len(traces), subplot_titles=titles)
    for idx, (label, matrix) in enumerate(traces, start=1):
        figure.add_trace(
            go.Heatmap(
                x=bias.tolist(),
                y=freq.tolist(),
                z=matrix.tolist(),
                colorscale="Viridis",
                colorbar={"title": label},
                showscale=True,
            ),
            row=1,
            col=idx,
        )
        figure.update_xaxes(title_text="Bias", row=1, col=idx)
        figure.update_yaxes(title_text="Frequency (GHz)", row=1, col=idx)

    title_device = device or dataset_name
    figure.update_layout(
        title=f"{title_device}: Flux Dependence",
        template="plotly_white",
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
    )
    return figure


def _build_slice_bias_plot(
    dataset_name: str,
    representation: str,
    freq: np.ndarray,
    bias: np.ndarray,
    matrix: np.ndarray,
    target_bias: float,
    device: str | None,
    phase_unit: PhaseUnit,
) -> go.Figure:
    idx = int(np.argmin(np.abs(bias - target_bias)))
    chosen_bias = float(bias[idx])
    values = matrix[:, idx]
    ylabel = _phase_axis_label(phase_unit) if representation == "phase" else "Amplitude"
    title_device = device or dataset_name
    fig = go.Figure(
        data=[
            go.Scatter(
                x=freq.tolist(),
                y=values.tolist(),
                mode="lines",
                name=f"Bias={chosen_bias:.6g}",
            )
        ]
    )
    fig.update_layout(
        title=f"{title_device}: {representation.capitalize()} Slice @ Bias={chosen_bias:.6g}",
        template="plotly_white",
        xaxis_title="Frequency (GHz)",
        yaxis_title=ylabel,
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
    )
    return fig


def _build_slice_freq_plot(
    dataset_name: str,
    representation: str,
    freq: np.ndarray,
    bias: np.ndarray,
    matrix: np.ndarray,
    target_freq: float,
    device: str | None,
    phase_unit: PhaseUnit,
) -> go.Figure:
    idx = int(np.argmin(np.abs(freq - target_freq)))
    chosen_freq = float(freq[idx])
    values = matrix[idx, :]
    ylabel = _phase_axis_label(phase_unit) if representation == "phase" else "Amplitude"
    title_device = device or dataset_name
    fig = go.Figure(
        data=[
            go.Scatter(
                x=bias.tolist(),
                y=values.tolist(),
                mode="lines",
                name=f"Freq={chosen_freq:.6g} GHz",
            )
        ]
    )
    fig.update_layout(
        title=f"{title_device}: {representation.capitalize()} Slice @ Freq={chosen_freq:.6g} GHz",
        template="plotly_white",
        xaxis_title="Bias",
        yaxis_title=ylabel,
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


@app.command("flux-dependence")
def main(
    datasets: Annotated[
        list[str],
        typer.Argument(help="Dataset names or IDs."),
    ],
    parameter: Annotated[
        str,
        typer.Option("--parameter", help="Parameter name (e.g. S11)."),
    ] = "S11",
    view: Annotated[
        ViewMode,
        typer.Option("--view", case_sensitive=False, help="View mode."),
    ] = "all",
    phase_unit: Annotated[
        PhaseUnit,
        typer.Option("--phase-unit", case_sensitive=False, help="Phase unit."),
    ] = "rad",
    wrap_phase: Annotated[
        bool,
        typer.Option("--wrap-phase/--no-wrap-phase", help="Wrap phase to ±pi or ±180°."),
    ] = False,
    slice_frequency: Annotated[
        float | None,
        typer.Option("--slice-frequency", help="Slice at frequency (GHz)."),
    ] = None,
    slice_bias: Annotated[
        float | None,
        typer.Option("--slice-bias", help="Slice at bias."),
    ] = None,
    device: Annotated[
        str | None,
        typer.Option("--device", help="Custom device label in title."),
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
    """Plot flux dependence heatmaps and optional slices from DB records."""
    if not datasets:
        typer.echo("Error: No datasets specified.")
        raise typer.Exit(code=1)

    requested = _select_representations(view)
    with get_unit_of_work() as uow:
        for token in datasets:
            dataset = resolve_dataset(token)
            if dataset is None or dataset.id is None:
                typer.echo(f"Skip: dataset not found ({token}).")
                continue

            records = uow.data_records.list_by_dataset(int(dataset.id))
            amp_record = _find_record(records, parameter, "amplitude")
            phase_record = _find_record(records, parameter, "phase")

            if amp_record is None and phase_record is None:
                typer.echo(
                    f"Skip: no amplitude/phase records found for dataset '{dataset.name}' "
                    f"(parameter={parameter})."
                )
                continue

            amp_data = None
            phase_data = None
            if amp_record is not None:
                amp_data = _to_matrix(amp_record)
            if phase_record is not None:
                phase_freq, phase_bias, phase_matrix = _to_matrix(phase_record)
                if phase_unit == "deg":
                    phase_matrix = np.degrees(phase_matrix)
                if wrap_phase:
                    phase_matrix = _wrap_phase(phase_matrix, phase_unit=phase_unit)
                phase_data = (phase_freq, phase_bias, phase_matrix)

            if view in {"combined", "all"}:
                base_data = amp_data or phase_data
                if base_data is None:
                    typer.echo(f"Skip: no plottable records for dataset '{dataset.name}'.")
                    continue
                freq, bias, _ = base_data
                amp_matrix = amp_data[2] if amp_data is not None else None
                phase_matrix = phase_data[2] if phase_data is not None else None
                combined = _build_combined_heatmap(
                    dataset_name=dataset.name,
                    freq=freq,
                    bias=bias,
                    amplitude=amp_matrix,
                    phase=phase_matrix,
                    device=device,
                )
                combined_output = None
                if output is not None and len(datasets) == 1:
                    combined_output = output
                elif output is not None:
                    combined_output = output.with_stem(f"{output.stem}_{dataset.name}_combined")
                _render_figure(
                    combined,
                    show=show,
                    save_html=save_html,
                    output_path=combined_output,
                    default_stem=f"plot_flux_dependence_{dataset.name}_combined",
                )
            else:
                for representation in requested:
                    data = amp_data if representation == "amplitude" else phase_data
                    if data is None:
                        typer.echo(
                            f"Skip: representation '{representation}' missing in dataset "
                            f"'{dataset.name}'."
                        )
                        continue
                    freq, bias, matrix = data
                    fig = _build_single_heatmap(
                        dataset_name=dataset.name,
                        representation=representation,
                        freq=freq,
                        bias=bias,
                        matrix=matrix,
                        device=device,
                    )
                    rep_output = None
                    if output is not None and len(datasets) == 1:
                        rep_output = output.with_stem(f"{output.stem}_{representation}")
                    elif output is not None:
                        rep_output = output.with_stem(
                            f"{output.stem}_{dataset.name}_{representation}"
                        )
                    _render_figure(
                        fig,
                        show=show,
                        save_html=save_html,
                        output_path=rep_output,
                        default_stem=f"plot_flux_dependence_{dataset.name}_{representation}",
                    )

            # Slices
            for representation, data in [("amplitude", amp_data), ("phase", phase_data)]:
                if data is None:
                    continue
                freq, bias, matrix = data
                if slice_frequency is not None:
                    slice_fig = _build_slice_freq_plot(
                        dataset_name=dataset.name,
                        representation=representation,
                        freq=freq,
                        bias=bias,
                        matrix=matrix,
                        target_freq=slice_frequency,
                        device=device,
                        phase_unit=phase_unit,
                    )
                    _render_figure(
                        slice_fig,
                        show=show,
                        save_html=save_html,
                        output_path=None
                        if output is None
                        else output.with_stem(
                            f"{output.stem}_{dataset.name}_{representation}_slice_freq"
                        ),
                        default_stem=f"plot_flux_dependence_{dataset.name}_{representation}_slice_freq",
                    )
                if slice_bias is not None:
                    slice_fig = _build_slice_bias_plot(
                        dataset_name=dataset.name,
                        representation=representation,
                        freq=freq,
                        bias=bias,
                        matrix=matrix,
                        target_bias=slice_bias,
                        device=device,
                        phase_unit=phase_unit,
                    )
                    _render_figure(
                        slice_fig,
                        show=show,
                        save_html=save_html,
                        output_path=None
                        if output is None
                        else output.with_stem(
                            f"{output.stem}_{dataset.name}_{representation}_slice_bias"
                        ),
                        default_stem=f"plot_flux_dependence_{dataset.name}_{representation}_slice_bias",
                    )


if __name__ == "__main__":
    app()
