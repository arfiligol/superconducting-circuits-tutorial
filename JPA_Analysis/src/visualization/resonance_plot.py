from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_resonance_vs_lsquid(
    filename: str,
    df_modes: pd.DataFrame,
    target_modes: Sequence[str] | None = None,
) -> None:
    if "L_jun" not in df_modes.columns:
        return

    mode_cols = [col for col in df_modes.columns if col.startswith("Mode ")]
    if target_modes:
        mode_cols = [col for col in mode_cols if col in target_modes]
    if not mode_cols:
        return

    l_squid = df_modes["L_jun"].to_numpy(dtype=float) / 2.0

    _ = plt.figure(figsize=(10, 6))
    for mode in mode_cols:
        freq_values = df_modes[mode].to_numpy(dtype=float)
        valid_mask = ~np.isnan(freq_values)
        if not np.any(valid_mask):
            continue
        _ = plt.scatter(
            l_squid[valid_mask],
            freq_values[valid_mask],
            s=35,
            alpha=0.7,
            label=f"{filename} - {mode}",
        )

    _ = plt.title(f"Resonant Frequency vs L_squid - {filename}")
    _ = plt.xlabel(r"$L_{squid}$ [nH]")
    _ = plt.ylabel("Frequency [GHz]")
    _ = plt.grid(True, linestyle="--", alpha=0.5)
    _ = plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()
