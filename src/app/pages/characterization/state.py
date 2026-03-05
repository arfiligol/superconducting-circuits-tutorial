"""Typed state contracts for Characterization page orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AnalysisScopeCompatibility:
    """Compatibility summary for one analysis under current record scope."""

    compatible_trace_rows: list[dict[str, str | int]]
    compatible_trace_count: int
    has_compatible_traces: bool
    status: str
    message: str


@dataclass(frozen=True)
class AnalysisRunUiState:
    """UI contract for availability label and run-button enabled state."""

    has_compatible_traces: bool
    availability_text: str
    availability_class: str
    run_disabled: bool
    run_hint: str


@dataclass(frozen=True)
class AnalysisRunAvailability:
    """Profile recommendation + scope compatibility for one analysis."""

    status: str
    reason: str
    has_compatible_traces: bool
    profile_hints: list[str]


@dataclass(frozen=True)
class ResultArtifact:
    """Declarative contract for one result-view unit."""

    artifact_id: str
    analysis_id: str
    category: str
    view_kind: str
    tab_label: str
    title: str
    subtitle: str | None
    query_spec: dict[str, Any]
    meta: dict[str, Any]

