from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from core.analysis.application.preprocessing.dataset_payload import (
    AxisPayload,
    DataPayload,
    DatasetPayload,
)


def detect_columns(df: pd.DataFrame) -> tuple[str, str, str]:
    l_cols = [c for c in df.columns if "l_jun" in c.lower() or "l_ind" in c.lower()]
    if not l_cols:
        raise ValueError("Unable to locate L_jun column.")
    freq_cols = [c for c in df.columns if "freq" in c.lower()]
    if not freq_cols:
        raise ValueError("Unable to locate frequency column.")
    phase_cols = [
        c
        for c in df.columns
        if any(kw in c.lower() for kw in ["phase", "deg", "rad", "ang", "cang"])
    ]
    if not phase_cols:
        raise ValueError("Unable to locate phase column.")
    return l_cols[0], freq_cols[0], phase_cols[0]


def reshape_matrix(df: pd.DataFrame, l_col: str, freq_col: str, phase_col: str) -> pd.DataFrame:
    pivot = df.pivot(index=freq_col, columns=l_col, values=phase_col).sort_index()
    pivot = pivot[sorted(pivot.columns, key=float)]
    return pivot


def derive_parameter_name(input_str: str) -> str:
    lower = input_str.lower()
    if "s11" in lower:
        return "S11"
    if "s21" in lower:
        return "S21"
    if "s12" in lower:
        return "S12"
    if "s22" in lower:
        return "S22"
    raise ValueError(f"Unable to derive phase parameter name (S11, S21, etc.) from '{input_str}'")


def parse_phase_metadata(filename: str, col_name: str) -> tuple[bool, str]:
    """Determine if data is in degrees and whether it's wrapped or unwrapped phase."""
    combined = f"{filename} {col_name}".lower()

    # Default to degrees if not explicitly rad, but check rad first
    is_degrees = True
    if "rad" in combined and "deg" not in combined:
        is_degrees = False

    # Check representation
    representation = "unwrapped_phase" if "cang" in combined else "phase"

    return is_degrees, representation


def build_dataset_payload(
    pivot_rad: pd.DataFrame,
    raw_path: str,
    parameter_name: str,
    representation: str,
) -> DatasetPayload:
    freq_axis = AxisPayload(name="Freq", unit="GHz", values=pivot_rad.index.tolist())
    bias_axis = AxisPayload(name="L_jun", unit="nH", values=[float(x) for x in pivot_rad.columns])

    dataset_phase = DataPayload(
        data_type="s_parameters",
        parameter=parameter_name,
        representation=representation,
        axes=[freq_axis, bias_axis],
        values=pivot_rad.values.tolist(),
    )

    return DatasetPayload(
        source_meta={"origin": "layout_simulation"},
        parameters={},
        data_records=[dataset_phase],
        raw_files=[raw_path],
    )


def process_hfss_phase_file(raw_path: Path) -> DatasetPayload:
    """Orchestrate the processing of a single HFSS Phase CSV file into a dataset payload."""
    df = pd.read_csv(raw_path)
    l_col, freq_col, phase_col = detect_columns(df)

    parameter_name = derive_parameter_name(raw_path.name)
    is_degrees, representation = parse_phase_metadata(raw_path.name, phase_col)

    pivot = reshape_matrix(df, l_col, freq_col, phase_col)

    if is_degrees:
        pivot_rad = pd.DataFrame(np.deg2rad(pivot), index=pivot.index, columns=pivot.columns)
    else:
        pivot_rad = pivot

    return build_dataset_payload(pivot_rad, str(raw_path.resolve()), parameter_name, representation)
