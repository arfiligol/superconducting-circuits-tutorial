"""Tests for capability gating in analysis registry."""

from app.services.analysis_capability_evaluator import evaluate_analysis_capability_gating
from app.services.analysis_registry import ANALYSIS_REGISTRY


def _analysis_by_id(analysis_id: str) -> dict:
    return next(analysis for analysis in ANALYSIS_REGISTRY if analysis["id"] == analysis_id)


def test_squid_fitting_recommended_for_squid_profile() -> None:
    decision = evaluate_analysis_capability_gating(
        _analysis_by_id("squid_fitting"),
        dataset_profile={
            "device_type": "squid",
            "capabilities": [
                "y_parameter_characterization",
                "squid_characterization",
                "y11_response_fitting",
            ],
        },
    )

    assert decision.allowed is True
    assert decision.recommended is True
    assert decision.status == "recommended"
    assert decision.reasons == []


def test_squid_fitting_unavailable_when_squid_capability_missing() -> None:
    decision = evaluate_analysis_capability_gating(
        _analysis_by_id("squid_fitting"),
        dataset_profile={
            "device_type": "single_junction",
            "capabilities": ["y_parameter_characterization"],
        },
    )

    assert decision.allowed is False
    assert decision.recommended is False
    assert decision.status == "unavailable"
    assert any(
        "Profile hint: missing capability SQUID Characterization" in reason
        for reason in decision.reasons
    )


def test_y11_fit_unavailable_when_excluded_capability_present() -> None:
    decision = evaluate_analysis_capability_gating(
        _analysis_by_id("y11_fit"),
        dataset_profile={
            "device_type": "traveling_wave",
            "capabilities": [
                "y_parameter_characterization",
                "y11_response_fitting",
                "traveling_wave_gain",
            ],
        },
    )

    assert decision.allowed is False
    assert decision.status == "unavailable"
    assert any(
        "Profile hint: excluded by capability Traveling-wave Gain Characterization" in reason
        for reason in decision.reasons
    )
