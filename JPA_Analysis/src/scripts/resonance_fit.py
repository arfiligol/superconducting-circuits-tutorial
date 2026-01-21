from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go  # type: ignore

from src.utils import (
    PROCESSED_REPORTS_DIR,
    RAW_LAYOUT_ADMITTANCE_DIR,
    apply_plotly_layout,
    plotly_default_config,
)


class ModeEntry(TypedDict):
    L_jun: float
    Modes: list[float]


@dataclass
class FitParameters:
    capacitance_F: float
    ls1_h: float
    ls2_h: float
    l_sum_h: float


FILES_TO_ANALYZE: dict[str, str] = {
    "v3_with_pump": "LJPAL658_v3_Im_Y11.csv",
    "v2_im_y11": "LJPAL658_v2_Im_Y11.csv",
}

MODE1_THRESHOLD_GHZ = 12.0
MODE2_WINDOW_GHZ = (12.0, 14.5)
PLOTS_DIR: Path = PROCESSED_REPORTS_DIR / "resonance_fits"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_and_standardize(name: str, filename: str) -> pd.DataFrame | None:
    csv_path = RAW_LAYOUT_ADMITTANCE_DIR / filename
    if not csv_path.exists():
        print(f"[Warning] {name}: file not found ({csv_path})")
        return None
    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        print(f"[Warning] {name}: failed to read CSV ({exc})")
        return None

    col_map: dict[str, str] = {}

    for col in df.columns:
        lower = col.lower()
        if "l_jun" in lower:
            col_map[col] = "L_jun"
        elif "freq" in lower:
            col_map[col] = "Freq_GHz"
        elif "im(" in lower or "imy" in lower or "im y" in lower or "im" in lower:
            col_map[col] = "ImY"

    if {"L_jun", "Freq_GHz", "ImY"} - set(col_map.values()):
        print(f"[Warning] {name}: missing required columns after standardization")
        return None

    standardized = df.rename(columns=col_map)[["L_jun", "Freq_GHz", "ImY"]]
    standardized = standardized.dropna()
    return standardized


def extract_modes(df: pd.DataFrame) -> list[ModeEntry]:
    mode_entries: list[ModeEntry] = []

    for l_val in sorted(df["L_jun"].unique()):
        subset = df[df["L_jun"] == l_val].sort_values("Freq_GHz")
        freqs = subset["Freq_GHz"].to_numpy(dtype=float)
        admittance = subset["ImY"].to_numpy(dtype=float)

        crossings: list[float] = []

        for idx in range(len(freqs) - 1):
            y1 = admittance[idx]
            y2 = admittance[idx + 1]
            if y1 < 0.0 and y2 > 0.0:
                delta = y2 - y1
                freq_cross = freqs[idx] - y1 * (freqs[idx + 1] - freqs[idx]) / delta
                crossings.append(freq_cross)

        mode_entries.append({"L_jun": float(l_val), "Modes": sorted(crossings)})
    return mode_entries


def clean_modes(modes: Sequence[ModeEntry]) -> pd.DataFrame:
    rows = {"L_jun": [], "Mode1": [], "Mode2": []}
    for entry in modes:
        l_val = entry["L_jun"]
        mode1 = np.nan
        mode2_values: list[float] = []

        for freq in entry["Modes"]:
            if freq < MODE1_THRESHOLD_GHZ:
                if np.isnan(mode1):
                    mode1 = freq
            elif MODE2_WINDOW_GHZ[0] <= freq <= MODE2_WINDOW_GHZ[1]:
                mode2_values.append(freq)

        rows["L_jun"].append(l_val)
        rows["Mode1"].append(mode1)
        rows["Mode2"].append(float(np.mean(mode2_values)) if mode2_values else np.nan)

    return pd.DataFrame(rows)


