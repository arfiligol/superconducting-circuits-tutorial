import pandas as pd

from core.analysis.domain.schemas.components import ParameterAxis, ParameterDataset


def _canonical_column_name(axis: ParameterAxis, default: str | None = None) -> str:
    name = axis.name
    if default and default.lower() in name.lower():
        name = default
    return f"{name} [{axis.unit}]"


def convert_dataset_to_dataframe(dataset: ParameterDataset, value_label: str) -> pd.DataFrame:
    """
    Convert a 2D ParameterDataset into a wide-format DataFrame (or long-format depending on usage).
    The implementation here builds a list of dicts.
    """
    if len(dataset.axes) != 2:
        raise ValueError("Only 2D datasets can be converted to DataFrame.")
    axis_freq, axis_bias = dataset.axes
    freq_col = _canonical_column_name(axis_freq, default="Freq")
    bias_col = _canonical_column_name(axis_bias, default="L_jun")
    matrix = dataset.values  # List[List[float]]
    rows = []

    # Validation for 2D structure
    if not matrix or not isinstance(matrix[0], list):
        raise ValueError("Expected 2D matrix for values")

    for row_idx, freq in enumerate(axis_freq.values):
        row_vals = matrix[row_idx]
        for col_idx, bias in enumerate(axis_bias.values):
            rows.append(
                {
                    freq_col: float(freq),
                    bias_col: float(bias),
                    value_label: float(row_vals[col_idx]),  # type: ignore
                }
            )
    return pd.DataFrame(rows)
