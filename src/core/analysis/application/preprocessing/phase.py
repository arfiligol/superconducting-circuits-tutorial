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
    l_cols = [c for c in df.columns if "l_jun" in c.lower()]
    if not l_cols:
        raise ValueError("Unable to locate L_jun column.")
    freq_cols = [c for c in df.columns if "freq" in c.lower()]
    if not freq_cols:
        raise ValueError("Unable to locate frequency column.")
    phase_cols = [
        c for c in df.columns if "phase" in c.lower() or "deg(" in c.lower() or "cang" in c.lower()
    ]
    if not phase_cols:
        raise ValueError("Unable to locate phase column.")
    return l_cols[0], freq_cols[0], phase_cols[0]


def reshape_matrix(df: pd.DataFrame, l_col: str, freq_col: str, phase_col: str) -> pd.DataFrame:
    pivot = df.pivot(index=freq_col, columns=l_col, values=phase_col).sort_index()
    pivot = pivot[sorted(pivot.columns)]
    return pivot


def convert_to_radians(matrix: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(np.deg2rad(matrix), index=matrix.index, columns=matrix.columns)


def build_dataset_payload(
    pivot_rad: pd.DataFrame,
    raw_path: str,
    parameter_name: str,
) -> DatasetPayload:
    freq_axis = AxisPayload(name="Freq", unit="GHz", values=pivot_rad.index.tolist())
    bias_axis = AxisPayload(
        name="L_jun", unit="nH", values=pivot_rad.columns.astype(float).tolist()
    )

    dataset_phase = DataPayload(
        data_type="s_parameters",
        parameter=parameter_name,
        representation="phase",
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
    pivot_deg = reshape_matrix(df, l_col, freq_col, phase_col)
    pivot_rad = convert_to_radians(pivot_deg)
    return build_dataset_payload(pivot_rad, str(raw_path.resolve()), parameter_name="S11")
