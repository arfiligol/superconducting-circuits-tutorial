from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go  # type: ignore

from src.utils import (
    MATPLOTLIB_FONT_SIZE,
    MATPLOTLIB_TITLE_SIZE,
    RAW_LAYOUT_ADMITTANCE_DIR,
    apply_plotly_layout,
    plotly_default_config,
)
from src.visualization import print_dataframe_table

DEFAULT_INPUT_FILES: Sequence[str] = [
    "PF6FQ_Q0_Float_No_L_Im_Y11.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Compute the equivalent capacitance per frequency sample assuming Im(Y)=ωC.")
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="CSV files to analyze (defaults to PF6FQ dataset when omitted).",
    )
    parser.add_argument(
        "--freq-min", type=float, default=None, help="Minimum frequency (GHz) to include."
    )
    parser.add_argument(
        "--freq-max", type=float, default=None, help="Maximum frequency (GHz) to include."
    )

    parser.add_argument(
        "--title",
        default="Effective Capacitance Estimates",
        help="Title for plots.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip plotting the C_eff vs frequency curve.",
    )
    parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of the default Plotly view.",
    )
    return parser.parse_args()


def resolve_csv_path(candidate: str) -> Path | None:
    path = Path(candidate)
    if path.exists():
        return path

    fallback = RAW_LAYOUT_ADMITTANCE_DIR / candidate
    if fallback.exists():
        return fallback

    print(f"[Warning] File not found: {candidate}")
    return None


def infer_frequency_scale(column_name: str) -> float:
    lower = column_name.lower()
    if "ghz" in lower:
        return 1e9
    if "mhz" in lower:
        return 1e6
    if "khz" in lower:
        return 1e3
    if "hz" in lower:
        return 1.0
    return 1.0


def extract_columns(df: pd.DataFrame) -> tuple[str, str] | None:
    freq_cols = [col for col in df.columns if "freq" in col.lower()]
    if not freq_cols:
        print("[Error] Frequency column not found.")
        return None
    freq_col = freq_cols[0]

    imag_cols = [col for col in df.columns if "im" in col.lower() and "y" in col.lower()]
    if not imag_cols:
        imag_cols = [col for col in df.columns if "imag" in col.lower()]
    if not imag_cols:
        print("[Error] Imaginary admittance column not found.")
        return None
    imag_col = imag_cols[0]
    return freq_col, imag_col


def apply_frequency_window(
    freq_ghz: np.ndarray,
    imag_y: np.ndarray,
    freq_min: float | None,
    freq_max: float | None,
) -> tuple[np.ndarray, np.ndarray]:
    mask = np.ones_like(freq_ghz, dtype=bool)
    if freq_min is not None:
        mask &= freq_ghz >= freq_min
    if freq_max is not None:
        mask &= freq_ghz <= freq_max
    return freq_ghz[mask], imag_y[mask]


def summarize_samples(freq_ghz: np.ndarray, imag_y: np.ndarray) -> pd.DataFrame:
    omega = 2.0 * np.pi * freq_ghz * 1e9
    with np.errstate(divide="ignore", invalid="ignore"):
        capacitance_pf = np.where(omega > 0.0, imag_y / omega * 1e12, np.nan)
    return pd.DataFrame(
        {
            "Freq_GHz": freq_ghz,
            "ImY": imag_y,
            "C_eff_est_pF": capacitance_pf,
        }
    )


def analyze_file(
    csv_path: Path,
    freq_min: float | None,
    freq_max: float | None,
    show_plot: bool,
    use_matplotlib: bool,
    title: str,
) -> None:
    df = pd.read_csv(csv_path)
    columns = extract_columns(df)
    if columns is None:
        return
    freq_col, imag_col = columns
    scale = infer_frequency_scale(freq_col)
    freq_values = df[freq_col].to_numpy(dtype=float)
    imag_values = df[imag_col].to_numpy(dtype=float)

    freq_ghz = freq_values * (scale / 1e9)
    freq_ghz, imag_values = apply_frequency_window(freq_ghz, imag_values, freq_min, freq_max)

    print(f"\n=== Effective Capacitance Estimates for {csv_path.name} ===")
    table = summarize_samples(freq_ghz, imag_values)
    print_dataframe_table("Per-frequency capacitance estimate", table)
    if show_plot:
        if use_matplotlib:
            plot_capacitance_curve_matplotlib(csv_path.name, table, title)
        else:
            plot_capacitance_curve_plotly(csv_path.name, table, title)


def plot_capacitance_curve_matplotlib(filename: str, table: pd.DataFrame, title: str) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(
        table["Freq_GHz"],
        table["C_eff_est_pF"],
        "o-",
        alpha=0.85,
        label="C_eff estimate",
        linewidth=2,
        markersize=6,
    )
    plt.xlabel("Frequency [GHz]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.ylabel("Equivalent C_eff [pF]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.title(f"{title} - {filename}", fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(fontsize=MATPLOTLIB_FONT_SIZE)
    plt.tight_layout()
    plt.show()


def plot_capacitance_curve_plotly(filename: str, table: pd.DataFrame, title: str) -> None:
    traces = [
        go.Scatter(
            x=table["Freq_GHz"],
            y=table["C_eff_est_pF"],
            mode="lines+markers",
            name="C_eff estimate",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        )
    ]
    fig = go.Figure(data=traces)
    apply_plotly_layout(
        fig,
        title=f"{title} - {filename}",
        xaxis_title="Frequency [GHz]",
        yaxis_title="Equivalent C_eff [pF]",
        legend_title="Legend",
        x_tickformat=".2f",
    )
    fig.show(config=plotly_default_config(title))


def run() -> None:
    args = parse_args()
    file_list = args.files if args.files else DEFAULT_INPUT_FILES
    for candidate in file_list:
        csv_path = resolve_csv_path(candidate)
        if csv_path is None:
            continue
        analyze_file(
            csv_path,
            freq_min=args.freq_min,
            freq_max=args.freq_max,
            show_plot=not args.no_plot,
            use_matplotlib=args.matplotlib,
            title=args.title,
        )


if __name__ == "__main__":
    run()
