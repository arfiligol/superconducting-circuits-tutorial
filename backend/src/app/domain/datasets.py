from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DatasetSummary:
    dataset_id: str
    name: str
    family: str
    owner: str
    updated_at: str
    samples: int
    status: Literal["Ready", "Queued", "Review"]


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
    status: Literal["Ready", "Queued", "Review"]
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
