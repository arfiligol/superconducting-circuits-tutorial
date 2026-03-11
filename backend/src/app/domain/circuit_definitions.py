from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ValidationNotice:
    level: Literal["ok", "warning"]
    message: str


@dataclass(frozen=True)
class CircuitDefinitionSummary:
    definition_id: int
    name: str
    created_at: str
    element_count: int


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
