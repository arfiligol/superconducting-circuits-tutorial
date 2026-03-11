from typing import Literal

from pydantic import BaseModel, Field


class ValidationNoticeResponse(BaseModel):
    level: Literal["ok", "warning"]
    message: str


class CircuitDefinitionSummaryResponse(BaseModel):
    definition_id: int
    name: str
    created_at: str
    element_count: int


class CircuitDefinitionDetailResponse(CircuitDefinitionSummaryResponse):
    source_text: str
    normalized_output: str
    validation_notices: list[ValidationNoticeResponse]
    preview_artifacts: list[str]


class CircuitDefinitionCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    source_text: str = Field(min_length=1)


class CircuitDefinitionUpdateRequest(BaseModel):
    name: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
