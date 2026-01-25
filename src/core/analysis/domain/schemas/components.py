from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from enum import Enum
from typing import cast

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
    imported_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ParameterAxis(BaseModel):
    """Defines one sweep axis (bias, frequency, etc.)."""

    name: str
    unit: str
    values: Sequence[float]

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: Sequence[float]) -> Sequence[float]:
        if not values:
            raise ValueError("Axis values cannot be empty.")
        return values


ValueArray = list[float] | list[list[float]]


class ParameterDataset(BaseModel):
    """
    Canonical representation for a single parameter dataset.
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
    @classmethod
    def validate_shape(cls, values: ValueArray, info: ValidationInfo) -> ValueArray:
        data = info.data
        if not data:
            return values

        axes = cast(list[ParameterAxis], data.get("axes", []))
        dim = len(axes)

        if dim == 0:
            raise ValueError("At least one axis is required.")

        if dim == 1:
            expected_len = len(axes[0].values)
            if values and isinstance(values[0], list):
                raise ValueError("1D dataset must be a list of numbers.")
            if len(values) != expected_len:
                raise ValueError(
                    f"Values length ({len(values)}) must match axis length ({expected_len})."
                )
        elif dim == 2:
            freq_len = len(axes[0].values)
            bias_len = len(axes[1].values)
            if not values or not isinstance(values[0], list):
                raise ValueError("2D dataset must be a list of lists.")

            # Help the type checker know this is a list of lists
            matrix_values = cast(list[list[float]], values)

            if len(matrix_values) != freq_len:
                raise ValueError(
                    f"Row count ({len(matrix_values)}) must match first axis length ({freq_len})."
                )
            for row in matrix_values:
                if len(row) != bias_len:
                    raise ValueError(
                        f"Column count ({len(row)}) must match second axis length ({bias_len})."
                    )
        else:
            raise ValueError("Only up to 2 axes are currently supported.")
        return values


class ComponentRecord(BaseModel):
    """
    Aggregated data for a single component.
    """

    component_id: str
    source_type: SourceType
    datasets: list[ParameterDataset]
    metadata: dict[str, str] = Field(default_factory=dict)
    sweep_parameters: dict[str, float] = Field(default_factory=dict)
    raw_files: list[RawFileMeta] = Field(default_factory=list)

    @field_validator("datasets")
    @classmethod
    def validate_datasets(cls, datasets: list[ParameterDataset]) -> list[ParameterDataset]:
        if not datasets:
            raise ValueError("Component must include at least one dataset.")
        return datasets
