from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from enum import Enum
from typing import List, Union, cast

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class SourceType(str, Enum):
    """Top-level origin of the data."""

    circuit_simulation = "circuit_simulation"
    layout_simulation = "layout_simulation"
    measurement = "measurement"


class ParameterFamily(str, Enum):
    """Whether the dataset represents S, Y, or Z parameters."""

    s_parameters = "s_parameters"
    y_parameters = "y_parameters"
    z_parameters = "z_parameters"


class ParameterRepresentation(str, Enum):
    """Representation of the parameter values."""

    amplitude = "amplitude"
    phase = "phase"
    real = "real"
    imaginary = "imaginary"


class RawFileMeta(BaseModel):
    """Metadata describing a raw input file used to generate the record."""

    path: str
    hash: str | None = None
    imported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ParameterAxis(BaseModel):
    """Defines one sweep axis (bias, frequency, etc.)."""

    name: str
    unit: str
    values: Sequence[float]

    @field_validator("values")
    def validate_values(cls, values: Sequence[float]) -> Sequence[float]:
        if not values:
            raise ValueError("Axis values cannot be empty.")
        return values


ValueArray = Union[List[float], List[List[float]]]


class ParameterDataset(BaseModel):
    """
    Canonical representation for a single parameter dataset.

    Examples:
        - S11 amplitude over bias + frequency (axes=2, values=matrix)
        - Y21 real part versus frequency (axes=1, values=list)
    """

    dataset_id: str
    family: ParameterFamily
    parameter: str  # e.g., S11, Z21
    representation: ParameterRepresentation
    ports: Sequence[str] = Field(default_factory=list)
    axes: list[ParameterAxis]
    values: ValueArray
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("values")
    def validate_shape(cls, values: ValueArray, info: ValidationInfo):
        data = info.data if hasattr(info, "data") else {}
        axes = cast(list[ParameterAxis], data.get("axes", []))
        dim = len(axes)
        if dim == 0:
            raise ValueError("At least one axis is required.")
        if dim == 1:
            expected_len = len(axes[0].values)
            if values and isinstance(values[0], list):
                raise ValueError("1D dataset must be a list of numbers.")
            if len(values) != expected_len:
                raise ValueError("Values length must match axis length.")
        elif dim == 2:
            freq_len = len(axes[0].values)
            bias_len = len(axes[1].values)
            if not values or not isinstance(values[0], list):
                raise ValueError("2D dataset must be a list of lists.")

            # Help the type checker know this is a list of lists
            matrix_values = cast(list[list[float]], values)

            if len(matrix_values) != freq_len:
                raise ValueError("Row count must match first axis length.")
            for row in matrix_values:
                if len(row) != bias_len:
                    raise ValueError("Column count must match second axis length.")
        else:
            raise ValueError("Only up to 2 axes are currently supported.")
        return values


class ComponentRecord(BaseModel):
    """
    Aggregated data for a single component.

    Every record corresponds to one component_id plus zero or more parameter datasets.
    """

    component_id: str
    source_type: SourceType
    datasets: list[ParameterDataset]
    metadata: dict[str, str] = Field(default_factory=dict)
    sweep_parameters: dict[str, float] = Field(default_factory=dict)
    raw_files: list[RawFileMeta] = Field(default_factory=list)

    @field_validator("datasets")
    def validate_datasets(cls, datasets: list[ParameterDataset]) -> list[ParameterDataset]:
        if not datasets:
            raise ValueError("Component must include at least one dataset.")
        return datasets


if __name__ == "__main__":
    # Example showing how a flux bias sweep can be represented.
    freq_axis = ParameterAxis(
        name="frequency",
        unit="GHz",
        values=[3.8, 3.9, 4.0],
    )
    flux_axis = ParameterAxis(
        name="flux_bias",
        unit="mA",
        values=[-2.0, -1.0, 0.0, 1.0, 2.0],
    )
    example_dataset = ParameterDataset(
        dataset_id="LJPAL6572-flux-s11-amplitude",
        family=ParameterFamily.s_parameters,
        parameter="S11",
        representation=ParameterRepresentation.amplitude,
        ports=["port1"],
        axes=[freq_axis, flux_axis],
        values=[
            [-21.0, -20.5, -20.1, -21.3, -22.0],
            [-18.2, -18.0, -17.9, -18.4, -19.2],
            [-15.0, -15.8, -16.1, -15.7, -15.3],
        ],
        metadata={"power_dBm": "-55"},
    )
    record = ComponentRecord(
        component_id="LJPAL6572",
        source_type=SourceType.measurement,
        datasets=[example_dataset],
    )
    print(record.model_dump_json(indent=2))


__all__ = [
    "ComponentRecord",
    "ParameterAxis",
    "ParameterDataset",
    "ParameterFamily",
    "ParameterRepresentation",
    "RawFileMeta",
    "SourceType",
]
