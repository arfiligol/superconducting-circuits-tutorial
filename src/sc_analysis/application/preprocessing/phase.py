from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from sc_analysis.domain.schemas.components import (
    ComponentRecord,
    ParameterAxis,
    ParameterDataset,
    ParameterFamily,
    ParameterRepresentation,
    RawFileMeta,
    SourceType,
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


def build_component_record(
    component_id: str,
    pivot_rad: pd.DataFrame,
    raw_path: str,
    parameter_name: str,
) -> ComponentRecord:
    freq_axis = ParameterAxis(name="Freq", unit="GHz", values=pivot_rad.index.tolist())
    bias_axis = ParameterAxis(
        name="L_jun", unit="nH", values=pivot_rad.columns.astype(float).tolist()
    )

    dataset_phase = ParameterDataset(
        dataset_id=f"{component_id}-{parameter_name}-phase",
        family=ParameterFamily.s_parameters,
        parameter=parameter_name,
        representation=ParameterRepresentation.phase,
        ports=["port1"],
        axes=[freq_axis, bias_axis],
        values=pivot_rad.values.tolist(),
        metadata={},
    )

    record = ComponentRecord(
        component_id=component_id,
        source_type=SourceType.measurement,
        datasets=[dataset_phase],
        raw_files=[RawFileMeta(path=raw_path)],
    )
    return record


def process_hfss_phase_file(raw_path: Path, component_id: str) -> ComponentRecord:
    """
    Orchestrate the processing of a single HFSS Phase CSV file into a ComponentRecord.
    """
    df = pd.read_csv(raw_path)
    l_col, freq_col, phase_col = detect_columns(df)
    pivot_deg = reshape_matrix(df, l_col, freq_col, phase_col)
    pivot_rad = convert_to_radians(pivot_deg)

    record = build_component_record(
        component_id, pivot_rad, str(raw_path.resolve()), parameter_name="S11"
    )
    return record
