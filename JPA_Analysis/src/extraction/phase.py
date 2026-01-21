from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

CsvPath = Union[str, Path]


def extract_from_phase(
    csv_file_path: CsvPath, freq_range_ghz: tuple[float, float] | None = None
) -> pd.DataFrame | None:
    """
    Extracts resonant frequencies from S11 Phase data based on Group Delay peaks.

    Args:
        csv_file_path (Union[str, Path]): Path to the CSV file.
        freq_range_ghz (Union[tuple[float, float], None]): Frequency range to analyze (min, max) in GHz.

    Returns:
        Union[pd.DataFrame, None]: DataFrame containing 'L_jun', 'Mode 1', and 'Q_factor',
                                or None if extraction fails.
    """
    try:
        csv_path = Path(csv_file_path)
        df: pd.DataFrame = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[Error] Failed to read file {csv_file_path}: {e}")
        return None

    # --- 1. Identify Columns ---
    l_cols: list[str] = [c for c in df.columns if "L_jun" in c or "L_ind" in c]
    l_col: str | None = l_cols[0] if l_cols else None

    freq_cols: list[str] = [c for c in df.columns if "Freq" in c]
    if not freq_cols:
        return None
    freq_col: str = freq_cols[0]

    phase_cols: list[str] = [
        c for c in df.columns if "deg" in c.lower() or "ang" in c.lower() or "phase" in c.lower()
    ]
    if not phase_cols:
        return None
    phase_col: str = phase_cols[0]

    # --- 2. Process Data ---
    results: list[dict[str, float]] = []

    unique_Ls: list[float]
    if l_col:
        unique_Ls = sorted(df[l_col].unique())
    else:
        unique_Ls = [0.0]

    for l_val in unique_Ls:
        # Filter data
        if l_col:
            subset = df[df[l_col] == l_val].sort_values(freq_col)
        else:
            subset = df.sort_values(freq_col)

        # Frequency Range Filter
        if freq_range_ghz:
            subset = subset[
                (subset[freq_col] >= freq_range_ghz[0]) & (subset[freq_col] <= freq_range_ghz[1])
            ]

        if subset.empty or len(subset) < 5:
            continue

        freqs: np.ndarray = subset[freq_col].to_numpy(dtype=float) * 1e9  # Hz
        phase_deg: np.ndarray = subset[phase_col].to_numpy(dtype=float)

        # Unwrap phase
        phase_rad = np.deg2rad(phase_deg)
        phase_unwrapped = np.unwrap(phase_rad)

        # Calculate Group Delay: tau = -d(phi)/d(omega)
        omega = 2 * np.pi * freqs
        group_delay = -np.gradient(phase_unwrapped, omega)

        # Find Peak (Resonance)
        peak_idx = np.argmax(group_delay)

        f0 = freqs[peak_idx]

        entry: dict[str, float] = {"L_jun": float(l_val)}
        entry["Mode 1"] = float(f0 / 1e9)  # GHz

        # Calculate Q Factor
        tau_max = group_delay[peak_idx]
        w0 = 2 * np.pi * f0
        Q_val = (w0 * tau_max) / 4
        entry["Q_factor"] = Q_val

        results.append(entry)

    return pd.DataFrame(results)
