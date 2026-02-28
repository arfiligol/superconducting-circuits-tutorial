"""Analysis Registry for the SC Data Browser UI."""

from typing import Any

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
        ],
        "scope": "per_dataset",
        "description": "Fits flux-dependent resonance frequencies to a SQUID-LC model.",
        "completed_methods": ["squid_fit"],
    },
    {
        "id": "y11_fit",
        "label": "Y11 Response Fit",
        "icon": "insights",
        "requires": {"data_type": "y_parameters", "parameter": ["Y11"]},
        "auto_run": False,
        "config_fields": [],
        "scope": "per_dataset",
        "description": "Detailed fitting of the Y11 response over frequency and flux.",
        "completed_methods": ["y11_fit"],
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

    for param in params:
        if param.method in completed_methods:
            return True
    return False
