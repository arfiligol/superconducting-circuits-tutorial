from dataclasses import dataclass
from typing import Literal

DatasetStatus = Literal["Ready", "Queued", "Review"]
DatasetSortBy = Literal["updated_at", "name", "samples"]
SortOrder = Literal["asc", "desc"]
DatasetMetadataField = Literal["device_type", "capabilities", "source"]


@dataclass(frozen=True)
class DatasetSummary:
    dataset_id: str
    name: str
    family: str
    owner: str
    updated_at: str
    device_type: str
    source: str
    samples: int
    status: DatasetStatus
    capability_count: int
    tag_count: int


@dataclass(frozen=True)
class DatasetDetail:
    dataset_id: str
    name: str
    family: str
    owner: str
    updated_at: str
    device_type: str
    capabilities: tuple[str, ...]
    source: str
    samples: int
    status: DatasetStatus
    tags: tuple[str, ...]
    preview_columns: tuple[str, ...]
    preview_rows: tuple[tuple[str, ...], ...]
    artifacts: tuple[str, ...]
    lineage: tuple[str, ...]


@dataclass(frozen=True)
class DatasetMetadataUpdate:
    device_type: str
    capabilities: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class DatasetListQuery:
    family: str | None = None
    status: DatasetStatus | None = None
    sort_by: DatasetSortBy = "updated_at"
    sort_order: SortOrder = "desc"


@dataclass(frozen=True)
class DatasetMetadataUpdateResult:
    dataset: DatasetDetail
    updated_fields: tuple[DatasetMetadataField, ...]
