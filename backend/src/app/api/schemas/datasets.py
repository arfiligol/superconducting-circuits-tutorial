from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    name: str
    family: str
    owner: str
    updated_at: str
    device_type: str
    source: str
    samples: int
    status: Literal["Ready", "Queued", "Review"]
    capability_count: int
    tag_count: int


class DatasetMetricsResponse(BaseModel):
    capability_count: int
    tag_count: int
    preview_row_count: int
    artifact_count: int
    lineage_depth: int


class DatasetDetailResponse(DatasetSummaryResponse):
    capabilities: list[str]
    tags: list[str]
    preview_columns: list[str]
    preview_rows: list[list[str]]
    artifacts: list[str]
    lineage: list[str]
    metrics: DatasetMetricsResponse


class DatasetMetadataUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    device_type: str = Field(min_length=1)
    capabilities: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1)

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, capabilities: list[str]) -> list[str]:
        cleaned = [capability.strip() for capability in capabilities]
        if any(not capability for capability in cleaned):
            raise ValueError("Capabilities must not be blank.")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("Capabilities must be unique.")
        return cleaned


class DatasetMetadataUpdateResponse(BaseModel):
    dataset: DatasetDetailResponse
    updated_fields: list[Literal["device_type", "capabilities", "source"]]
