from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go  # type: ignore
from matplotlib.axes import Axes
from plotly.subplots import make_subplots  # type: ignore

from src.utils import (
    MATPLOTLIB_FONT_SIZE,
    MATPLOTLIB_TITLE_SIZE,
    PLOTLY_FONT_SIZE,
    apply_plotly_layout,
    plotly_default_config,
)

FluxView = Literal["amplitude", "phase", "combined"]

_PLOTLY_COLORSETS = {
    "amplitude": "Portland",
    "phase": "Viridis",
}


def render_flux_heatmap(
    dataset_name: str,
    pivot_amp: pd.DataFrame,
    pivot_phase: pd.DataFrame,
    view: FluxView,
    use_matplotlib: bool,
    phase_label: str = "Phase [deg]",
) -> None:
    if use_matplotlib:
        _render_matplotlib(dataset_name, pivot_amp, pivot_phase, view, phase_label)
    else:
        _render_plotly(dataset_name, pivot_amp, pivot_phase, view, phase_label)


def _render_plotly(
    dataset_name: str,
    pivot_amp: pd.DataFrame,
    pivot_phase: pd.DataFrame,
    view: FluxView,
    phase_label: str,
) -> None:
    bias = pivot_amp.columns
    freq = pivot_amp.index

    if view == "combined":
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            subplot_titles=("Amplitude [dB]", "Phase [deg]"),
            vertical_spacing=0.08,
        )
        _ = fig.add_trace(
            go.Heatmap(
                x=bias,
                y=freq,
                z=pivot_amp.values,
                colorbar=dict(title="dB", y=0.85, len=0.4),
                colorscale=_PLOTLY_COLORSETS["amplitude"],
                zsmooth="best",
            ),
            row=1,
            col=1,
        )
        _ = fig.add_trace(
            go.Heatmap(
                x=bias,
                y=freq,
                z=pivot_phase.values,
                colorbar=dict(title=phase_label, y=0.25, len=0.4),
                colorscale=_PLOTLY_COLORSETS["phase"],
                zsmooth="best",
                zmid=0.0,
            ),
            row=2,
            col=1,
        )
        _ = fig.update_xaxes(title_text="Bias Current [mA]", row=2, col=1)
        _ = fig.update_yaxes(title_text="Frequency [GHz]", row=1, col=1)
        _ = fig.update_yaxes(title_text="Frequency [GHz]", row=2, col=1)
        _ = fig.update_layout(font=dict(size=PLOTLY_FONT_SIZE))
        _ = apply_plotly_layout(
            fig,
            title=dataset_name,
            xaxis_title="Bias Current [mA]",
            yaxis_title="Frequency [GHz]",
            legend_title="Datasets",
        )
        fig.show(config=plotly_default_config(f"{dataset_name}-combined"))
        return

    pivot = pivot_amp if view == "amplitude" else pivot_phase
    label = "Amplitude [dB]" if view == "amplitude" else phase_label
    fig = go.Figure(
        go.Heatmap(
            x=bias,
            y=freq,
            z=pivot.values,
            colorbar=dict(title=label.split()[0]),
            colorscale=_PLOTLY_COLORSETS["amplitude" if view == "amplitude" else "phase"],
            zsmooth="best",
            zmid=0.0 if view != "amplitude" else None,
        )
    )
    _ = apply_plotly_layout(
        fig,
        title=dataset_name,
        xaxis_title="Bias Current [mA]",
        yaxis_title="Frequency [GHz]",
        legend_title="Datasets",
    )
    fig.show(config=plotly_default_config(f"{dataset_name}-{view}"))


