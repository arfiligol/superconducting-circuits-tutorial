from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import cast

import pandas as pd

from src.preprocess.schema import (
    ComponentRecord,
    ParameterAxis,
    ParameterDataset,
    ParameterFamily,
    ParameterRepresentation,
)


def load_component_record(path: Path) -> ComponentRecord:
    """
    Load and validate a preprocessed component JSON.
    """
    text = path.read_text(encoding="utf-8")
    return ComponentRecord.model_validate_json(text)


def find_dataset(
    record: ComponentRecord,
    *,
    family: ParameterFamily,
    parameter: str,
    representation: ParameterRepresentation,
) -> ParameterDataset:
    parameter_upper = parameter.upper()
    for dataset in record.datasets:
        if (
            dataset.family == family
            and dataset.representation == representation
            and dataset.parameter.upper() == parameter_upper
        ):
            return dataset
    raise ValueError(
        f"Dataset not found: family={family}, parameter={parameter}, representation={representation}"
    )


def dataset_to_dataframe(
    dataset: ParameterDataset,
    value_label: str,
) -> pd.DataFrame:
    """
    Convert a 2D ParameterDataset into a long-form DataFrame compatible with legacy analysis code.
    """
    if len(dataset.axes) != 2:
        raise ValueError("Only 2D datasets can be converted to DataFrame.")

    axis_freq, axis_bias = dataset.axes
    freq_col = _canonical_column_name(axis_freq, default="Freq")
    bias_col = _canonical_column_name(axis_bias, default="L_jun")

    matrix = cast(Sequence[Sequence[float]], dataset.values)
    rows: list[dict[str, float]] = []
    for row_idx, freq in enumerate(axis_freq.values):
        row_vals = matrix[row_idx]
        for col_idx, bias in enumerate(axis_bias.values):
            rows.append(
                {
                    freq_col: float(freq),
                    bias_col: float(bias),
                    value_label: float(row_vals[col_idx]),
                }
            )
    return pd.DataFrame(rows)


def _canonical_column_name(axis: ParameterAxis, default: str | None = None) -> str:
    name = axis.name
    if default and default.lower() in name.lower():
        name = default
    return f"{name} [{axis.unit}]"
