"""CLI-local standalone circuit-definition contracts."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, Protocol

from pydantic import BaseModel

LocalValidationLevel = Literal["ok", "warning", "invalid"]


class LocalValidationNotice(BaseModel):
    level: LocalValidationLevel
    message: str


class LocalValidationSummary(BaseModel):
    status: LocalValidationLevel
    notice_count: int
    warning_count: int
    invalid_count: int


class LocalCircuitDefinitionSummary(BaseModel):
    definition_id: int
    name: str
    created_at: str
    element_count: int
    validation_status: LocalValidationLevel
    preview_artifact_count: int


class LocalCircuitDefinitionDetail(LocalCircuitDefinitionSummary):
    source_text: str
    normalized_output: str
    validation_notices: list[LocalValidationNotice]
    validation_summary: LocalValidationSummary
    preview_artifacts: list[str]


class LocalCircuitDefinitionInspection(BaseModel):
    source_file: str
    circuit_name: str
    family: str
    element_count: int
    validation_status: LocalValidationLevel
    preview_artifact_count: int
    preview_artifacts: list[str]
    normalized_output: str
    validation_notices: list[LocalValidationNotice]
    validation_summary: LocalValidationSummary


class SupportsValidationNotice(Protocol):
    level: str
    message: str


class SupportsCircuitDefinitionSummaryPayload(Protocol):
    definition_id: int
    name: str
    created_at: str
    element_count: int
    validation_status: str
    preview_artifact_count: int


class SupportsCircuitDefinitionDetailPayload(
    SupportsCircuitDefinitionSummaryPayload,
    Protocol,
):
    source_text: str
    normalized_output: str
    validation_notices: Iterable[SupportsValidationNotice]
    preview_artifacts: Iterable[str]


class SupportsCircuitDefinitionInspectionPayload(Protocol):
    circuit_name: str
    family: str
    element_count: int
    normalized_output: str
    validation_notices: Iterable[SupportsValidationNotice]


def normalize_validation_level(level: str) -> LocalValidationLevel:
    if level == "ok":
        return "ok"
    if level == "warning":
        return "warning"
    return "invalid"


def build_local_validation_notices(
    notices: Iterable[SupportsValidationNotice],
) -> list[LocalValidationNotice]:
    local_notices: list[LocalValidationNotice] = []
    for notice in notices:
        local_notices.append(
            LocalValidationNotice(
                level=normalize_validation_level(str(notice.level)),
                message=str(notice.message),
            )
        )
    return local_notices


def derive_validation_status(
    notices: Iterable[LocalValidationNotice],
) -> LocalValidationLevel:
    levels = {notice.level for notice in notices}
    if "invalid" in levels:
        return "invalid"
    if "warning" in levels:
        return "warning"
    return "ok"


def build_validation_summary(
    notices: list[LocalValidationNotice],
) -> LocalValidationSummary:
    return LocalValidationSummary(
        status=derive_validation_status(notices),
        notice_count=len(notices),
        warning_count=sum(1 for notice in notices if notice.level == "warning"),
        invalid_count=sum(1 for notice in notices if notice.level == "invalid"),
    )


def build_local_circuit_definition_summary(
    payload: SupportsCircuitDefinitionSummaryPayload,
) -> LocalCircuitDefinitionSummary:
    return LocalCircuitDefinitionSummary(
        definition_id=int(payload.definition_id),
        name=str(payload.name),
        created_at=str(payload.created_at),
        element_count=int(payload.element_count),
        validation_status=normalize_validation_level(str(payload.validation_status)),
        preview_artifact_count=int(payload.preview_artifact_count),
    )


def build_local_circuit_definition_detail(
    payload: SupportsCircuitDefinitionDetailPayload,
) -> LocalCircuitDefinitionDetail:
    validation_notices = build_local_validation_notices(payload.validation_notices)
    validation_summary = build_validation_summary(validation_notices)
    summary = build_local_circuit_definition_summary(payload)
    return LocalCircuitDefinitionDetail(
        definition_id=summary.definition_id,
        name=summary.name,
        created_at=summary.created_at,
        element_count=summary.element_count,
        validation_status=validation_summary.status,
        preview_artifact_count=summary.preview_artifact_count,
        source_text=str(payload.source_text),
        normalized_output=str(payload.normalized_output),
        validation_notices=validation_notices,
        validation_summary=validation_summary,
        preview_artifacts=[str(artifact) for artifact in payload.preview_artifacts],
    )


def build_local_circuit_definition_inspection(
    *,
    source_file: str,
    inspection: SupportsCircuitDefinitionInspectionPayload,
    preview_artifacts: Iterable[str],
) -> LocalCircuitDefinitionInspection:
    validation_notices = build_local_validation_notices(inspection.validation_notices)
    validation_summary = build_validation_summary(validation_notices)
    preview_artifact_list = [str(artifact) for artifact in preview_artifacts]
    return LocalCircuitDefinitionInspection(
        source_file=source_file,
        circuit_name=str(inspection.circuit_name),
        family=str(inspection.family),
        element_count=int(inspection.element_count),
        validation_status=validation_summary.status,
        preview_artifact_count=len(preview_artifact_list),
        preview_artifacts=preview_artifact_list,
        normalized_output=str(inspection.normalized_output),
        validation_notices=validation_notices,
        validation_summary=validation_summary,
    )
