from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go  # type: ignore

from src.extraction import extract_from_admittance
from src.utils import (
    MATPLOTLIB_FONT_SIZE,
    MATPLOTLIB_TITLE_SIZE,
    RAW_LAYOUT_ADMITTANCE_DIR,
    apply_plotly_layout,
    plotly_default_config,
)


class ComparisonFileConfigRequired(TypedDict):
    path: Path
    label: str


class ComparisonFileConfig(ComparisonFileConfigRequired, total=False):
    color: str
    marker: str
    linestyle: str


DEFAULT_FILES: list[ComparisonFileConfig] = [
    {
        "path": RAW_LAYOUT_ADMITTANCE_DIR / "LJPAL658_v3_Admittance_Imaginary_Part.csv",
        "label": "With Pump Line",
        "color": "tab:red",
        "marker": "o",
        "linestyle": "-",
    },
    {
        "path": RAW_LAYOUT_ADMITTANCE_DIR
        / "LJPAL658_v3_No_Pump_Line_Admittance_Imaginary_Part.csv",
        "label": "No Pump Line",
        "color": "tab:blue",
        "marker": "s",
        "linestyle": "--",
    },
]


def plot_comparison(
    file_list: Sequence[ComparisonFileConfig],
    title: str = "Resonant Frequency Comparison",
    use_matplotlib: bool = False,
) -> None:
    """
    讀取多個檔案並疊圖比較
    """
    datasets = _load_comparison_data(file_list)
    if use_matplotlib:
        _plot_comparison_matplotlib(datasets, title)
    else:
        _plot_comparison_plotly(datasets, title)


def plot_dual_axis_comparison(
    file_list: Sequence[ComparisonFileConfig],
    title: str = "Dual Axis Comparison",
    use_matplotlib: bool = False,
) -> None:
    """
    雙軸繪圖函數 (Input 格式與 plot_comparison 統一)

    Args:
        file_list (list of dict): 檔案設定列表
            [{'path':..., 'label':..., 'color':...}, ...]
    """

    # 1. 建立畫布與雙軸
    datasets = _load_comparison_data(file_list)
    if use_matplotlib:
        _plot_dual_axis_matplotlib(datasets, title)
    else:
        _plot_dual_axis_plotly(datasets, title)


def _load_comparison_data(
    file_list: Sequence[ComparisonFileConfig],
) -> list[tuple[ComparisonFileConfig, pd.DataFrame | None]]:
    loaded: list[tuple[ComparisonFileConfig, pd.DataFrame | None]] = []

    for file_info in file_list:
        path = file_info["path"]
        label = file_info["label"]
        print(f"正在處理: {label} ({path})...")
        df = extract_from_admittance(path)
        # Ensure df is DataFrame or None
        if not isinstance(df, pd.DataFrame):
            df = None
        loaded.append((file_info, df))
    return loaded


def _plot_comparison_plotly(
    datasets: Sequence[tuple[ComparisonFileConfig, pd.DataFrame | None]],
    title: str,
) -> None:
    fig = go.Figure()
    for file_info, df in datasets:
        if df is None or df.empty:
            continue
        label = file_info["label"]
        if "Mode 1" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["L_jun"],
                    y=df["Mode 1"],
                    mode="lines+markers",
                    name=f"{label} (Mode 1)",
                )
            )
        if "Mode 2" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["L_jun"],
                    y=df["Mode 2"],
                    mode="lines+markers",
                    name=f"{label} (Mode 2)",
                    line=dict(dash="dash"),
                )
            )
    apply_plotly_layout(
        fig,
        title=title,
        xaxis_title="Junction Inductance L_jun [nH]",
        yaxis_title="Frequency [GHz]",
        legend_title="Datasets",
    )
    fig.show(config=plotly_default_config(title))


