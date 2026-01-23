from __future__ import annotations

from pathlib import Path

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
    l_cols = [c for c in df.columns if "l_jun" in c.lower() or "l_ind" in c.lower()]
    if not l_cols:
        raise ValueError("Unable to locate L_jun column.")
    freq_cols = [c for c in df.columns if "freq" in c.lower()]
    if not freq_cols:
        raise ValueError("Unable to locate frequency column.")
    y_cols = [c for c in df.columns if "y" in c.lower()]
    if not y_cols:
        raise ValueError("Unable to locate admittance column.")
    return l_cols[0], freq_cols[0], y_cols[0]


def reshape_matrix(df: pd.DataFrame, l_col: str, freq_col: str, y_col: str) -> pd.DataFrame:
    pivot = df.pivot(index=freq_col, columns=l_col, values=y_col).sort_index()
    # Sort columns (L_jun values) numerically
    pivot = pivot[sorted(pivot.columns, key=float)]
    return pivot


def derive_parameter_name(column: str) -> str:
    lower = column.lower()
    if "y11" in lower or "(rect" in lower:
        return "Y11"
    if "y22" in lower:
        return "Y22"
    if "y12" in lower:
        return "Y12"
    if "y21" in lower:
        return "Y21"
    return "Y"


def build_component_record(
    component_id: str,
    pivot: pd.DataFrame,
    raw_path: str,  # Path string
    parameter_name: str,
) -> ComponentRecord:
    frequency_axis = ParameterAxis(name="Freq", unit="GHz", values=pivot.index.tolist())
    # Columns are strings/floats from pivot, convert to float
    bias_axis = ParameterAxis(name="L_jun", unit="nH", values=[float(x) for x in pivot.columns])

    # pivot.values is numpy array, convert to list of lists
    values = pivot.values.tolist()

    dataset = ParameterDataset(
        dataset_id=f"{component_id}-{parameter_name}-imag",
        family=ParameterFamily.y_parameters,
        parameter=parameter_name,
        representation=ParameterRepresentation.imaginary,
        ports=["port1"],
        axes=[frequency_axis, bias_axis],
        values=values,
        metadata={},
    )

    record = ComponentRecord(
        component_id=component_id,
        source_type=SourceType.measurement,
        datasets=[dataset],
        raw_files=[RawFileMeta(path=raw_path)],
    )
    return record


def process_hfss_admittance_file(raw_path: Path, component_id: str) -> ComponentRecord:
    """
    Orchestrate the processing of a single HFSS CSV file into a ComponentRecord.
    """
    df = pd.read_csv(raw_path)
    l_col, freq_col, y_col = detect_columns(df)
    pivot = reshape_matrix(df, l_col, freq_col, y_col)
    parameter_name = derive_parameter_name(y_col)

    record = build_component_record(component_id, pivot, str(raw_path.resolve()), parameter_name)
    return record