def fit_parameters(df_modes: pd.DataFrame) -> FitParameters | None:
    valid = df_modes.dropna(subset=["Mode1"])
    if len(valid) < 2:
        return None

    freq_mode1 = valid["Mode1"].to_numpy(dtype=float) * 1e9
    inductance = valid["L_jun"].to_numpy(dtype=float) * 1e-9
    y_values = 1.0 / (2.0 * np.pi * freq_mode1) ** 2

    slope, intercept = np.polyfit(inductance, y_values, 1)
    capacitance = slope
    l_sum = intercept / slope

    valid_m2 = df_modes.dropna(subset=["Mode2"])
    if valid_m2.empty:
        ls1 = 0.0
    else:
        freq_avg = valid_m2["Mode2"].mean() * 1e9
        omega2 = 2.0 * np.pi * freq_avg
        ls1 = 1.0 / (omega2**2 * capacitance)

    ls2 = l_sum - ls1
    return FitParameters(
        capacitance_F=float(capacitance),
        ls1_h=float(ls1),
        ls2_h=float(ls2),
        l_sum_h=float(l_sum),
    )


def plot_dataset(
    name: str,
    raw_modes: Sequence[ModeEntry],
    df_modes: pd.DataFrame,
    params: FitParameters | None,
    use_matplotlib: bool,
) -> None:
    if use_matplotlib:
        _plot_dataset_matplotlib(name, raw_modes, df_modes, params)
    else:
        _plot_dataset_plotly(name, raw_modes, df_modes, params)


def _plot_dataset_matplotlib(
    name: str,
    raw_modes: Sequence[ModeEntry],
    df_modes: pd.DataFrame,
    params: FitParameters | None,
) -> None:
    plt.figure(figsize=(10, 8))

    plt.scatter(
        df_modes["L_jun"],
        df_modes["Mode1"],
        color="tab:blue",
        label="Mode 1 (JPA)",
        s=60,
        zorder=3,
    )
    plt.scatter(
        df_modes["L_jun"],
        df_modes["Mode2"],
        color="tab:red",
        label="Mode 2 (SRF avg)",
        s=60,
        zorder=3,
    )

    raw_x: list[float] = []
    raw_y: list[float] = []

    for entry in raw_modes:
        for freq in entry["Modes"]:
            if freq > MODE1_THRESHOLD_GHZ:
                raw_x.append(entry["L_jun"])
                raw_y.append(freq)
    if raw_x:
        plt.scatter(
            raw_x,
            raw_y,
            color="tab:red",
            alpha=0.3,
            s=15,
            label="Raw mode splitting",
            zorder=2,
        )

    if params:
        l_values = np.linspace(df_modes["L_jun"].min(), df_modes["L_jun"].max(), 200)
        l_h = l_values * 1e-9
        omega_curve1 = 1.0 / np.sqrt(params.capacitance_F * (l_h + params.l_sum_h))
        freq_curve1 = omega_curve1 / (2.0 * np.pi) * 1e-9
        plt.plot(l_values, freq_curve1, "b--", linewidth=2, label="Fit: LC mode")

        if params.ls1_h > 0.0:
            omega_curve2 = 1.0 / np.sqrt(params.capacitance_F * params.ls1_h)
            freq_curve2 = omega_curve2 / (2.0 * np.pi) * 1e-9
            plt.axhline(
                freq_curve2,
                color="tab:red",
                linestyle="--",
                linewidth=2,
                label=f"Fit: SRF ({freq_curve2:.2f} GHz)",
            )

        text_lines = [
            f"Dataset: {name}",
            f"C_static = {params.capacitance_F * 1e12:.3f} pF",
            f"L_s1 = {params.ls1_h * 1e9:.3f} nH",
            f"L_s2 = {params.ls2_h * 1e9:.3f} nH",
            f"L_sum = {params.l_sum_h * 1e9:.3f} nH",
        ]
        plt.gca().text(
            0.55,
            0.70,
            "\n".join(text_lines),
            transform=plt.gca().transAxes,
            fontsize=12,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    plt.title(f"Resonance Modes & Fitting: {name}", fontsize=16)
    plt.xlabel("Junction Inductance $L_{jun}$ [nH]", fontsize=14)
    plt.ylabel("Frequency [GHz]", fontsize=14)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=12, loc="lower left")
    plt.ylim(2, 15)

    output_path = PLOTS_DIR / f"squid_jpa_fit_{name}.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  > Plot saved to {output_path}")