def _plot_comparison_matplotlib(
    datasets: Sequence[tuple[ComparisonFileConfig, pd.DataFrame | None]],
    title: str,
) -> None:
    plt.figure(figsize=(10, 7))
    for file_info, df in datasets:
        if df is None or df.empty:
            continue
        label = file_info["label"]
        color = file_info.get("color")
        marker = file_info.get("marker", "o")
        style = file_info.get("linestyle", "-")
        if "Mode 1" in df.columns:
            plt.plot(
                df["L_jun"],
                df["Mode 1"],
                label=f"{label} (Mode 1)",
                color=color,
                marker=marker,
                linestyle=style,
                linewidth=2,
            )
        if "Mode 2" in df.columns:
            plt.plot(
                df["L_jun"],
                df["Mode 2"],
                label=f"{label} (Mode 2)",
                color=color,
                marker=marker,
                linestyle="--",
                alpha=0.5,
            )
    plt.title(title, fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.xlabel(r"Junction Inductance $L_{jun}$ [nH]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.ylabel("Frequency [GHz]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.legend(fontsize=MATPLOTLIB_FONT_SIZE - 2)
    plt.tight_layout()
    plt.show()


def _plot_dual_axis_plotly(
    datasets: Sequence[tuple[ComparisonFileConfig, pd.DataFrame | None]],
    title: str,
) -> None:
    fig = go.Figure()
    for file_info, df in datasets:
        if df is None or df.empty:
            continue
        label = file_info["label"]
        if "Mode 1" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["L_jun"],
                    y=df["Mode 1"],
                    mode="lines+markers",
                    name=f"{label} (Mode 1)",
                    yaxis="y1",
                )
            )
        if "Mode 2" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["L_jun"],
                    y=df["Mode 2"],
                    mode="lines+markers",
                    name=f"{label} (Mode 2)",
                    line=dict(dash="dash"),
                    yaxis="y2",
                )
            )
    apply_plotly_layout(
        fig,
        title=title,
        xaxis_title="Junction Inductance L_jun [nH]",
        yaxis_title="Mode 1 Frequency [GHz]",
        legend_title="Datasets",
    )
    fig.update_layout(
        yaxis2=dict(
            title="Mode 2 Frequency [GHz]",
            overlaying="y",
            side="right",
        )
    )
    fig.show(config=plotly_default_config(title))


def _plot_dual_axis_matplotlib(
    datasets: Sequence[tuple[ComparisonFileConfig, pd.DataFrame | None]],
    title: str,
) -> None:
    _, ax1 = plt.subplots(figsize=(12, 7))

    ax2 = ax1.twinx()
    lines = []
    for file_info, df in datasets:
        if df is None or df.empty:
            continue
        label = file_info["label"]
        color = file_info.get("color")
        marker = file_info.get("marker", "o")
        if "Mode 1" in df.columns:
            (l1,) = ax1.plot(
                df["L_jun"],
                df["Mode 1"],
                color=color,
                marker=marker,
                linestyle="-",
                linewidth=2,
                label=f"{label} (Mode 1)",
            )
            lines.append(l1)
        if "Mode 2" in df.columns:
            (l2,) = ax2.plot(
                df["L_jun"],
                df["Mode 2"],
                color=color,
                marker=marker,
                linestyle="--",
                linewidth=2,
                alpha=0.7,
                label=f"{label} (Mode 2)",
            )
            lines.append(l2)
    ax1.set_xlabel(r"Junction Inductance $L_{jun}$ [nH]", fontsize=MATPLOTLIB_FONT_SIZE)
    ax1.set_ylabel("Mode 1 Frequency [GHz] (Solid Line)", fontsize=MATPLOTLIB_FONT_SIZE)
    ax2.set_ylabel("Mode 2 Frequency [GHz] (Dashed Line)", fontsize=MATPLOTLIB_FONT_SIZE)
    ax1.grid(True, linestyle="--", alpha=0.5)
    labels = [line.get_label() for line in lines]
    ax1.legend(
        lines,
        labels,
        loc="center right",
        fontsize=MATPLOTLIB_FONT_SIZE - 2,
        framealpha=0.8,
    )
    plt.title(title, fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare resonant frequencies across multiple admittance files."
    )
    parser.add_argument(
        "--dual-axis",
        action="store_true",
        help="Use the dual-axis comparison plot instead of the single-axis overlay.",
    )
    parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render figures with Matplotlib instead of Plotly.",
    )
    parser.add_argument(
        "--title",
        default="Resonant Frequency Comparison",
        help="Plot title.",
    )
    return parser.parse_args()


# ==========================================
# 使用範例 (Main Block)
# ==========================================
if __name__ == "__main__":
    args = parse_args()
    if args.dual_axis:
        plot_dual_axis_comparison(DEFAULT_FILES, title=args.title, use_matplotlib=args.matplotlib)
    else:
        plot_comparison(DEFAULT_FILES, title=args.title, use_matplotlib=args.matplotlib)
