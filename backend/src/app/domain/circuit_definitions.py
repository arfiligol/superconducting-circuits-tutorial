from dataclasses import dataclass
from typing import Literal

ValidationLevel = Literal["ok", "warning"]
CircuitDefinitionSortBy = Literal["created_at", "name", "element_count"]
SortOrder = Literal["asc", "desc"]


@dataclass(frozen=True)
class ValidationNotice:
    level: ValidationLevel
    message: str


@dataclass(frozen=True)
class CircuitDefinitionSummary:
    definition_id: int
    name: str
    created_at: str
    element_count: int
    validation_status: ValidationLevel
    preview_artifact_count: int


@dataclass(frozen=True)
class CircuitDefinitionDetail:
    definition_id: int
    name: str
    created_at: str
    element_count: int
    source_text: str
    normalized_output: str
    validation_notices: tuple[ValidationNotice, ...]
    preview_artifacts: tuple[str, ...]


@dataclass(frozen=True)
class CircuitDefinitionDraft:
    name: str
    source_text: str


@dataclass(frozen=True)
class CircuitDefinitionUpdate:
    name: str
    source_text: str


@dataclass(frozen=True)
class CircuitDefinitionListQuery:
    search: str | None = None
    sort_by: CircuitDefinitionSortBy = "created_at"
    sort_order: SortOrder = "desc"
