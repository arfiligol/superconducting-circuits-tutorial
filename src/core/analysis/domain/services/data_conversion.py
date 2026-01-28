import pandas as pd

from core.shared.persistence import DataRecord


def _canonical_column_name(axis: dict, default: str | None = None) -> str:
    name = str(axis.get("name", ""))
    if default and default.lower() in name.lower():
        name = default
    unit = str(axis.get("unit", ""))
    return f"{name} [{unit}]"


def convert_data_record_to_dataframe(record: DataRecord, value_label: str) -> pd.DataFrame:
    """
    Convert a 2D DataRecord into a wide-format DataFrame (or long-format depending on usage).
    The implementation here builds a list of dicts.
    """
    if len(record.axes) != 2:
        raise ValueError("Only 2D datasets can be converted to DataFrame.")
    axis_freq, axis_bias = record.axes
    freq_col = _canonical_column_name(axis_freq, default="Freq")
    bias_col = _canonical_column_name(axis_bias, default="L_jun")
    matrix = record.values  # List[List[float]]
    rows = []

    # Validation for 2D structure
    if not matrix or not isinstance(matrix[0], list):
        raise ValueError("Expected 2D matrix for values")

    freq_values = axis_freq.get("values", [])
    bias_values = axis_bias.get("values", [])
    for row_idx, freq in enumerate(freq_values):
        row_vals = matrix[row_idx]
        for col_idx, bias in enumerate(bias_values):
            rows.append(
                {
                    freq_col: float(freq),
                    bias_col: float(bias),
                    value_label: float(row_vals[col_idx]),  # type: ignore
                }
            )
    return pd.DataFrame(rows)
