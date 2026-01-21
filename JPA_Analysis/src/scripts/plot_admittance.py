from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, NamedTuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore

from src.preprocess.loader import (
    dataset_to_dataframe,
    find_dataset,
    load_component_record,
)
from src.preprocess.schema import ParameterFamily, ParameterRepresentation
from src.utils import (
    MATPLOTLIB_FONT_SIZE,
    MATPLOTLIB_TITLE_SIZE,
    PLOTLY_FONT_SIZE,
    PREPROCESSED_DATA_DIR,
    apply_plotly_layout,
    plotly_default_config,
)

PlotMode = Literal["lines", "heatmap", "both"]

DEFAULT_COMPONENT_IDS: Sequence[str] = [
    "LJPAL6572_B46D1",
    "LJPAL6572_B46D2",
    "LJPAL6574_B46D1",
]


class PlotAdmittanceArgs(NamedTuple):
    components: list[str]
    mode: PlotMode
    show_zeros: bool
    freq_min: float | None
    freq_max: float | None
    matplotlib: bool
    title: str


def parse_args() -> PlotAdmittanceArgs:
    parser = argparse.ArgumentParser(
        description="Plot admittance (Im(Y)) data from preprocessed component records."
    )
    parser.add_argument(
        "components",
        nargs="*",
        help="Component IDs from data/preprocessed/ (e.g., LJPAL6572_B46D1).",
    )
    parser.add_argument(
        "--mode",
        choices=["lines", "heatmap", "both"],
        default="both",
        help="Visualization mode: lines (L_jun slices), heatmap, or both.",
    )
    parser.add_argument(
        "--show-zeros",
        action="store_true",
        help="Mark zero-crossing points (resonances) on the plot.",
    )
    parser.add_argument(
        "--freq-min",
        type=float,
        default=None,
        help="Minimum frequency (GHz) to display.",
    )
    parser.add_argument(
        "--freq-max",
        type=float,
        default=None,
        help="Maximum frequency (GHz) to display.",
    )
    parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Use Matplotlib instead of Plotly for rendering.",
    )
    parser.add_argument(
        "--title",
        default="Admittance (Im(Y)) Analysis",
        help="Custom plot title.",
    )
    args = parser.parse_args()

    component_list = list(args.components) if args.components else list(DEFAULT_COMPONENT_IDS)

    return PlotAdmittanceArgs(
        components=component_list,
        mode=args.mode,
        show_zeros=args.show_zeros,
        freq_min=args.freq_min,
        freq_max=args.freq_max,
        matplotlib=args.matplotlib,
        title=args.title,
    )


def resolve_component_path(component_id: str) -> Path | None:
    """Resolve component ID to preprocessed JSON path."""
    path = Path(component_id)
    if path.exists():
        return path

    fallback = PREPROCESSED_DATA_DIR / f"{component_id}.json"
    if fallback.exists():
        return fallback

    print(f"[Warning] Component not found: {component_id}")
    return None


def load_admittance_data(component_path: Path) -> pd.DataFrame | None:
    """Load Im(Y) data from preprocessed component record."""
    try:
        record = load_component_record(component_path)
        dataset = find_dataset(
            record,
            family=ParameterFamily.y_parameters,
            parameter="Y11",
            representation=ParameterRepresentation.imaginary,
        )
        if dataset is None:
            print(f"[Warning] No Im(Y11) dataset found in {component_path.stem}")
            return None

        df = dataset_to_dataframe(dataset, value_label="ImY")

        # Pivot to wide format: index=Freq, columns=L_jun
        freq_col = [c for c in df.columns if "Freq" in c][0]
        bias_col = [c for c in df.columns if "L_jun" in c][0]

        pivot = df.pivot(index=freq_col, columns=bias_col, values="ImY")
        pivot = pivot.sort_index()
        pivot.columns.name = "L_jun"
        pivot.index.name = "Freq"

        return pivot

    except Exception as exc:
        print(f"[Error] Failed to load {component_path.stem}: {exc}")
        return None


def apply_frequency_window(
    df: pd.DataFrame, freq_min: float | None, freq_max: float | None
) -> pd.DataFrame:
    """Filter dataframe by frequency range."""
    # freq_col = df.index.name or "Freq"
    df_filtered = df.copy()

    if freq_min is not None:
        df_filtered = df_filtered[df_filtered.index >= freq_min]
    if freq_max is not None:
        df_filtered = df_filtered[df_filtered.index <= freq_max]

    return df_filtered


def find_zero_crossings(df: pd.DataFrame) -> pd.DataFrame:
    """Find zero-crossing frequencies for each L_jun column."""
    crossings: list[dict[str, float]] = []

    for col in df.columns:
        freqs = df.index.to_numpy(dtype=float)
        y_vals = df[col].to_numpy(dtype=float)

        for i in range(len(y_vals) - 1):
            if not np.isnan(y_vals[i]) and not np.isnan(y_vals[i + 1]):
                if y_vals[i] * y_vals[i + 1] < 0:  # Sign change
                    # Linear interpolation
                    f_cross = freqs[i] - y_vals[i] * (freqs[i + 1] - freqs[i]) / (
                        y_vals[i + 1] - y_vals[i]
                    )
                    crossings.append({"L_jun": float(col), "Freq": float(f_cross)})

    return pd.DataFrame(crossings) if crossings else pd.DataFrame()


