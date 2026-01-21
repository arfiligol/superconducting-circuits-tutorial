from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go  # type: ignore

from src.utils import (
    MATPLOTLIB_FONT_SIZE,
    MATPLOTLIB_TITLE_SIZE,
    RAW_LAYOUT_PHASE_DIR,
    apply_plotly_layout,
    plotly_default_config,
)

CsvPath = str | Path


def calculate_Q_from_phase(
    csv_file_path: CsvPath,
    freq_range_ghz: tuple[float, float] = (2.0, 6.5),
) -> pd.DataFrame | None:
    """
    從 S11 相位數據中計算 Q 值 (針對過耦合/全反射的共振器)。
    使用公式: Q = (omega0 * group_delay) / 4

    Args:
        csv_file_path (str): 包含 S11 相位數據的 CSV 檔案路徑。
        freq_range_ghz (tuple): 關注的頻率範圍 (min, max), 預設為 2-6.5 GHz (低頻 Mode)。

    Returns:
        Optional[pd.DataFrame]: 包含 L_jun, Resonant_Freq, Group_Delay, Q_factor 的結果表;
                                若讀檔失敗或缺欄位則回傳 None。

    """
    try:
        csv_path = Path(csv_file_path)
        df: pd.DataFrame = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[Error] 無法讀取檔案: {e}")
        return None

    # --- 1. 自動識別欄位 ---
    # 尋找 L_jun 欄位
    l_cols = [c for c in df.columns if "L_jun" in c or "L_ind" in c]
    if not l_cols:
        print("[Error] 找不到電感欄位 (L_jun)")
        return None
    l_col = l_cols[0]

    # 尋找 Freq 欄位
    freq_cols = [c for c in df.columns if "Freq" in c]
    if not freq_cols:
        print("[Error] 找不到頻率欄位 (Freq)")
        return None
    freq_col = freq_cols[0]

    # 尋找 Phase 欄位 (通常包含 'deg' 或 'ang')
    # 尋找 Phase 欄位 (通常包含 'deg' 或 'ang')
    phase_cols = [
        c for c in df.columns if "deg" in c.lower() or "ang" in c.lower() or "phase" in c.lower()
    ]

    if not phase_cols:
        print("[Error] 找不到相位欄位 (Phase/Deg)")
        return None
    phase_col = phase_cols[0]

    print(f"正在分析檔案: {csv_file_path}")
    print(f"鎖定頻率範圍: {freq_range_ghz} GHz")

    # --- 2. 數據處理與 Q 值計算 ---
    unique_Ls = sorted(float(value) for value in df[l_col].unique())
    results: list[dict[str, float]] = []

    for l_val in unique_Ls:
        # 篩選特定 L 值與頻率範圍的數據
        subset = df[
            (df[l_col] == l_val)
            & (df[freq_col] >= freq_range_ghz[0])
            & (df[freq_col] <= freq_range_ghz[1])
        ].sort_values(freq_col)

        if subset.empty:
            continue

        freqs = subset[freq_col].to_numpy(dtype=float) * 1e9  # 轉為 Hz
        phase_deg = subset[phase_col].to_numpy(dtype=float)
        phase_rad = np.deg2rad(phase_deg)

        # 計算角頻率 omega
        omega = 2 * np.pi * freqs

        # 計算群延遲 (Group Delay): tau = -d(phi)/d(omega)
        # 使用 numpy 的 gradient 函數進行數值微分
        # 注意: 這裡假設相位隨頻率增加是"下降"的 (180 -> -180), 所以加負號

        group_delay = -np.gradient(phase_rad, omega)

        # 找出群延遲的最大值 (即共振點)
        peak_idx = np.argmax(group_delay)

        tau_max = group_delay[peak_idx]
        f0 = freqs[peak_idx]
        w0 = 2 * np.pi * f0

        # 計算 Q 值
        # 對於直接耦合的並聯 RLC (S11=1), 相位斜率與 Q 的關係為:

        # Q = (w0 * tau_max) / 4
        Q_val = (w0 * tau_max) / 4

        results.append(
            {
                "L_jun": l_val,
                "Resonant_Freq_GHz": f0 / 1e9,
                "Max_Group_Delay_ns": tau_max * 1e9,
                "Q_factor": Q_val,
            }
        )

    return pd.DataFrame(results)


def plot_q_factor(
    df_q: pd.DataFrame,
    title: str,
    use_matplotlib: bool,
) -> None:
    if use_matplotlib:
        plt.figure(figsize=(8, 5))
        plt.plot(
            df_q["L_jun"],
            df_q["Q_factor"],
            "o-",
            color="purple",
            label="Extracted Q",
        )
        plt.xlabel(r"Junction Inductance $L_{jun}$ [nH]", fontsize=MATPLOTLIB_FONT_SIZE)
        plt.ylabel("Quality Factor Q", fontsize=MATPLOTLIB_FONT_SIZE)
        plt.title(title, fontsize=MATPLOTLIB_TITLE_SIZE)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(fontsize=MATPLOTLIB_FONT_SIZE)
        plt.tight_layout()
        plt.show()
    else:
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=df_q["L_jun"],
                    y=df_q["Q_factor"],
                    mode="lines+markers",
                    name="Extracted Q",
                    line=dict(color="#7e2f8e", width=3),
                    marker=dict(size=8),
                )
            ]
        )
        apply_plotly_layout(
            fig,
            title=title,
            xaxis_title="Junction Inductance L_jun [nH]",
            yaxis_title="Quality Factor Q",
            legend_title="Series",
        )
        fig.show(config=plotly_default_config(title))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute Q factors from S11 phase data.")
    parser.add_argument(
        "--file",
        type=Path,
        default=RAW_LAYOUT_PHASE_DIR / "No_Pump_Line_S11_cang_deg.csv",
        help="Phase CSV to analyze (default: No_Pump_Line file).",
    )
    parser.add_argument("--freq-min", type=float, default=1.0, help="Minimum frequency in GHz.")
    parser.add_argument("--freq-max", type=float, default=6.5, help="Maximum frequency in GHz.")
    parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of Plotly.",
    )
    parser.add_argument(
        "--title",
        default="Q Factor vs. Inductance",
        help="Plot title.",
    )
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    df_q = calculate_Q_from_phase(
        csv_file_path=args.file,
        freq_range_ghz=(args.freq_min, args.freq_max),
    )
    if df_q is None or df_q.empty:
        print("未找到符合條件的數據, 請檢查檔案或頻率範圍設定。")
        return

    print("\n=== Q 值分析結果 ===")
    pd.options.display.float_format = "{:,.4f}".format
    print(df_q.to_string(index=False))
    plot_q_factor(df_q, args.title, args.matplotlib)


if __name__ == "__main__":
    run()
