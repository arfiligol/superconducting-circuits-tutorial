"""Analysis Registry for the SC Data Browser UI."""

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


ANALYSIS_REGISTRY = [
    {
        "id": "admittance_extraction",
        "label": "Admittance Extraction",
        "icon": "query_stats",
        "requires": {"data_type": "y_parameters", "representation": "imaginary"},
        "auto_run": True,
        "config_fields": [],
        "scope": "per_dataset",
        "description": "Finds resonance modes by identifying zero-crossings in Im(Y).",
        "completed_methods": ["admittance_zero_crossing"],
        "required_capabilities": ["y_parameter_characterization"],
        "excluded_capabilities": [],
        "recommended_for": ["single_junction", "squid", "resonator"],
    },
    {
        "id": "s21_resonance_fit",
        "label": "S21 Resonance Fit",
        "icon": "tune",
        "requires": {"data_type": "s_parameters", "parameter": ["S21", "S11"]},
        "auto_run": False,
        "config_fields": [
            {
                "name": "model",
                "label": "Model",
                "type": "select",
                "options": ["notch", "transmission"],
                "default": "notch",
            },
            {"name": "resonators", "label": "Resonators (N)", "type": "number", "default": 1},
            {"name": "f_min", "label": "f_min (GHz)", "type": "number", "default": None},
            {"name": "f_max", "label": "f_max (GHz)", "type": "number", "default": None},
        ],
        "scope": "per_dataset",
        "description": "Fits the S-parameter data to extract Qi, Qc, and fr.",
        "completed_methods": [
            "complex_notch_fit_S21",
            "transmission_fit_S21",
            "vector_fit_S21",
            "complex_notch_fit_S11",
            "transmission_fit_S11",
            "vector_fit_S11",
        ],
        "required_capabilities": ["s_parameter_characterization"],
        "excluded_capabilities": [],
        "recommended_for": ["traveling_wave", "resonator"],
    },
    {
        "id": "squid_fitting",
        "label": "SQUID Fitting",
        "icon": "science",
        "requires": {"data_type": "y_parameters", "representation": "imaginary"},
        "auto_run": False,
        "config_fields": [
            {
                "name": "fit_model",
                "label": "Model",
                "type": "select",
                "options": ["NO_LS", "WITH_LS", "FIXED_C"],
                "default": "WITH_LS",
            },
            {"name": "ls_min_nh", "label": "Ls min (nH)", "type": "number", "default": 0.0},
            {"name": "ls_max_nh", "label": "Ls max (nH)", "type": "number", "default": None},
            {"name": "c_min_pf", "label": "C min (pF)", "type": "number", "default": 0.0},
            {"name": "c_max_pf", "label": "C max (pF)", "type": "number", "default": None},
            {"name": "fixed_c_pf", "label": "Fixed C (pF)", "type": "number", "default": None},
            {
                "name": "fit_min_nh",
                "label": "Fit L_jun min (nH)",
                "type": "number",
                "default": None,
            },
            {
                "name": "fit_max_nh",
                "label": "Fit L_jun max (nH)",
                "type": "number",
                "default": None,
            },
        ],
        "scope": "per_dataset",
        "description": "Fits flux-dependent resonance frequencies to a SQUID-LC model.",
        "completed_methods": ["lc_squid_fit"],
        "required_capabilities": [
            "y_parameter_characterization",
            "squid_characterization",
        ],
        "excluded_capabilities": [],
        "recommended_for": ["squid"],
    },
    {
        "id": "y11_fit",
        "label": "Y11 Response Fit",
        "icon": "insights",
        "requires": {
            "data_type": "y_parameters",
            "parameter": ["Y11"],
            "representation": "imaginary",
        },
        "auto_run": False,
        "config_fields": [
            {
                "name": "ls1_init_nh",
                "label": "Ls1 init (nH)",
                "type": "number",
                "default": 0.01,
            },
            {
                "name": "ls2_init_nh",
                "label": "Ls2 init (nH)",
                "type": "number",
                "default": 0.01,
            },
            {"name": "c_init_pf", "label": "C init (pF)", "type": "number", "default": 0.885},
            {"name": "c_max_pf", "label": "C max (pF)", "type": "number", "default": 3.0},
        ],
        "scope": "per_dataset",
        "description": "Detailed fitting of the Y11 response over frequency and flux.",
        "completed_methods": ["y11_fit"],
        "required_capabilities": [
            "y_parameter_characterization",
            "y11_response_fitting",
        ],
        "excluded_capabilities": ["traveling_wave_gain"],
        "recommended_for": ["single_junction", "squid"],
    },
    {
        "id": "parameter_comparison",
        "label": "Parameter Comparison",
        "icon": "compare_arrows",
        "requires": {},  # cross_dataset bypasses standard record checks
        "auto_run": False,
        "config_fields": [
            {
                "name": "parameter",
                "label": "Parameter",
                "type": "select",
                "options": ["mode_1_ghz", "mode_ghz", "fr_ghz", "Qi", "Qc", "Ls_nH", "C_pF"],
                "default": "mode_1_ghz",
            }
        ],
        "scope": "cross_dataset",
        "description": "Compare derived parameters across multiple datasets.",
        "completed_methods": [],
        "required_capabilities": [],
        "excluded_capabilities": [],
        "recommended_for": [],
    },
]


def get_available_analyses(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Determine which analyses can be run on a given dataset's records."""
    available = []

    for analysis in ANALYSIS_REGISTRY:
        if analysis["scope"] != "per_dataset":
            continue

        reqs = analysis["requires"]

        found_match = False
        for r in records:
            match = True
            for k, v in reqs.items():
                if k == "parameter" and isinstance(v, list):
                    if r.get(k) not in v:
                        match = False
                elif r.get(k) != v:
                    match = False

            if match:
                found_match = True
                break

        if found_match:
            available.append(analysis)

    return available


def is_analysis_completed(analysis: dict[str, Any], params: list[Any]) -> bool:
    """Check if the dataset already contains derived parameters from this analysis."""
    completed_methods = analysis.get("completed_methods", [])
    if not completed_methods:
        return False

    return any(param.method in completed_methods for param in params)


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
