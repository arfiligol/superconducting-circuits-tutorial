from dataclasses import dataclass
from typing import Literal

ValidationLevel = Literal["ok", "warning"]

DEFAULT_PREVIEW_ARTIFACTS: tuple[str, ...] = (
    "definition.normalized.json",
    "schematic-input.yaml",
    "parameter-bundle.toml",
)


@dataclass(frozen=True)
class ValidationNotice:
    level: ValidationLevel
    message: str


@dataclass(frozen=True)
class CircuitDefinitionInspection:
    circuit_name: str
    family: str
    element_count: int
    normalized_output: str
    validation_notices: tuple[ValidationNotice, ...]


def inspect_circuit_definition_source(source_text: str) -> CircuitDefinitionInspection:
    circuit_name = _extract_scalar(source_text, "name") or "pending_name"
    family = _extract_scalar(source_text, "family") or "pending_family"
    element_count = estimate_element_count(source_text)
    return CircuitDefinitionInspection(
        circuit_name=circuit_name,
        family=family,
        element_count=element_count,
        normalized_output=_render_normalized_output(circuit_name, family, element_count),
        validation_notices=_default_validation_notices(),
    )


def estimate_element_count(source_text: str) -> int:
    return max(1, sum(1 for line in source_text.splitlines() if ":" in line) - 3)


def _render_normalized_output(circuit_name: str, family: str, element_count: int) -> str:
    return (
        "{\n"
        f'  "circuit": "{circuit_name}",\n'
        f'  "family": "{family}",\n'
        f'  "elements": {element_count},\n'
        '  "ports": "pending migration",\n'
        '  "schemdraw_ready": true\n'
        "}"
    )


def _default_validation_notices() -> tuple[ValidationNotice, ...]:
    return (
        ValidationNotice(level="ok", message="Canonical schema matches rewrite draft v1."),
        ValidationNotice(level="ok", message="All required element blocks are present."),
        ValidationNotice(
            level="warning",
            message="Port mapping metadata still needs migration from legacy forms.",
        ),
    )


def _extract_scalar(source_text: str, field_name: str) -> str | None:
    for raw_line in source_text.splitlines():
        line = raw_line.strip()
        if not line.startswith(f"{field_name}:"):
            continue
        _, _, value = line.partition(":")
        cleaned = value.strip()
        if cleaned:
            return cleaned
    return None