def _render_matplotlib(
    dataset_name: str,
    pivot_amp: pd.DataFrame,
    pivot_phase: pd.DataFrame,
    view: FluxView,
    phase_label: str,
) -> None:
    bias = pivot_amp.columns.to_numpy(dtype=float)
    freq = pivot_amp.index.to_numpy(dtype=float)
    if view == "combined":
        fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
        _draw_matplotlib_heatmap(
            axes[0],
            bias,
            freq,
            pivot_amp.to_numpy(dtype=float),
            "Amplitude [dB]",
            "coolwarm",
        )
        _draw_matplotlib_heatmap(
            axes[1],
            bias,
            freq,
            pivot_phase.to_numpy(dtype=float),
            phase_label,
            "viridis",
        )
        _ = axes[1].set_xlabel("Bias Current [mA]", fontsize=MATPLOTLIB_FONT_SIZE)
        _ = fig.suptitle(dataset_name, fontsize=MATPLOTLIB_TITLE_SIZE)
        plt.tight_layout()
        plt.show()
        return

    pivot = pivot_amp if view == "amplitude" else pivot_phase
    label = "Amplitude [dB]" if view == "amplitude" else phase_label
    cmap = "coolwarm" if view == "amplitude" else "viridis"
    plt.figure(figsize=(9, 5))
    _draw_matplotlib_heatmap(
        plt.gca(),
        bias,
        freq,
        pivot.to_numpy(dtype=float),
        label,
        cmap,
    )
    _ = plt.xlabel("Bias Current [mA]", fontsize=MATPLOTLIB_FONT_SIZE)
    _ = plt.title(dataset_name, fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.tight_layout()
    plt.show()


def _draw_matplotlib_heatmap(
    ax: Axes,
    bias: np.ndarray,
    freq: np.ndarray,
    values: np.ndarray,
    label: str,
    cmap: str,
) -> None:
    c = ax.pcolormesh(bias, freq, values, shading="auto", cmap=cmap)
    _ = ax.set_ylabel("Frequency [GHz]", fontsize=MATPLOTLIB_FONT_SIZE)
    _ = ax.set_title(label, fontsize=MATPLOTLIB_FONT_SIZE)
    _ = plt.colorbar(c, ax=ax, label=label)


def render_flux_slice(
    title: str,
    x_values: Sequence[float] | np.ndarray,
    amplitude_values: Sequence[float] | np.ndarray,
    phase_values: Sequence[float] | np.ndarray,
    x_axis_label: str,
    phase_label: str,
    use_matplotlib: bool,
) -> None:
    if use_matplotlib:
        _render_slice_matplotlib(
            title,
            x_values,
            amplitude_values,
            phase_values,
            x_axis_label,
            phase_label,
        )
    else:
        _render_slice_plotly(
            title,
            x_values,
            amplitude_values,
            phase_values,
            x_axis_label,
            phase_label,
        )


def _render_slice_plotly(
    title: str,
    x_values: Sequence[float] | np.ndarray,
    amplitude_values: Sequence[float] | np.ndarray,
    phase_values: Sequence[float] | np.ndarray,
    x_axis_label: str,
    phase_label: str,
) -> None:
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
    _ = fig.add_trace(
        go.Scatter(
            x=list(x_values),
            y=list(amplitude_values),
            mode="lines",
            name="Amplitude [dB]",
            line=dict(color="#1f77b4", width=3),
        ),
        row=1,
        col=1,
        secondary_y=False,
    )
    _ = fig.add_trace(
        go.Scatter(
            x=list(x_values),
            y=list(phase_values),
            mode="lines",
            name=phase_label,
            line=dict(color="#d62728", width=2, dash="dot"),
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    _ = fig.update_xaxes(title_text=x_axis_label)
    _ = fig.update_yaxes(title_text="Amplitude [dB]", secondary_y=False)
    _ = fig.update_yaxes(title_text=phase_label, secondary_y=True)
    _ = apply_plotly_layout(
        fig,
        title=title,
        xaxis_title=x_axis_label,
        yaxis_title="Amplitude [dB]",
        legend_title="Series",
    )
    fig.show(config=plotly_default_config(title))


def _render_slice_matplotlib(
    title: str,
    x_values: Sequence[float] | np.ndarray,
    amplitude_values: Sequence[float] | np.ndarray,
    phase_values: Sequence[float] | np.ndarray,
    x_axis_label: str,
    phase_label: str,
) -> None:
    fig, ax1 = plt.subplots(figsize=(8, 5))
    _ = ax1.plot(
        x_values,
        amplitude_values,
        color="#1f77b4",
        linewidth=2.5,
        label="Amplitude [dB]",
    )
    _ = ax1.set_xlabel(x_axis_label, fontsize=MATPLOTLIB_FONT_SIZE)
    _ = ax1.set_ylabel("Amplitude [dB]", fontsize=MATPLOTLIB_FONT_SIZE, color="#1f77b4")
    _ = ax1.tick_params(axis="y", labelcolor="#1f77b4")
    _ = ax1.grid(True, linestyle="--", alpha=0.4)

    ax2 = ax1.twinx()
    _ = ax2.plot(
        x_values,
        phase_values,
        color="#d62728",
        linewidth=2,
        linestyle="dotted",
        label=phase_label,
    )
    _ = ax2.set_ylabel(phase_label, fontsize=MATPLOTLIB_FONT_SIZE, color="#d62728")
    _ = ax2.tick_params(axis="y", labelcolor="#d62728")

    _ = fig.suptitle(title, fontsize=MATPLOTLIB_TITLE_SIZE)
    fig.tight_layout()
    plt.show()
