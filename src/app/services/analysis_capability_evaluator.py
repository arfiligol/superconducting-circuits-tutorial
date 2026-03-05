"""Runtime evaluator for dataset-profile capability hints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.dataset_profile import (
    capability_label,
    normalize_capabilities,
    normalize_device_type,
)


@dataclass(frozen=True)
class AnalysisCapabilityDecision:
    """Capability-gating decision for one analysis on one dataset profile."""

    allowed: bool
    recommended: bool
    status: str
    reasons: list[str]


def evaluate_analysis_capability_gating(
    analysis: dict[str, Any],
    *,
    dataset_profile: dict[str, Any],
) -> AnalysisCapabilityDecision:
    """Evaluate capability-based gating for one analysis."""
    capabilities = set(normalize_capabilities(dataset_profile.get("capabilities", [])))
    device_type = normalize_device_type(dataset_profile.get("device_type"))

    required = set(normalize_capabilities(analysis.get("required_capabilities", [])))
    excluded = set(normalize_capabilities(analysis.get("excluded_capabilities", [])))
    recommended_for = {
        normalize_device_type(raw_device_type)
        for raw_device_type in analysis.get("recommended_for", [])
    }

    missing = sorted(required - capabilities)
    blocked = sorted(excluded & capabilities)
    reasons: list[str] = []
    reasons.extend(f"Missing capability: {capability_label(capability)}" for capability in missing)
    reasons.extend(
        f"Excluded by capability: {capability_label(capability)}" for capability in blocked
    )

    allowed = not reasons
    recommended = allowed and device_type in recommended_for
    status = "recommended" if recommended else ("available" if allowed else "unavailable")
    return AnalysisCapabilityDecision(
        allowed=allowed,
        recommended=recommended,
        status=status,
        reasons=reasons,
    )
