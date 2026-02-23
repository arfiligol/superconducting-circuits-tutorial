"""SQLModel table definitions for persistence layer."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


# ===================
# Enums
# ===================
class DeviceType(str, Enum):
    """Device type for derived parameters."""

    RESONATOR = "resonator"
    QUBIT = "qubit"
    JPA = "jpa"
    OTHER = "other"


# ===================
# Many-to-Many Link Table
# ===================
class DatasetTagLink(SQLModel, table=True):
    """Link table for DatasetRecord <-> Tag many-to-many relationship."""

    __tablename__ = "dataset_tags"  # type: ignore[assignment]

    dataset_id: int = Field(foreign_key="dataset_records.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


# ===================
# Tag
# ===================
class Tag(SQLModel, table=True):
    """Tag for organizing and searching datasets."""

    __tablename__ = "tags"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Relationships
    datasets: list["DatasetRecord"] = Relationship(back_populates="tags", link_model=DatasetTagLink)


# ===================
# DatasetRecord (Collection)
# ===================
class DatasetRecord(SQLModel, table=True):
    """Dataset collection containing multiple DataRecords."""

    __tablename__ = "dataset_records"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Source metadata
    source_meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {"origin": "layout_simulation", "solver": "hfss", "raw_file": "..."}

    # Simulation/measurement parameters
    parameters: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {"L_jun_nH": 0.5, "freq_range_ghz": [1, 10]}

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tags: list["Tag"] = Relationship(back_populates="datasets", link_model=DatasetTagLink)
    data_records: list["DataRecord"] = Relationship(
        back_populates="dataset",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    derived_params: list["DerivedParameter"] = Relationship(
        back_populates="dataset",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ===================
# DataRecord (Single Data)
# ===================
class DataRecord(SQLModel, table=True):
    """Single data record (e.g., Y11 imaginary part)."""

    __tablename__ = "data_records"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="dataset_records.id", index=True)

    # Data type and parameter
    data_type: str  # s_params | y_params | z_params
    parameter: str  # S11, Y21, C12
    representation: str  # real | imaginary | amplitude | phase

    # Axis definitions and values
    axes: list = Field(default_factory=list, sa_column=Column(JSON))
    # [{"name": "frequency", "unit": "GHz", "values": [...]}]

    values: list = Field(default_factory=list, sa_column=Column(JSON))
    # [0.01, 0.02, ...] or [[...], [...]]

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    dataset: Optional["DatasetRecord"] = Relationship(back_populates="data_records")


# ===================
# DerivedParameter
# ===================
class DerivedParameter(SQLModel, table=True):
    """Physical parameter derived from data analysis."""

    __tablename__ = "derived_parameters"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="dataset_records.id", index=True)

    # Device type
    device_type: DeviceType

    # Parameter info
    name: str  # f_resonance, Q_factor, g_coupling
    value: float
    unit: str | None = None

    # Extraction method
    method: str | None = None  # "S11_min", "model_fit", "manual"

    # Extra metadata
    extra: dict = Field(default_factory=dict, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    dataset: Optional["DatasetRecord"] = Relationship(back_populates="derived_params")
