from typing import Literal

from pydantic import BaseModel, Field


class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    name: str
    family: str
    owner: str
    updated_at: str
    samples: int
    status: Literal["Ready", "Queued", "Review"]


class DatasetDetailResponse(DatasetSummaryResponse):
    device_type: str
    capabilities: list[str]
    source: str
    tags: list[str]
    preview_columns: list[str]
    preview_rows: list[list[str]]
    artifacts: list[str]
    lineage: list[str]


class DatasetMetadataUpdateRequest(BaseModel):
    device_type: str = Field(min_length=1)
    capabilities: list[str]
    source: str = Field(min_length=1)