def plot_lines_plotly(df: pd.DataFrame, zeros_df: pd.DataFrame | None, title: str) -> None:
    """Plot Im(Y) vs Freq for each L_jun value (line plot)."""
    fig = go.Figure()

    for col in df.columns:
        series = df[col].dropna()
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=f"L_jun = {float(col):.2f} nH",
                line=dict(width=2),
            )
        )

    # Add zero crossings
    if zeros_df is not None and not zeros_df.empty:
        fig.add_trace(
            go.Scatter(
                x=zeros_df["Freq"],
                y=[0] * len(zeros_df),
                mode="markers",
                name="Resonances",
                marker=dict(color="red", size=8, symbol="x"),
            )
        )

    apply_plotly_layout(
        fig,
        title=title,
        xaxis_title="Frequency [GHz]",
        yaxis_title="Im(Y) []",
        legend_title="L_jun",
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.show(config=plotly_default_config(title))


def plot_heatmap_plotly(df: pd.DataFrame, title: str) -> None:
    """Plot Im(Y) as heatmap (L_jun vs Freq)."""
    fig = go.Figure(
        go.Heatmap(
            x=df.columns,
            y=df.index,
            z=df.values,
            colorscale="RdBu_r",
            zmid=0.0,
            colorbar=dict(title="Im(Y)"),
        )
    )

    apply_plotly_layout(
        fig,
        title=title,
        xaxis_title="L_jun [nH]",
        yaxis_title="Frequency [GHz]",
        legend_title="",
    )
    fig.show(config=plotly_default_config(title))


def plot_both_plotly(df: pd.DataFrame, zeros_df: pd.DataFrame | None, title: str) -> None:
    """Combined view: lines + heatmap."""
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Im(Y) vs Frequency", "Heatmap (L_jun vs Freq)"),
        column_widths=[0.6, 0.4],
    )

    # Left: line plots
    for col in df.columns:
        series = df[col].dropna()
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=f"L={float(col):.2f}nH",
                line=dict(width=1.5),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    if zeros_df is not None and not zeros_df.empty:
        fig.add_trace(
            go.Scatter(
                x=zeros_df["Freq"],
                y=[0] * len(zeros_df),
                mode="markers",
                name="Resonances",
                marker=dict(color="red", size=6, symbol="x"),
            ),
            row=1,
            col=1,
        )

    # Right: heatmap
    fig.add_trace(
        go.Heatmap(
            x=df.columns,
            y=df.index,
            z=df.values,
            colorscale="RdBu_r",
            zmid=0.0,
            colorbar=dict(title="Im(Y)", x=1.15),
            showscale=True,
        ),
        row=1,
        col=2,
    )

    fig.update_xaxes(title_text="Frequency [GHz]", row=1, col=1)
    fig.update_yaxes(title_text="Im(Y) []", row=1, col=1)
    fig.update_xaxes(title_text="L_jun [nH]", row=1, col=2)
    fig.update_yaxes(title_text="Frequency [GHz]", row=1, col=2)

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3, row=1, col=1)  # type: ignore

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=PLOTLY_FONT_SIZE + 4)),
        font=dict(size=PLOTLY_FONT_SIZE - 2),
        height=600,
    )
    fig.show(config=plotly_default_config(title))


def plot_lines_matplotlib(df: pd.DataFrame, zeros_df: pd.DataFrame | None, title: str) -> None:
    """Matplotlib version of line plot."""
    plt.figure(figsize=(10, 6))

    for col in df.columns:
        series = df[col].dropna()
        plt.plot(series.index, series.values, label=f"L_jun = {float(col):.2f} nH", linewidth=2)  # type: ignore

    if zeros_df is not None and not zeros_df.empty:
        plt.scatter(
            zeros_df["Freq"],
            [0] * len(zeros_df),
            color="red",
            marker="x",
            s=100,
            zorder=5,
            label="Resonances",
        )

    plt.axhline(0, linestyle="--", color="gray", alpha=0.5)
    plt.xlabel("Frequency [GHz]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.ylabel("Im(Y) []", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.title(title, fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.legend(fontsize=MATPLOTLIB_FONT_SIZE - 2)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_heatmap_matplotlib(df: pd.DataFrame, title: str) -> None:
    """Matplotlib version of heatmap."""
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(
        df.columns,
        df.index,
        df.values,
        shading="auto",
        cmap="RdBu_r",
        vmin=-np.abs(df.values).max(),
        vmax=np.abs(df.values).max(),
    )
    plt.colorbar(label="Im(Y) []")
    plt.xlabel("L_jun [nH]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.ylabel("Frequency [GHz]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.title(title, fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.tight_layout()
    plt.show()


def run() -> None:
    args = parse_args()

    # Process each component
    for component_id in args.components:
        print(f"\n=== Processing {component_id} ===")

        component_path = resolve_component_path(component_id)
        if component_path is None:
            continue

        df = load_admittance_data(component_path)
        if df is None or df.empty:
            continue

        df = apply_frequency_window(df, args.freq_min, args.freq_max)

        zeros_df = None
        if args.show_zeros:
            zeros_df = find_zero_crossings(df)
            print(f"Found {len(zeros_df)} zero crossings")

        plot_title = f"{args.title} - {component_id}"

        if args.matplotlib:
            if args.mode == "lines":
                plot_lines_matplotlib(df, zeros_df, plot_title)
            elif args.mode == "heatmap":
                plot_heatmap_matplotlib(df, plot_title)
            else:  # both
                plot_lines_matplotlib(df, zeros_df, plot_title)
                plot_heatmap_matplotlib(df, plot_title)
        else:
            if args.mode == "lines":
                plot_lines_plotly(df, zeros_df, plot_title)
            elif args.mode == "heatmap":
                plot_heatmap_plotly(df, plot_title)
            else:  # both
                plot_both_plotly(df, zeros_df, plot_title)


if __name__ == "__main__":
    run()
