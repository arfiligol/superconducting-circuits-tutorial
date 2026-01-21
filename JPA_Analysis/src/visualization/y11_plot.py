from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from src.types import Y11FitSuccess


def plot_y11_fit(filename: str, fit: Y11FitSuccess) -> None:
    freq_raw = np.array(fit["raw_data"]["freq_ghz"], dtype=float)
    imag_raw = np.array(fit["raw_data"]["imag_y"], dtype=float)
    l_jun_raw = np.array(fit["raw_data"]["L_jun"], dtype=float)

    freq_fit = np.array(fit["fit_curve"]["freq_ghz"], dtype=float)
    imag_fit = np.array(fit["fit_curve"]["imag_y"], dtype=float)
    l_jun_fit = np.array(fit["fit_curve"]["L_jun"], dtype=float)

    unique_ljun = np.unique(l_jun_raw)
    cmap = plt.get_cmap("tab10")

    _ = plt.figure(figsize=(10, 6))
    for idx, l_val in enumerate(sorted(unique_ljun)):
        mask_raw = np.isclose(l_jun_raw, l_val)
        if not np.any(mask_raw):
            continue
        color = cmap(idx % cmap.N)
        label = f"L_jun={l_val:.3f} nH (L_squid={l_val / 2:.3f} nH)"
        _ = plt.scatter(
            freq_raw[mask_raw],
            imag_raw[mask_raw],
            s=12,
            alpha=0.7,
            color=color,
            label=f"{label} data",
        )

        mask_fit = np.isclose(l_jun_fit, l_val)
        if np.any(mask_fit):
            order = np.argsort(freq_fit[mask_fit])
            _ = plt.plot(
                freq_fit[mask_fit][order],
                imag_fit[mask_fit][order],
                linestyle="--",
                color=color,
                linewidth=1.8,
                label=f"{label} fit",
            )

    _ = plt.xlabel("Frequency [GHz]")
    _ = plt.ylabel("Im(Y11) [S]")
    _ = plt.title(f"Y11 Fit - {filename}")
    _ = plt.grid(True, linestyle="--", alpha=0.5)
    _ = plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()