def _plot_dataset_plotly(
    name: str,
    raw_modes: Sequence[ModeEntry],
    df_modes: pd.DataFrame,
    params: FitParameters | None,
) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_modes["L_jun"],
            y=df_modes["Mode1"],
            mode="markers",
            name="Mode 1 (JPA)",
            marker=dict(color="rgb(31,119,180)", size=10),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_modes["L_jun"],
            y=df_modes["Mode2"],
            mode="markers",
            name="Mode 2 (SRF avg)",
            marker=dict(color="rgb(214,39,40)", size=10),
        )
    )
    raw_x: list[float] = []
    raw_y: list[float] = []

    for entry in raw_modes:
        for freq in entry["Modes"]:
            if freq > MODE1_THRESHOLD_GHZ:
                raw_x.append(entry["L_jun"])
                raw_y.append(freq)
    if raw_x:
        fig.add_trace(
            go.Scatter(
                x=raw_x,
                y=raw_y,
                mode="markers",
                name="Raw mode splitting",
                marker=dict(color="rgba(214,39,40,0.4)", size=6),
            )
        )
    annotations: list[dict[str, object]] = []

    if params:
        l_values = np.linspace(df_modes["L_jun"].min(), df_modes["L_jun"].max(), 200)
        l_h = l_values * 1e-9
        omega_curve1 = 1.0 / np.sqrt(params.capacitance_F * (l_h + params.l_sum_h))
        freq_curve1 = omega_curve1 / (2.0 * np.pi) * 1e-9
        fig.add_trace(
            go.Scatter(
                x=l_values,
                y=freq_curve1,
                mode="lines",
                name="Fit: LC mode",
                line=dict(color="rgb(31,119,180)", dash="dash"),
            )
        )
        if params.ls1_h > 0.0:
            omega_curve2 = 1.0 / np.sqrt(params.capacitance_F * params.ls1_h)
            freq_curve2 = omega_curve2 / (2.0 * np.pi) * 1e-9
            fig.add_trace(
                go.Scatter(
                    x=[df_modes["L_jun"].min(), df_modes["L_jun"].max()],
                    y=[freq_curve2, freq_curve2],
                    mode="lines",
                    name=f"Fit: SRF ({freq_curve2:.2f} GHz)",
                    line=dict(color="rgb(214,39,40)", dash="dash"),
                )
            )
        annotations.append(
            dict(
                x=0.6,
                y=0.25,
                text="<br>".join(
                    [
                        f"C_static = {params.capacitance_F * 1e12:.3f} pF",
                        f"L_s1 = {params.ls1_h * 1e9:.3f} nH",
                        f"L_s2 = {params.ls2_h * 1e9:.3f} nH",
                        f"L_sum = {params.l_sum_h * 1e9:.3f} nH",
                    ]
                ),
                showarrow=False,
                xref="paper",
                yref="paper",
                align="left",
                bgcolor="rgba(255,255,224,0.7)",
                font=dict(size=12),
            )
        )
    apply_plotly_layout(
        fig,
        title=f"Resonance Modes & Fitting: {name}",
        xaxis_title="Junction Inductance L_jun [nH]",
        yaxis_title="Frequency [GHz]",
        legend_title="Datasets",
    )
    fig.update_layout(yaxis=dict(range=[2, 15]), annotations=annotations)
    fig.show(config=plotly_default_config(name))
    output_path = PLOTS_DIR / f"squid_jpa_fit_{name}.html"
    fig.write_html(str(output_path))
    print(f"  > Interactive plot saved to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resonance fitting and visualization.")
    parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of Plotly.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip rendering plots (still prints tables/parameters).",
    )
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    print("=== SQUID JPA Resonance Fitting ===")
    for name, filename in FILES_TO_ANALYZE.items():
        df = load_and_standardize(name, filename)
        if df is None:
            continue

        raw_modes = extract_modes(df)
        df_modes = clean_modes(raw_modes)
        params = fit_parameters(df_modes)
        print(df_modes.to_string(index=False))
        if params:
            print(
                f"  > Fit parameters (dataset={name}): "
                f"C={params.capacitance_F * 1e12:.3f} pF, "
                f"L_s1={params.ls1_h * 1e9:.3f} nH, "
                f"L_s2={params.ls2_h * 1e9:.3f} nH"
            )
        else:
            print(f"  > Dataset {name}: insufficient points to fit Mode 1")
        if not args.no_plot:
            plot_dataset(name, raw_modes, df_modes, params, use_matplotlib=args.matplotlib)


if __name__ == "__main__":
    run()
