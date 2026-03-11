"""Output formatting helpers for the CLI adapter layer."""

from pathlib import Path

from sc_core import CircuitDefinitionInspection


def render_preview_artifacts(artifacts: tuple[str, ...]) -> str:
    lines = ["sc_core preview artifacts:"]
    lines.extend(f"- {artifact}" for artifact in artifacts)
    return "\n".join(lines)


def render_circuit_definition_inspection(
    source_file: Path, inspection: CircuitDefinitionInspection
) -> str:
    lines = [
        f"source_file: {source_file}",
        f"circuit_name: {inspection.circuit_name}",
        f"family: {inspection.family}",
        f"element_count: {inspection.element_count}",
        "normalized_output:",
        inspection.normalized_output,
        "validation_notices:",
    ]
    lines.extend(f"- [{notice.level}] {notice.message}" for notice in inspection.validation_notices)
    return "\n".join(lines)
