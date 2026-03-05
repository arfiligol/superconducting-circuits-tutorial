"""Characterization page — unified analysis + results view."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any
from uuid import uuid4

import pandas as pd
from nicegui import app, ui

from app.layout import app_shell
from app.pages.characterization.state import (
    AnalysisRunAvailability,
    AnalysisRunUiState,
    AnalysisScopeCompatibility,
    CharacterizationRuntimeState,
    ResultArtifact,
)
from app.services.analysis_capability_evaluator import evaluate_analysis_capability_gating
from app.services.analysis_registry import list_dataset_analyses
from app.services.characterization_trace_scope import (
    count_scope_trace_records,
    list_scope_compatible_trace_index_page,
)
from app.services.dataset_profile import normalize_dataset_profile, profile_summary_text
from core.analysis.application.services.characterization_fitting_service import (
    CharacterizationFittingService,
    SquidFittingConfig,
    Y11FittingConfig,
)
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import ParameterDesignation, ResultBundleRecord

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
METHOD_LABELS: dict[str, str] = {
    "admittance_zero_crossing": "Admittance Zero-Crossing",
    "lc_squid_fit": "SQUID Fitting",
    "y11_fit": "Y11 Response Fit",
    "complex_notch_fit_S21": "Complex Notch Fit (S21)",
    "complex_notch_fit_S11": "Complex Notch Fit (S11)",
    "transmission_fit_S21": "Transmission Fit (S21)",
    "transmission_fit_S11": "Transmission Fit (S11)",
    "vector_fit_S21": "Vector Fit (S21)",
    "vector_fit_S11": "Vector Fit (S11)",
}

_BIAS_RE = re.compile(r"^(.+?)_b(\d+)$")
_IDX_RE = re.compile(r"^(.+?)_(\d+)$")
_MODE_CANONICAL_RE = re.compile(r"^mode_(\d+)_ghz$")
_MODE_LEGACY_INDEX_RE = re.compile(r"^(?:mode_ghz|fr_ghz)_(\d+)$")
_MODE_LEGACY_SINGLE_RE = re.compile(r"^(?:mode_ghz|fr_ghz)$")
_ANALYSIS_RUN_SELECTED_KEY = "analysis_selected_run_by_dataset"
_ANALYSIS_RESULT_SELECTED_KEY = "analysis_selected_result_by_dataset"
_ANALYSIS_RESULT_CATEGORY_SELECTED_KEY = "analysis_selected_result_category_by_scope"
_ANALYSIS_RESULT_ARTIFACT_SELECTED_KEY = "analysis_selected_result_artifact_by_scope"
_ANALYSIS_RESULT_TRACE_MODE_SELECTED_KEY = "analysis_selected_result_trace_mode_by_scope"
_CATEGORY_LABELS: dict[str, str] = {
    "resonance": "Resonance",
    "fit": "Fitting",
    "summary": "Summary",
    "qa": "QA",
}
_CATEGORY_ORDER: dict[str, int] = {name: idx for idx, name in enumerate(_CATEGORY_LABELS)}
_TRACE_MODE_ALL = "all"
_TRACE_MODE_LABELS: dict[str, str] = {
    _TRACE_MODE_ALL: "All",
    "base": "Base",
    "sideband": "Sideband",
}
_TRACE_MODE_FILTER_OPTIONS: dict[str, str] = {
    _TRACE_MODE_ALL: "All Modes",
    "base": "Base",
    "sideband": "Sideband",
}
_MAX_BULK_TRACE_SELECTION = 2000
_ANALYSIS_CATEGORY_DEFAULTS: dict[str, str] = {
    "admittance_extraction": "resonance",
    "s21_resonance_fit": "fit",
    "squid_fitting": "fit",
    "y11_fit": "fit",
}


def _with_test_id(element: Any, test_id: str) -> Any:
    """Attach one stable test id to a NiceGUI element."""
    try:
        element.props(f"data-testid={test_id}")
    except Exception:
        props = getattr(element, "_props", None)
        if isinstance(props, dict):
            props["data-testid"] = test_id
    return element


def _result_view_controls_row_classes() -> str:
    """Shared responsive row classes for Result View controls."""
    return "w-full items-end gap-3 mt-3 mb-3 flex-wrap lg:flex-nowrap"


def _mode_index_from_key(name: str) -> int | None:
    match = _MODE_CANONICAL_RE.match(name)
    if match:
        return int(match.group(1))
    match = _MODE_LEGACY_INDEX_RE.match(name)
    if match:
        return int(match.group(1)) + 1
    if _MODE_LEGACY_SINGLE_RE.match(name):
        return 1
    return None


def _format_mode_label(name: str) -> str | None:
    mode_index = _mode_index_from_key(name)
    if mode_index is None:
        return None
    return f"Mode {mode_index} (GHz)"


def _display_param_name(name: str) -> str:
    mode_label = _format_mode_label(name)
    return mode_label if mode_label is not None else name


def _load_dataset_text_selection(storage_key: str, dataset_id: int) -> str:
    """Load one per-dataset string selection from user storage."""
    raw_map = app.storage.user.get(storage_key, {})
    if not isinstance(raw_map, dict):
        return ""
    selected = raw_map.get(str(dataset_id), "")
    return selected if isinstance(selected, str) else ""


def _save_dataset_text_selection(storage_key: str, dataset_id: int, token: str) -> None:
    """Save one per-dataset string selection into user storage."""
    raw_map = app.storage.user.get(storage_key, {})
    selected_map = dict(raw_map) if isinstance(raw_map, dict) else {}
    selected_map[str(dataset_id)] = token
    app.storage.user[storage_key] = selected_map


def _analysis_scope_key(dataset_id: int, analysis_id: str) -> str:
    """Build one stable scope key for dataset+analysis result-view state."""
    return f"{dataset_id}:{analysis_id}"


def _load_scope_text_selection(storage_key: str, scope_key: str) -> str:
    """Load one per-scope string selection from user storage."""
    raw_map = app.storage.user.get(storage_key, {})
    if not isinstance(raw_map, dict):
        return ""
    selected = raw_map.get(scope_key, "")
    return selected if isinstance(selected, str) else ""


def _save_scope_text_selection(storage_key: str, scope_key: str, token: str) -> None:
    """Save one per-scope string selection into user storage."""
    raw_map = app.storage.user.get(storage_key, {})
    selected_map = dict(raw_map) if isinstance(raw_map, dict) else {}
    selected_map[scope_key] = token
    app.storage.user[storage_key] = selected_map


def _resolve_selected_option(preferred: str, options: list[str]) -> str:
    """Resolve a selected option with graceful fallback."""
    if preferred in options:
        return preferred
    return options[0] if options else ""


def _effective_analysis_requires(
    *,
    analysis_id: str,
    analysis_requires: dict[str, object],
) -> dict[str, object]:
    """Resolve runtime requires overrides for one analysis id."""
    resolved_requires = dict(analysis_requires)
    if analysis_id == "s21_resonance_fit":
        # Current fit execution path is fixed to S21.
        resolved_requires["parameter"] = "S21"
    return resolved_requires


def _build_analysis_run_ui_state(
    *,
    has_compatible_traces: bool,
    selected_trace_count: int,
) -> AnalysisRunUiState:
    """Build availability text and run-button state from one compatibility source."""
    if not has_compatible_traces:
        return AnalysisRunUiState(
            has_compatible_traces=False,
            availability_text="Unavailable for current scope",
            availability_class="text-warning",
            run_disabled=True,
            run_hint="No compatible traces found for the selected analysis in current scope.",
        )
    if selected_trace_count <= 0:
        return AnalysisRunUiState(
            has_compatible_traces=True,
            availability_text="Available for current scope (no traces selected)",
            availability_class="text-positive",
            run_disabled=True,
            run_hint="Select at least one trace to run.",
        )
    return AnalysisRunUiState(
        has_compatible_traces=True,
        availability_text="Available for current scope",
        availability_class="text-positive",
        run_disabled=False,
        run_hint="Ready to run selected analysis.",
    )


def _build_analysis_run_availability(
    *,
    profile_recommended: bool,
    profile_hints: Sequence[str],
    has_compatible_traces: bool,
) -> AnalysisRunAvailability:
    """Merge profile recommendation hints and trace compatibility into one status."""
    if not has_compatible_traces:
        return AnalysisRunAvailability(
            status="Unavailable",
            reason="No compatible traces in current scope.",
            has_compatible_traces=False,
            profile_hints=list(profile_hints),
        )
    if profile_recommended:
        return AnalysisRunAvailability(
            status="Recommended",
            reason="Compatible traces found and dataset profile recommends this analysis.",
            has_compatible_traces=True,
            profile_hints=list(profile_hints),
        )
    reason = (
        "; ".join(profile_hints) if profile_hints else "Compatible traces found in current scope."
    )
    return AnalysisRunAvailability(
        status="Available",
        reason=reason,
        has_compatible_traces=True,
        profile_hints=list(profile_hints),
    )


def _is_sideband_trace_parameter(parameter: str) -> bool:
    """Return True when parameter name contains mode suffix metadata."""
    return " [om=" in parameter or " [im=" in parameter


def _normalize_trace_mode_group(raw_value: object) -> str:
    """Normalize trace mode provenance token used by filters and persistence."""
    normalized = str(raw_value or "").strip().lower()
    if normalized in ("base", "signal"):
        return "base"
    if normalized == "sideband":
        return "sideband"
    return ""


def _trace_mode_group_for_selected_rows(rows: Sequence[dict[str, str | int]]) -> str:
    """Resolve one aggregate mode group for currently selected trace rows."""
    has_sideband = any(str(row.get("mode", "")) == "Sideband" for row in rows)
    return "sideband" if has_sideband else "base"


def _param_trace_mode_group(param: object) -> str:
    """Extract persisted trace mode provenance from one DerivedParameter-like object."""
    extra = getattr(param, "extra", {})
    if isinstance(extra, dict):
        return _normalize_trace_mode_group(extra.get("trace_mode_group"))
    return ""


def _trace_mode_filter_options(method_groups: dict[str, list]) -> dict[str, str]:
    """Build stable trace-mode filter options from one method-group payload."""
    present_modes = {
        _param_trace_mode_group(param) for params in method_groups.values() for param in params
    }
    available_keys = [_TRACE_MODE_ALL]
    for mode_key in ("base", "sideband"):
        if mode_key in present_modes:
            available_keys.append(mode_key)
    return {key: _TRACE_MODE_LABELS[key] for key in available_keys}


def _filter_method_groups_by_trace_mode(
    method_groups: dict[str, list],
    *,
    trace_mode_filter: str,
) -> dict[str, list]:
    """Filter one analysis method-group mapping by persisted trace mode provenance."""
    normalized_mode = _normalize_trace_mode_group(trace_mode_filter)
    if trace_mode_filter == _TRACE_MODE_ALL:
        return {method_key: list(params) for method_key, params in method_groups.items()}

    filtered: dict[str, list] = {}
    for method_key, params in method_groups.items():
        selected = [param for param in params if _param_trace_mode_group(param) == normalized_mode]
        if selected:
            filtered[method_key] = selected
    return filtered


def _trace_row_mode_key(row: Mapping[str, str | int]) -> str:
    """Resolve canonical mode key for one trace row."""
    return "sideband" if str(row.get("mode", "")) == "Sideband" else "base"


def _filter_trace_rows_by_mode(
    rows: Sequence[dict[str, str | int]],
    *,
    mode_filter: str,
) -> list[dict[str, str | int]]:
    """Filter trace rows by canonical mode filter (`all`/`base`/`sideband`)."""
    if mode_filter == _TRACE_MODE_ALL:
        return list(rows)
    normalized = _normalize_trace_mode_group(mode_filter)
    if not normalized:
        return list(rows)
    return [row for row in rows if _trace_row_mode_key(row) == normalized]


def _trace_rows_for_view(
    rows: list[dict[str, str | int]],
    *,
    search: str,
    mode_filter: str,
    sort_by: str,
    descending: bool,
) -> list[dict[str, str | int]]:
    """Filter and sort trace rows for table rendering."""
    filtered_rows = list(rows)
    search_text = search.strip().lower()
    if search_text:
        filtered_rows = [
            row
            for row in filtered_rows
            if search_text in str(row.get("parameter", "")).lower()
            or search_text in str(row.get("representation", "")).lower()
            or search_text in str(row.get("id", "")).lower()
        ]
    if mode_filter:
        filtered_rows = _filter_trace_rows_by_mode(filtered_rows, mode_filter=mode_filter)

    if sort_by == "mode":
        filtered_rows.sort(
            key=lambda row: _trace_row_mode_key(row),
            reverse=descending,
        )
    elif sort_by == "parameter":
        filtered_rows.sort(
            key=lambda row: str(row.get("parameter", "")).lower(),
            reverse=descending,
        )
    elif sort_by == "representation":
        filtered_rows.sort(
            key=lambda row: str(row.get("representation", "")).lower(),
            reverse=descending,
        )
    else:
        filtered_rows.sort(
            key=lambda row: int(row["id"]) if isinstance(row.get("id"), int) else 0,
            reverse=descending,
        )
    return filtered_rows


def _to_int(value: object, default: int) -> int:
    """Convert to int with fallback for UI state values."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _build_analysis_run_bundle_record(
    *,
    dataset_id: int,
    analysis_id: str,
    analysis_label: str,
    run_id: str,
    selected_bundle_id: int | None,
    selected_scope_token: str,
    config_snapshot: dict[str, object],
) -> ResultBundleRecord:
    """Build a provenance bundle for one Characterization run."""
    return ResultBundleRecord(
        dataset_id=dataset_id,
        bundle_type="characterization",
        role="analysis_run",
        status="completed",
        source_meta={
            "origin": "characterization",
            "analysis_id": analysis_id,
            "analysis_label": analysis_label,
            "run_id": run_id,
            "input_bundle_id": selected_bundle_id,
            "input_scope": selected_scope_token,
        },
        config_snapshot=config_snapshot,
        result_payload={},
    )


# ---------------------------------------------------------------------------
# Data helpers (from former parameters.py)
# ---------------------------------------------------------------------------


def _group_by_method(params):
    groups: dict[str, list] = defaultdict(list)
    for p in params:
        groups[p.method or "unknown"].append(p)
    return dict(sorted(groups.items()))


def _build_bias_dataframe(params) -> pd.DataFrame | None:
    rows: dict[str, dict[int, float]] = defaultdict(dict)
    l_jun_values: dict[int, float] = {}
    l_jun_unit: str = "nH"

    for p in params:
        m = _BIAS_RE.match(p.name)
        if m:
            base, bias = m.group(1), int(m.group(2))
            if base == "L_jun":
                l_jun_values[bias] = p.value
                if p.unit:
                    l_jun_unit = p.unit
            else:
                rows[base][bias] = p.value

    if not rows:
        return None

    df = pd.DataFrame.from_dict(rows, orient="index")
    df = df.reindex(sorted(df.columns), axis=1)
    col_map: dict[object, str]

    if l_jun_values:
        col_map = {
            b: f"{l_jun_values[b]:.4g} ({l_jun_unit})" for b in df.columns if b in l_jun_values
        }
        for column_name in df.columns:
            if column_name not in col_map:
                col_map[column_name] = f"B{column_name}"
    else:
        col_map = {b: f"B{b}" for b in df.columns}
    df = df.rename(columns=col_map)

    new_index = []
    for idx in df.index:
        new_index.append(_display_param_name(str(idx)))
    df.index = new_index
    df.index.name = "Parameter"
    return df


def _build_resonator_table(params) -> pd.DataFrame | None:
    cells: dict[int, dict[str, float]] = defaultdict(dict)
    for p in params:
        if _BIAS_RE.match(p.name):
            continue

        mode_index = _mode_index_from_key(p.name)
        if mode_index is not None:
            cells[mode_index]["mode_ghz"] = p.value
            continue

        m2 = _IDX_RE.match(p.name)
        if m2:
            base, idx = m2.group(1), int(m2.group(2))
            cells[idx][base] = p.value

    if not cells:
        return None

    df = pd.DataFrame.from_dict(cells, orient="index")
    df.index.name = "Resonator"
    df = df.sort_index()

    if "mode_ghz" in df.columns:
        df = df.rename(columns={"mode_ghz": "Mode (GHz)"})

    preferred = ["Mode (GHz)", "Qi", "Qc", "Ql"]
    cols_ordered = [c for c in preferred if c in df.columns]
    cols_ordered += [c for c in sorted(df.columns) if c not in cols_ordered]
    return df[cols_ordered]


def _build_fit_parameter_table(params: list) -> pd.DataFrame | None:
    """Build per-fit parameter summary table using DerivedParameter.extra metadata."""
    rows: dict[str, dict[str, float]] = defaultdict(dict)

    for param in params:
        extra = param.extra if isinstance(getattr(param, "extra", {}), dict) else {}
        row_key = str(extra.get("mode") or "Y11")
        name = str(param.name)
        if name in {"Ls_nH", "C_eff_pF", "Ls1_nH", "Ls2_nH", "C_pF", "RMSE"}:
            rows[row_key][name] = float(param.value)
        if "rmse" in extra:
            rows[row_key]["RMSE"] = float(extra["rmse"])

    if not rows:
        return None

    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "Trace"
    preferred_cols = ["Ls_nH", "C_eff_pF", "Ls1_nH", "Ls2_nH", "C_pF", "RMSE"]
    ordered_cols = [name for name in preferred_cols if name in df.columns]
    ordered_cols += [name for name in sorted(df.columns) if name not in ordered_cols]
    return df[ordered_cols].sort_index()


# ---------------------------------------------------------------------------
# Result Artifact helpers
# ---------------------------------------------------------------------------


def _build_mode_vs_ljun_dataframe(params: list) -> pd.DataFrame | None:
    """Build canonical Mode-vs-L_jun table; synthesize a single-column form when needed."""
    bias_df = _build_bias_dataframe(params)
    if bias_df is not None and not bias_df.empty:
        return bias_df

    mode_by_index: dict[int, float] = {}
    l_jun_value: float | None = None
    l_jun_unit = "nH"
    for param in params:
        mode_index = _mode_index_from_key(str(param.name))
        if mode_index is not None:
            mode_by_index[mode_index] = float(param.value)
            continue
        if str(param.name) == "L_jun":
            l_jun_value = float(param.value)
            if getattr(param, "unit", None):
                l_jun_unit = str(param.unit)

    if not mode_by_index:
        return None

    sorted_modes = sorted(mode_by_index)
    col_label = (
        f"{l_jun_value:.4g} ({l_jun_unit})" if l_jun_value is not None else f"L_jun ({l_jun_unit})"
    )
    mode_rows = [f"Mode {mode_index} (GHz)" for mode_index in sorted_modes]
    values = [mode_by_index[mode_index] for mode_index in sorted_modes]
    df = pd.DataFrame({col_label: values}, index=mode_rows)
    df.index.name = "Parameter"
    return df


def _default_analysis_category(analysis_id: str) -> str:
    """Resolve default category for one analysis id."""
    return _ANALYSIS_CATEGORY_DEFAULTS.get(analysis_id, "summary")


def _build_result_artifacts_for_analysis(
    *,
    analysis_id: str,
    method_groups: dict[str, list],
) -> list[ResultArtifact]:
    """Build declarative artifact manifest for one analysis."""
    method_keys = sorted(method_groups)
    if not method_keys:
        return []

    artifacts: list[ResultArtifact] = []
    default_category = _default_analysis_category(analysis_id)
    method_count = len(method_keys)

    for method_key in method_keys:
        method_params = list(method_groups[method_key])
        method_label = METHOD_LABELS.get(method_key, method_key)

        mode_vs_ljun_df = _build_mode_vs_ljun_dataframe(method_params)
        if mode_vs_ljun_df is not None and not mode_vs_ljun_df.empty:
            artifacts.append(
                ResultArtifact(
                    artifact_id=f"{analysis_id}.{method_key}.mode_vs_ljun",
                    analysis_id=analysis_id,
                    category=default_category,
                    view_kind="matrix_table_plot",
                    tab_label=(
                        "Mode vs L_jun" if method_count == 1 else f"Mode vs L_jun ({method_label})"
                    ),
                    title="Mode vs L_jun",
                    subtitle=method_label if method_count > 1 else None,
                    query_spec={
                        "method_key": method_key,
                        "dataset": "derived_parameters",
                        "shape": "mode_vs_ljun",
                    },
                    meta={
                        "row_count": int(mode_vs_ljun_df.shape[0]),
                        "col_count": int(mode_vs_ljun_df.shape[1]),
                        "is_sweep": int(mode_vs_ljun_df.shape[1]) > 1,
                    },
                )
            )

        resonator_df = _build_resonator_table(method_params)
        if resonator_df is not None and not resonator_df.empty:
            artifacts.append(
                ResultArtifact(
                    artifact_id=f"{analysis_id}.{method_key}.resonator_summary",
                    analysis_id=analysis_id,
                    category=default_category,
                    view_kind="record_table",
                    tab_label=(
                        "Resonator Summary"
                        if method_count == 1
                        else f"Resonator Summary ({method_label})"
                    ),
                    title="Per-Resonator Summary",
                    subtitle=method_label if method_count > 1 else None,
                    query_spec={
                        "method_key": method_key,
                        "dataset": "derived_parameters",
                        "shape": "resonator_summary",
                    },
                    meta={
                        "row_count": int(resonator_df.shape[0]),
                        "col_count": int(resonator_df.shape[1]),
                    },
                )
            )

        fit_df = _build_fit_parameter_table(method_params)
        if fit_df is not None and not fit_df.empty:
            artifacts.append(
                ResultArtifact(
                    artifact_id=f"{analysis_id}.{method_key}.fit_parameters",
                    analysis_id=analysis_id,
                    category=default_category,
                    view_kind="record_table",
                    tab_label=(
                        "Fit Parameters"
                        if method_count == 1
                        else f"Fit Parameters ({method_label})"
                    ),
                    title="Fit Parameters",
                    subtitle=method_label if method_count > 1 else None,
                    query_spec={
                        "method_key": method_key,
                        "dataset": "derived_parameters",
                        "shape": "fit_parameters",
                    },
                    meta={
                        "row_count": int(fit_df.shape[0]),
                        "col_count": int(fit_df.shape[1]),
                    },
                )
            )

        scalars = [
            param
            for param in method_params
            if not _BIAS_RE.match(str(param.name)) and not _IDX_RE.match(str(param.name))
        ]
        if scalars:
            artifacts.append(
                ResultArtifact(
                    artifact_id=f"{analysis_id}.{method_key}.summary_metrics",
                    analysis_id=analysis_id,
                    category="summary",
                    view_kind="scalar_cards",
                    tab_label=(
                        "Summary Metrics"
                        if method_count == 1
                        else f"Summary Metrics ({method_label})"
                    ),
                    title="Summary Metrics",
                    subtitle=method_label if method_count > 1 else None,
                    query_spec={
                        "method_key": method_key,
                        "dataset": "derived_parameters",
                        "shape": "summary_metrics",
                    },
                    meta={"count": len(scalars)},
                )
            )

    artifacts.sort(
        key=lambda artifact: (
            _CATEGORY_ORDER.get(artifact.category, len(_CATEGORY_ORDER)),
            artifact.tab_label.lower(),
        )
    )
    return artifacts


def _artifact_categories(artifacts: list[ResultArtifact]) -> list[str]:
    """Return sorted category keys from artifact manifest."""
    unique = {artifact.category for artifact in artifacts}
    return sorted(unique, key=lambda category: _CATEGORY_ORDER.get(category, len(_CATEGORY_ORDER)))


def _artifacts_in_category(
    artifacts: list[ResultArtifact],
    *,
    category: str,
) -> list[ResultArtifact]:
    """Return artifacts belonging to one category."""
    return [artifact for artifact in artifacts if artifact.category == category]


def _result_view_empty_state_message(
    *,
    selected_mode_label: str,
    selected_analysis_groups_raw: Mapping[str, list],
    selected_analysis_groups: Mapping[str, list],
) -> str:
    """Build one diagnosable empty-state message for Result View."""
    if selected_analysis_groups:
        method_keys = ", ".join(sorted(str(method_key) for method_key in selected_analysis_groups))
        return (
            "Persisted results found but no renderable artifacts for selected analysis "
            f"(methods: {method_keys})."
        )
    if selected_analysis_groups_raw:
        return (
            f"No artifacts available for selected analysis under trace mode: {selected_mode_label}."
        )
    return "No artifacts available for selected analysis."


class ResultViewQueryService:
    """Lazy payload loader for result artifacts."""

    def __init__(self, method_groups: dict[str, list]) -> None:
        self._method_groups = method_groups
        self._cache: dict[str, dict[str, Any]] = {}

    def load_payload(self, artifact: ResultArtifact) -> dict[str, Any]:
        """Load payload for one artifact with in-memory cache."""
        cached = self._cache.get(artifact.artifact_id)
        if cached is not None:
            return cached

        method_key = str(artifact.query_spec.get("method_key", ""))
        method_params = list(self._method_groups.get(method_key, []))
        payload: dict[str, Any]
        if artifact.view_kind == "matrix_table_plot":
            payload = {
                "dataframe": _build_mode_vs_ljun_dataframe(method_params),
                "method_params": method_params,
            }
        elif artifact.view_kind == "record_table":
            shape = str(artifact.query_spec.get("shape", ""))
            if shape == "fit_parameters":
                payload = {"dataframe": _build_fit_parameter_table(method_params)}
            else:
                payload = {"dataframe": _build_resonator_table(method_params)}
        elif artifact.view_kind == "scalar_cards":
            payload = {
                "scalars": [
                    param
                    for param in method_params
                    if not _BIAS_RE.match(str(param.name)) and not _IDX_RE.match(str(param.name))
                ]
            }
        else:
            payload = {}

        self._cache[artifact.artifact_id] = payload
        return payload


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _render_table_df(df: pd.DataFrame, suppress_auto_header: bool = False):
    display = df.copy().reset_index()

    # Keep numeric cells numeric so ui.table sorting stays numeric (not lexicographic).
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col].dtype):
            display[col] = display[col].apply(lambda v: round(float(v), 6) if pd.notna(v) else None)

    columns = [
        {
            "name": str(column_name),
            "label": "" if suppress_auto_header and idx == 0 else str(column_name),
            "field": str(column_name),
            "align": "left",
            "sortable": True,
            "headerClasses": (
                "text-primary text-xs font-bold uppercase tracking-wider select-none"
            ),
            "classes": "text-fg",
        }
        for idx, column_name in enumerate(display.columns)
    ]
    rows = [
        {str(column_name): value for column_name, value in row.items()}
        for row in display.to_dict(orient="records")
    ]
    with ui.element("div").classes("w-full overflow-x-auto"):
        ui.table(columns=columns, rows=rows, pagination=20).classes(
            "w-full min-w-[640px] rounded-xl border border-border bg-surface"
        ).props("dense flat bordered separator=horizontal")


def _render_metric_cards(params):
    with ui.row().classes("w-full gap-4 flex-wrap"):
        for p in sorted(params, key=lambda x: x.name):
            with ui.column().classes("app-card p-4 min-w-[140px] flex-grow flex-shrink"):
                ui.label(_display_param_name(p.name)).classes(
                    "text-xs text-muted font-bold uppercase"
                )
                val = f"{p.value:.4g}" if isinstance(p.value, float) else str(p.value)
                with ui.row().classes("items-baseline gap-1 mt-1"):
                    ui.label(val).classes("text-xl font-bold text-fg")
                    if p.unit:
                        ui.label(p.unit).classes("text-xs text-muted")


def _render_bias_plotly(df: pd.DataFrame):
    import plotly.graph_objects as go

    from core.shared.visualization import get_plotly_layout

    x_labels = list(df.columns)
    x_numeric = []
    has_valid_numeric_x = False
    for label in x_labels:
        try:
            val = float(str(label).split()[0])
            x_numeric.append(val)
        except (ValueError, IndexError):
            x_numeric.append(label)

    if all(isinstance(x, int | float) for x in x_numeric):
        x_data = x_numeric
        has_valid_numeric_x = True
    else:
        x_data = x_labels

    fig = go.Figure()
    for idx, row in df.iterrows():
        mode_label = str(idx).replace(" (GHz)", "")
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=row.values,
                mode="markers",
                marker={"size": 8},
                name=mode_label,
                hovertemplate=(
                    f"<b>{mode_label}</b><br>Bias: %{{x}}<br>Freq: %{{y:.4g}} GHz<extra></extra>"
                ),
            )
        )

    is_dark = app.storage.user.get("dark_mode", True)
    theme_layout = get_plotly_layout(dark=is_dark)
    fig.update_layout(
        title="Mode Frequencies vs. Bias",
        xaxis_title="L_jun (nH)" if has_valid_numeric_x else "Bias Index",
        yaxis_title="Frequency (GHz)",
        margin=dict(l=60, r=150, t=60, b=60),
        height=400,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
    )
    fig.update_layout(**theme_layout)  # type: ignore[arg-type]
    if not has_valid_numeric_x:
        fig.update_xaxes(type="category")

    ui.plotly(fig).classes("w-full")


# ---------------------------------------------------------------------------
# Identify Mode UI
# ---------------------------------------------------------------------------


def _render_identify_mode(ds, method: str, params: list, bias_df):
    """Render the Identify Mode UI for tagging modes with physical meaning."""
    ui.separator().classes("my-4 bg-border")
    with ui.row().classes("w-full items-center justify-between"):
        ui.label("Identify Mode").classes("text-xs text-muted font-bold uppercase tracking-wider")

    with ui.row().classes("w-full items-end gap-4 mt-2 p-4 bg-bg rounded-xl border border-border"):

        def extract_base_param(name: str) -> str:
            m_bias = _BIAS_RE.match(name)
            if m_bias:
                return m_bias.group(1)
            m_idx = _IDX_RE.match(name)
            if m_idx:
                return m_idx.group(1)
            return name

        def format_base_param(base_name: str) -> str:
            return _display_param_name(base_name)

        unique_bases = {extract_base_param(p.name) for p in params}
        param_options = {base: format_base_param(base) for base in sorted(unique_bases)}

        if not param_options:
            ui.label("No parameters to tag").classes("text-muted text-sm")
        else:
            source_select = ui.select(param_options, label="Source Parameter").classes("w-64")

            tag_options = [
                "f_q (Qubit frequency)",
                "f_r (Readout frequency)",
                "alpha (Anharmonicity)",
                "g (Coupling strength)",
            ]
            tag_select = ui.select(tag_options, label="Designated Metric", with_input=True).classes(
                "w-64"
            )

            def save_designation():
                if not source_select.value or not tag_select.value:
                    ui.notify("Please select both a parameter and a tag", type="warning")
                    return

                true_tag = tag_select.value.split(" (")[0].strip()

                try:
                    with get_unit_of_work() as uow:
                        existing = (
                            uow._session.query(ParameterDesignation)
                            .filter_by(
                                dataset_id=ds.id,
                                designated_name=true_tag,
                                source_analysis_type=method,
                                source_parameter_name=source_select.value,
                            )
                            .first()
                        )

                        if existing:
                            ui.notify(
                                f"Tag '{true_tag}' already exists for {source_select.value}",
                                type="info",
                            )
                            return

                        desig = ParameterDesignation(
                            dataset_id=ds.id,
                            designated_name=true_tag,
                            source_analysis_type=method,
                            source_parameter_name=source_select.value,
                        )
                        uow._session.add(desig)
                        uow.commit()
                        ui.notify(
                            f"Successfully designated {source_select.value} as '{true_tag}'",
                            type="positive",
                        )

                        source_select.value = None
                        tag_select.value = None
                except Exception as e:
                    ui.notify(f"Error saving designation: {e}", type="negative")

            ui.button("Tag Parameter", icon="sell", on_click=save_designation).props(
                "outline color=primary size=sm"
            ).classes("mb-1")


# ---------------------------------------------------------------------------
# Result artifact renderer
# ---------------------------------------------------------------------------


def _render_result_artifact(
    *,
    ds,
    artifact: ResultArtifact,
    payload: dict[str, Any],
) -> None:
    """Render one artifact payload using view-kind specific renderer."""
    with (
        ui.row().classes("w-full items-center justify-between gap-3 flex-wrap mb-2"),
        ui.column().classes("gap-1"),
    ):
        ui.label(artifact.title).classes("text-xs text-muted font-bold uppercase tracking-wider")
        if artifact.subtitle:
            ui.label(artifact.subtitle).classes("text-xs text-muted")

    if artifact.view_kind == "matrix_table_plot":
        bias_df = payload.get("dataframe")
        if not isinstance(bias_df, pd.DataFrame) or bias_df.empty:
            ui.label("No rows available for this artifact.").classes("text-sm text-muted")
            return
        toggle = ui.toggle(["Table", "Plot"], value="Table").props(
            "size=md no-caps outline color=primary"
        )
        with ui.column().classes("w-full"):

            @ui.refreshable
            def render_matrix_view():
                if toggle.value == "Table":
                    _render_table_df(bias_df, suppress_auto_header=True)
                else:
                    _render_bias_plotly(bias_df)

            toggle.on_value_change(lambda _: render_matrix_view.refresh())
            render_matrix_view()

        method_params = payload.get("method_params")
        if isinstance(method_params, list):
            method_key = str(artifact.query_spec.get("method_key", ""))
            _render_identify_mode(ds, method_key, method_params, bias_df)
        return

    if artifact.view_kind == "record_table":
        resonator_df = payload.get("dataframe")
        if not isinstance(resonator_df, pd.DataFrame) or resonator_df.empty:
            ui.label("No rows available for this artifact.").classes("text-sm text-muted")
            return
        _render_table_df(resonator_df)
        return

    if artifact.view_kind == "scalar_cards":
        scalars = payload.get("scalars")
        if isinstance(scalars, list) and scalars:
            _render_metric_cards(scalars)
        else:
            ui.label("No scalar metrics available for this artifact.").classes("text-sm text-muted")
        return

    ui.label(f"Unsupported artifact view kind: {artifact.view_kind}").classes("text-warning")


# ---------------------------------------------------------------------------
# Analysis execution
# ---------------------------------------------------------------------------


def _execute_analysis_run(
    *,
    analysis_id: str,
    dataset_id: int,
    config_state: dict[str, str | float | int | None],
    trace_record_ids: list[int] | None = None,
    trace_mode_group: str | None = None,
) -> None:
    """Execute one analysis run using dataset-scoped records."""

    def _config_int(name: str, default: int) -> int:
        value = config_state.get(name)
        if value is None:
            return default
        return int(value)

    def _config_float(name: str) -> float | None:
        value = config_state.get(name)
        if value is None:
            return None
        return float(value)

    def _config_str(name: str, default: str) -> str:
        value = config_state.get(name)
        if value is None:
            return default
        return str(value)

    if analysis_id == "admittance_extraction":
        ResonanceExtractService().extract_admittance(
            str(dataset_id),
            record_ids=trace_record_ids,
            trace_mode_group=trace_mode_group,
        )
        return

    if analysis_id == "s21_resonance_fit":
        ResonanceFitService().perform_fit(
            dataset_identifier=str(dataset_id),
            parameter="S21",
            model=_config_str("model", "notch"),
            resonators=_config_int("resonators", 1),
            f_min=_config_float("f_min"),
            f_max=_config_float("f_max"),
            record_ids=trace_record_ids,
        )
        return

    if analysis_id == "squid_fitting":
        CharacterizationFittingService().run_squid_fitting(
            dataset_id=dataset_id,
            config=SquidFittingConfig(
                fit_model=_config_str("fit_model", "WITH_LS"),
                ls_min_nh=_config_float("ls_min_nh"),
                ls_max_nh=_config_float("ls_max_nh"),
                c_min_pf=_config_float("c_min_pf"),
                c_max_pf=_config_float("c_max_pf"),
                fixed_c_pf=_config_float("fixed_c_pf"),
                fit_min_nh=_config_float("fit_min_nh"),
                fit_max_nh=_config_float("fit_max_nh"),
            ),
            record_ids=trace_record_ids,
            trace_mode_group=trace_mode_group,
        )
        return

    if analysis_id == "y11_fit":
        CharacterizationFittingService().run_y11_fitting(
            dataset_id=dataset_id,
            config=Y11FittingConfig(
                ls1_init_nh=float(_config_float("ls1_init_nh") or 0.01),
                ls2_init_nh=float(_config_float("ls2_init_nh") or 0.01),
                c_init_pf=float(_config_float("c_init_pf") or 0.885),
                c_max_pf=float(_config_float("c_max_pf") or 3.0),
            ),
            record_ids=trace_record_ids,
            trace_mode_group=trace_mode_group,
        )
        return

    raise ValueError(f"Unsupported analysis id: {analysis_id}")


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------


@ui.page("/characterization")
def characterization_page():
    def content():
        ui.label("Characterization").classes("text-2xl font-bold text-fg mb-6")

        selected_dataset_ids = app.storage.user.get("selected_datasets", [])
        runtime_state = CharacterizationRuntimeState.create()

        def append_analysis_status(level: str, message: str) -> None:
            runtime_state.append_status(
                level=level,
                message=message,
                time_label=pd.Timestamp.now().strftime("%H:%M:%S"),
            )
            render_analysis_status()

        def render_analysis_status() -> None:
            if runtime_state.analysis_log_container is None:
                return

            icon_map = {
                "info": "info",
                "warning": "warning",
                "negative": "error",
                "positive": "check_circle",
            }
            color_map = {
                "info": "text-primary",
                "warning": "text-warning",
                "negative": "text-danger",
                "positive": "text-positive",
            }

            runtime_state.analysis_log_container.clear()
            with runtime_state.analysis_log_container:
                if not runtime_state.analysis_status_history:
                    ui.label("No analysis logs yet. Run one analysis to see status.").classes(
                        "text-sm text-muted"
                    )
                    return

                for item in runtime_state.analysis_status_history:
                    with ui.row().classes("w-full items-start gap-2"):
                        ui.icon(icon_map.get(item["level"], "info"), size="xs").classes(
                            color_map.get(item["level"], "text-primary mt-1")
                        )
                        ui.label(f"[{item['time']}] {item['message']}").classes(
                            "text-sm text-fg whitespace-pre-wrap break-all"
                        )

        if not selected_dataset_ids:
            with ui.column().classes(
                "w-full p-12 items-center justify-center "
                "border-2 border-dashed border-border rounded-xl"
            ):
                ui.icon("science", size="xl").classes("text-muted mb-4 opacity-50")
                ui.label("No Datasets Selected").classes("text-xl text-fg font-bold")
                ui.label("Select active datasets from the header or the Raw Data page.").classes(
                    "text-sm text-muted mt-2"
                )
            return

        try:
            with get_unit_of_work() as uow:
                ds_options = {}
                for ds_id in selected_dataset_ids:
                    ds = uow.datasets.get(ds_id)
                    if ds:
                        ds_options[ds_id] = ds.name

                if not ds_options:
                    ui.label("Error: Active datasets not found.").classes("text-danger")
                    return

                current_ds_id = app.storage.user.get("analysis_current_dataset")
                if current_ds_id not in ds_options:
                    current_ds_id = next(iter(ds_options.keys()))
                    app.storage.user["analysis_current_dataset"] = current_ds_id

                @ui.refreshable
                def render_dataset_view():
                    nonlocal runtime_state
                    active_id = app.storage.user.get("analysis_current_dataset")
                    if not active_id or active_id not in ds_options:
                        return

                    with get_unit_of_work() as refresh_uow:
                        ds = refresh_uow.datasets.get(active_id)
                        if not ds:
                            return

                        dataset_profile_index = (
                            refresh_uow.data_records.list_distinct_index_for_profile(active_id)
                        )
                        bundles = refresh_uow.result_bundles.list_by_dataset(active_id)
                        selected_bundle_id = None
                        selected_scope_token = "all_dataset_records"
                        scoped_trace_count = count_scope_trace_records(
                            uow=refresh_uow,
                            dataset_id=active_id,
                            selected_bundle_id=selected_bundle_id,
                        )

                        ds_params = refresh_uow.derived_params.list_by_dataset(active_id)
                        method_params = _group_by_method(ds_params)
                        analyses = list_dataset_analyses()
                        if not analyses:
                            ui.label("No per-dataset analyses are registered.").classes(
                                "text-danger"
                            )
                            return
                        dataset_profile = normalize_dataset_profile(
                            ds.source_meta,
                            record_index=dataset_profile_index,
                        )

                        analysis_scope_compatibility: dict[str, AnalysisScopeCompatibility] = {}
                        analysis_run_availability_by_id: dict[str, AnalysisRunAvailability] = {}
                        scope_revision = f"{scoped_trace_count}:{selected_scope_token}"
                        for analysis in analyses:
                            analysis_id = str(analysis["id"])
                            effective_requires = _effective_analysis_requires(
                                analysis_id=analysis_id,
                                analysis_requires=dict(analysis.get("requires", {})),
                            )
                            compatibility_cache_key = (
                                f"{active_id}:{selected_scope_token}:{scope_revision}:{analysis_id}"
                            )
                            compatibility = runtime_state.analysis_scope_compatibility_cache.get(
                                compatibility_cache_key
                            )
                            if compatibility is None:
                                _, compatible_trace_count = list_scope_compatible_trace_index_page(
                                    uow=refresh_uow,
                                    dataset_id=active_id,
                                    selected_bundle_id=selected_bundle_id,
                                    analysis_requires=effective_requires,
                                    limit=1,
                                    offset=0,
                                )
                                has_compatible_traces = compatible_trace_count > 0
                                compatibility = AnalysisScopeCompatibility(
                                    compatible_trace_rows=[],
                                    compatible_trace_count=compatible_trace_count,
                                    has_compatible_traces=has_compatible_traces,
                                    status=(
                                        "available" if has_compatible_traces else "unavailable"
                                    ),
                                    message=(
                                        "Available for current scope"
                                        if has_compatible_traces
                                        else "Unavailable for current scope"
                                    ),
                                )
                                runtime_state.analysis_scope_compatibility_cache[
                                    compatibility_cache_key
                                ] = compatibility
                            analysis_scope_compatibility[analysis_id] = compatibility
                            capability_decision = evaluate_analysis_capability_gating(
                                analysis,
                                dataset_profile=dataset_profile,
                            )
                            analysis_run_availability_by_id[analysis_id] = (
                                _build_analysis_run_availability(
                                    profile_recommended=capability_decision.recommended,
                                    profile_hints=capability_decision.reasons,
                                    has_compatible_traces=compatibility.has_compatible_traces,
                                )
                            )

                        analysis_options = {
                            str(analysis["id"]): (
                                f"{analysis['label']} "
                                f"[{analysis_run_availability_by_id[str(analysis['id'])].status}]"
                            )
                            for analysis in analyses
                        }
                        analysis_ids = list(analysis_options)
                        selected_run_analysis_id = _resolve_selected_option(
                            _load_dataset_text_selection(_ANALYSIS_RUN_SELECTED_KEY, active_id),
                            analysis_ids,
                        )
                        _save_dataset_text_selection(
                            _ANALYSIS_RUN_SELECTED_KEY,
                            active_id,
                            selected_run_analysis_id,
                        )
                        selected_run_analysis = next(
                            (
                                analysis
                                for analysis in analyses
                                if str(analysis["id"]) == selected_run_analysis_id
                            ),
                            analyses[0],
                        )
                        selected_run_availability = analysis_run_availability_by_id[
                            selected_run_analysis_id
                        ]
                        selected_analysis_requires = _effective_analysis_requires(
                            analysis_id=selected_run_analysis_id,
                            analysis_requires=dict(selected_run_analysis.get("requires", {})),
                        )

                        def _compatible_trace_page(
                            *,
                            search: str = "",
                            sort_by: str = "id",
                            descending: bool = False,
                            mode_filter: str = _TRACE_MODE_ALL,
                            ids: Sequence[int] | None = None,
                            limit: int = 20,
                            offset: int = 0,
                        ) -> tuple[list[dict[str, str | int]], int]:
                            return list_scope_compatible_trace_index_page(
                                uow=refresh_uow,
                                dataset_id=active_id,
                                selected_bundle_id=selected_bundle_id,
                                analysis_requires=selected_analysis_requires,
                                search=search,
                                sort_by=sort_by,
                                descending=descending,
                                mode_filter=mode_filter,
                                ids=ids,
                                limit=limit,
                                offset=offset,
                            )

                        trace_scope_key = (
                            f"{active_id}:{selected_scope_token}:{selected_run_analysis_id}"
                        )
                        if trace_scope_key not in runtime_state.selected_trace_ids_by_scope:
                            base_rows, _ = _compatible_trace_page(
                                mode_filter="base",
                                limit=1,
                                offset=0,
                            )
                            if base_rows:
                                runtime_state.set_selected_trace_ids(
                                    trace_scope_key,
                                    {int(base_rows[0]["id"])},
                                )
                            else:
                                first_rows, _ = _compatible_trace_page(limit=1, offset=0)
                                runtime_state.set_selected_trace_ids(
                                    trace_scope_key,
                                    {int(first_rows[0]["id"])} if first_rows else set(),
                                )
                        if trace_scope_key not in runtime_state.trace_table_state_by_scope:
                            _, base_trace_count = _compatible_trace_page(
                                mode_filter="base",
                                limit=1,
                                offset=0,
                            )
                            runtime_state.ensure_trace_table_state(
                                trace_scope_key,
                                default_mode_filter=(
                                    "base" if base_trace_count > 0 else _TRACE_MODE_ALL
                                ),
                            )

                        def _current_mode_filter() -> str:
                            table_state = runtime_state.trace_table_state_by_scope[trace_scope_key]
                            return str(table_state.get("trace_mode_filter", _TRACE_MODE_ALL))

                        def current_mode_trace_total() -> int:
                            _, total = _compatible_trace_page(
                                mode_filter=_current_mode_filter(),
                                limit=1,
                                offset=0,
                            )
                            return total

                        def current_selected_trace_ids() -> set[int]:
                            scope_selected_ids = runtime_state.selected_trace_ids_by_scope.get(
                                trace_scope_key,
                                set(),
                            )
                            if not scope_selected_ids:
                                return set()
                            validated_rows, _ = _compatible_trace_page(
                                mode_filter=_current_mode_filter(),
                                ids=sorted(scope_selected_ids),
                                limit=max(1, len(scope_selected_ids)),
                                offset=0,
                            )
                            validated_ids = {
                                int(row["id"])
                                for row in validated_rows
                                if isinstance(row.get("id"), int)
                            }
                            runtime_state.set_selected_trace_ids(trace_scope_key, validated_ids)
                            return validated_ids

                        def current_selected_trace_rows() -> list[dict[str, str | int]]:
                            selected_ids = sorted(current_selected_trace_ids())
                            if not selected_ids:
                                return []
                            rows, _ = _compatible_trace_page(
                                mode_filter=_current_mode_filter(),
                                ids=selected_ids,
                                limit=max(1, len(selected_ids)),
                                offset=0,
                            )
                            return rows

                        def set_selected_trace_ids(updated_ids: set[int]) -> None:
                            runtime_state.set_selected_trace_ids(trace_scope_key, updated_ids)

                        def bulk_select_for_mode(mode_filter: str) -> None:
                            rows, total = _compatible_trace_page(
                                mode_filter=mode_filter,
                                sort_by="id",
                                descending=False,
                                limit=_MAX_BULK_TRACE_SELECTION + 1,
                                offset=0,
                            )
                            selected_ids = {
                                int(row["id"])
                                for row in rows[:_MAX_BULK_TRACE_SELECTION]
                                if isinstance(row.get("id"), int)
                            }
                            set_selected_trace_ids(selected_ids)
                            if total > _MAX_BULK_TRACE_SELECTION:
                                ui.notify(
                                    (
                                        "Large selection truncated to "
                                        f"{_MAX_BULK_TRACE_SELECTION} traces for stability."
                                    ),
                                    type="warning",
                                )

                        def current_run_ui_state() -> AnalysisRunUiState:
                            return _build_analysis_run_ui_state(
                                has_compatible_traces=current_mode_trace_total() > 0,
                                selected_trace_count=len(current_selected_trace_ids()),
                            )

                        analysis_method_groups: dict[str, dict[str, list]] = {}
                        for analysis in analyses:
                            completed_methods = set(analysis.get("completed_methods", []))
                            analysis_method_groups[str(analysis["id"])] = {
                                method_key: list(method_params[method_key])
                                for method_key in sorted(completed_methods)
                                if method_key in method_params
                            }

                        completed_analysis_ids = [
                            analysis_id
                            for analysis_id, groups in analysis_method_groups.items()
                            if groups
                        ]
                        selected_result_analysis_id = _resolve_selected_option(
                            _load_dataset_text_selection(_ANALYSIS_RESULT_SELECTED_KEY, active_id),
                            completed_analysis_ids,
                        )
                        _save_dataset_text_selection(
                            _ANALYSIS_RESULT_SELECTED_KEY,
                            active_id,
                            selected_result_analysis_id,
                        )

                        with ui.column().classes("w-full gap-4"):
                            with _with_test_id(
                                ui.card().classes("w-full bg-surface rounded-xl p-6"),
                                "characterization-source-scope-card",
                            ):
                                with ui.row().classes(
                                    "w-full items-center justify-between gap-4 flex-wrap"
                                ):
                                    ui.icon("inventory_2", size="sm").classes("text-primary")
                                    ui.label("Source Scope").classes("text-lg font-bold text-fg")
                                ui.label(
                                    "Dataset-centric scope is active. Run Analysis uses all "
                                    "dataset trace records and applies trace-first "
                                    "compatibility filtering."
                                ).classes("text-sm text-muted mt-2")
                                with ui.row().classes("w-full gap-4 mt-3 flex-wrap"):
                                    with ui.column().classes(
                                        "bg-bg rounded-lg border border-border p-3 min-w-[160px]"
                                    ):
                                        ui.label("Scope").classes(
                                            "text-xs text-muted font-bold uppercase"
                                        )
                                        ui.label("All Dataset Records").classes("text-sm text-fg")
                                    with ui.column().classes(
                                        "bg-bg rounded-lg border border-border p-3 min-w-[160px]"
                                    ):
                                        ui.label("Trace Records").classes(
                                            "text-xs text-muted font-bold uppercase"
                                        )
                                        ui.label(str(scoped_trace_count)).classes("text-sm text-fg")
                                    with ui.column().classes(
                                        "bg-bg rounded-lg border border-border p-3 min-w-[160px]"
                                    ):
                                        ui.label("Result Bundles").classes(
                                            "text-xs text-muted font-bold uppercase"
                                        )
                                        ui.label(str(len(bundles))).classes("text-sm text-fg")

                            with _with_test_id(
                                ui.card().classes("w-full bg-surface rounded-xl p-6"),
                                "characterization-run-analysis-card",
                            ):
                                run_config_selects: dict[str, Any] = {}
                                run_config_numbers: dict[str, Any] = {}
                                run_button: Any | None = None
                                availability_label: Any | None = None
                                analysis_reason_label: Any | None = None

                                def refresh_run_controls() -> None:
                                    ui_state = current_run_ui_state()
                                    has_selected_traces = len(current_selected_trace_ids()) > 0
                                    if not ui_state.has_compatible_traces:
                                        availability_text = "Unavailable for current scope"
                                        availability_class = "text-warning"
                                        reason_text = "No compatible traces in current scope."
                                        run_disabled = True
                                    elif selected_run_availability.status == "Recommended":
                                        availability_text = "Recommended for current scope"
                                        availability_class = "text-positive"
                                        reason_text = (
                                            "Select at least one trace to run."
                                            if not has_selected_traces
                                            else selected_run_availability.reason
                                        )
                                        run_disabled = not has_selected_traces
                                    else:
                                        availability_text = "Available for current scope"
                                        availability_class = ui_state.availability_class
                                        reason_text = (
                                            "Select at least one trace to run."
                                            if not has_selected_traces
                                            else selected_run_availability.reason
                                        )
                                        run_disabled = not has_selected_traces

                                    if availability_label is not None:
                                        availability_label.set_text(availability_text)
                                        availability_label.classes(
                                            replace=(f"text-sm font-semibold {availability_class}")
                                        )
                                    if analysis_reason_label is not None:
                                        analysis_reason_label.set_text(reason_text)
                                        analysis_reason_label.classes(
                                            replace=(
                                                "text-sm text-warning mb-2"
                                                if run_disabled
                                                else "text-sm text-muted mb-2"
                                            )
                                        )
                                    if run_button is not None:
                                        if run_disabled:
                                            run_button.disable()
                                        else:
                                            run_button.enable()

                                with ui.row().classes(
                                    "w-full items-center justify-between gap-3 flex-wrap mb-3"
                                ):
                                    with ui.row().classes("items-center gap-2"):
                                        ui.icon("play_circle", size="sm").classes("text-primary")
                                        ui.label("Run Analysis").classes(
                                            "text-lg font-bold text-fg"
                                        )

                                    def run_selected_analysis() -> None:
                                        analysis_id = str(selected_run_analysis["id"])
                                        run_id = f"char-{uuid4().hex[:10]}"
                                        runtime_state.set_log_context(
                                            run_id=run_id,
                                            dataset_id=ds.id,
                                            analysis_id=analysis_id,
                                        )
                                        run_trace_ids = sorted(current_selected_trace_ids())
                                        config_fields = selected_run_analysis.get(
                                            "config_fields",
                                            [],
                                        )
                                        config_state: dict[str, str | float | int | None] = {
                                            str(field["name"]): field.get("default")
                                            for field in config_fields
                                            if field.get("name")
                                        }
                                        for field in config_fields:
                                            name = str(field.get("name", ""))
                                            if not name:
                                                continue
                                            if field["type"] == "select":
                                                config_state[name] = run_config_selects[name].value
                                            elif field["type"] == "number":
                                                config_state[name] = run_config_numbers[name].value

                                        run_ui_state = current_run_ui_state()
                                        if not run_ui_state.has_compatible_traces:
                                            append_analysis_status(
                                                "warning",
                                                run_ui_state.run_hint,
                                            )
                                            return
                                        if not run_trace_ids:
                                            append_analysis_status(
                                                "warning",
                                                "Select at least one trace to run.",
                                            )
                                            return

                                        append_analysis_status(
                                            "info",
                                            (
                                                f"Running {selected_run_analysis['label']} on "
                                                f"dataset {ds.name} (id={ds.id}) with "
                                                f"{len(run_trace_ids)} trace(s)."
                                            ),
                                        )
                                        try:
                                            if ds.id is None:
                                                raise ValueError("Active dataset id is missing.")

                                            selected_mode_group = (
                                                _trace_mode_group_for_selected_rows(
                                                    current_selected_trace_rows()
                                                )
                                            )
                                            _execute_analysis_run(
                                                analysis_id=analysis_id,
                                                dataset_id=ds.id,
                                                config_state=config_state,
                                                trace_record_ids=run_trace_ids,
                                                trace_mode_group=selected_mode_group,
                                            )
                                            with get_unit_of_work() as write_uow:
                                                bundle = _build_analysis_run_bundle_record(
                                                    dataset_id=ds.id,
                                                    analysis_id=analysis_id,
                                                    analysis_label=str(
                                                        selected_run_analysis["label"]
                                                    ),
                                                    run_id=run_id,
                                                    selected_bundle_id=None,
                                                    selected_scope_token=selected_scope_token,
                                                    config_snapshot={
                                                        **dict(config_state),
                                                        "run_id": run_id,
                                                        "selected_trace_ids": run_trace_ids,
                                                        "selected_trace_mode_group": (
                                                            selected_mode_group
                                                        ),
                                                        "selected_trace_count": len(run_trace_ids),
                                                    },
                                                )
                                                write_uow.result_bundles.add(bundle)
                                                write_uow.commit()
                                                if bundle.id is not None:
                                                    runtime_state.set_log_context(
                                                        run_id=run_id,
                                                        dataset_id=ds.id,
                                                        analysis_id=analysis_id,
                                                        bundle_id=bundle.id,
                                                    )
                                                    append_analysis_status(
                                                        "info",
                                                        f"Recorded analysis bundle #{bundle.id}.",
                                                    )

                                            append_analysis_status(
                                                "positive",
                                                f"{selected_run_analysis['label']} completed.",
                                            )
                                            render_dataset_view.refresh()
                                        except NotImplementedError:
                                            append_analysis_status(
                                                "warning",
                                                (
                                                    f"{selected_run_analysis['label']} is not "
                                                    "implemented yet."
                                                ),
                                            )
                                        except Exception as exc:
                                            append_analysis_status(
                                                "negative",
                                                f"{selected_run_analysis['label']} failed: {exc}",
                                            )

                                    run_button = (
                                        ui.button(
                                            "Run Selected Analysis",
                                            on_click=run_selected_analysis,
                                            icon="play_arrow",
                                        )
                                        .props("unelevated color=primary")
                                        .classes("font-bold")
                                    )
                                    _with_test_id(
                                        run_button,
                                        "characterization-run-analysis-button",
                                    )

                                ui.label(
                                    "Run control is centralized here. Choose one analysis, set "
                                    "parameters, then execute."
                                ).classes("text-sm text-muted mb-3")
                                ui.label(profile_summary_text(dataset_profile)).classes(
                                    "text-xs text-muted mb-2"
                                )

                                with ui.row().classes("w-full items-end gap-4 flex-wrap"):
                                    analysis_select = (
                                        ui.select(
                                            options=analysis_options,
                                            value=selected_run_analysis_id,
                                            label="Analysis",
                                            on_change=lambda e: (
                                                _save_dataset_text_selection(
                                                    _ANALYSIS_RUN_SELECTED_KEY,
                                                    active_id,
                                                    str(e.value),
                                                ),
                                                render_dataset_view.refresh(),
                                            ),
                                        )
                                        .props("dense outlined options-dense")
                                        .classes("w-72")
                                    )
                                    _with_test_id(
                                        analysis_select,
                                        "characterization-analysis-select",
                                    )

                                    availability_label = ui.label("").classes(
                                        "text-sm font-semibold"
                                    )
                                    _with_test_id(
                                        availability_label,
                                        "characterization-availability-label",
                                    )
                                analysis_reason_label = ui.label("").classes(
                                    "text-sm text-muted mb-2"
                                )
                                _with_test_id(
                                    analysis_reason_label,
                                    "characterization-availability-reason",
                                )
                                refresh_run_controls()

                                ui.separator().classes("my-4 bg-border")

                                @ui.refreshable
                                def render_trace_selection() -> None:
                                    table_state = runtime_state.trace_table_state_by_scope[
                                        trace_scope_key
                                    ]
                                    mode_filter = str(
                                        table_state.get("trace_mode_filter", _TRACE_MODE_ALL)
                                    )
                                    mode_total = current_mode_trace_total()

                                    with ui.row().classes(
                                        "w-full items-center justify-between gap-3 flex-wrap"
                                    ):
                                        ui.label("Trace Selection").classes(
                                            "text-sm font-bold text-fg uppercase tracking-wider"
                                        )
                                        with ui.row().classes("items-center gap-2"):
                                            ui.label(
                                                f"{len(current_selected_trace_ids())} / "
                                                f"{mode_total} selected"
                                            ).classes("text-xs text-muted")

                                            ui.button(
                                                "Base",
                                                on_click=lambda: (
                                                    bulk_select_for_mode("base"),
                                                    refresh_run_controls(),
                                                    render_trace_selection.refresh(),
                                                ),
                                            ).props("flat dense no-caps color=primary")
                                            ui.button(
                                                "All",
                                                on_click=lambda: (
                                                    bulk_select_for_mode(
                                                        str(
                                                            table_state.get(
                                                                "trace_mode_filter",
                                                                _TRACE_MODE_ALL,
                                                            )
                                                        )
                                                    ),
                                                    refresh_run_controls(),
                                                    render_trace_selection.refresh(),
                                                ),
                                            ).props("flat dense no-caps color=primary")
                                            ui.button(
                                                "Clear",
                                                on_click=lambda: (
                                                    set_selected_trace_ids(set()),
                                                    refresh_run_controls(),
                                                    render_trace_selection.refresh(),
                                                ),
                                            ).props("flat dense no-caps color=primary")

                                    if mode_total <= 0:
                                        ui.label(
                                            "No compatible traces found for the selected analysis "
                                            "under selected trace mode filter."
                                        ).classes("text-sm text-muted mb-2")
                                        return

                                    search_text = str(table_state.get("search", ""))
                                    sort_by = str(table_state.get("sort_by", "id"))
                                    descending = bool(table_state.get("descending", False))
                                    page_size = max(
                                        1,
                                        _to_int(table_state.get("page_size", 20), 20),
                                    )
                                    _, total_filtered = _compatible_trace_page(
                                        search=search_text,
                                        mode_filter=mode_filter,
                                        sort_by=sort_by,
                                        descending=descending,
                                        limit=1,
                                        offset=0,
                                    )
                                    total_pages = max(
                                        1,
                                        (total_filtered + page_size - 1) // page_size,
                                    )
                                    current_page = max(
                                        1,
                                        min(_to_int(table_state.get("page", 1), 1), total_pages),
                                    )
                                    table_state["page"] = current_page
                                    page_offset = (current_page - 1) * page_size
                                    visible_trace_rows, _ = _compatible_trace_page(
                                        search=search_text,
                                        mode_filter=mode_filter,
                                        sort_by=sort_by,
                                        descending=descending,
                                        limit=page_size,
                                        offset=page_offset,
                                    )

                                    with ui.row().classes("w-full gap-3 items-end flex-wrap mb-2"):
                                        filter_input = (
                                            ui.input(
                                                label="Filter Traces",
                                                value=str(table_state.get("search", "")),
                                                on_change=lambda e: (
                                                    table_state.__setitem__(
                                                        "search", str(e.value or "")
                                                    ),
                                                    table_state.__setitem__("page", 1),
                                                    render_trace_selection.refresh(),
                                                ),
                                            )
                                            .props("dense outlined clearable")
                                            .classes("min-w-[220px] flex-1")
                                        )
                                        _with_test_id(
                                            filter_input,
                                            "characterization-trace-filter-input",
                                        )
                                        run_trace_mode_filter = (
                                            ui.select(
                                                _TRACE_MODE_FILTER_OPTIONS,
                                                value=str(
                                                    table_state.get(
                                                        "trace_mode_filter",
                                                        _TRACE_MODE_ALL,
                                                    )
                                                ),
                                                label="Trace Mode Filter",
                                                on_change=lambda e: (
                                                    table_state.__setitem__(
                                                        "trace_mode_filter",
                                                        str(e.value or _TRACE_MODE_ALL),
                                                    ),
                                                    table_state.__setitem__("page", 1),
                                                    set_selected_trace_ids(set()),
                                                    refresh_run_controls(),
                                                    render_trace_selection.refresh(),
                                                ),
                                            )
                                            .props("dense outlined options-dense")
                                            .classes("w-40")
                                        )
                                        _with_test_id(
                                            run_trace_mode_filter,
                                            "characterization-run-trace-mode-filter-select",
                                        )
                                        ui.select(
                                            {
                                                "id": "ID",
                                                "mode": "Mode",
                                                "parameter": "Parameter",
                                                "representation": "Representation",
                                            },
                                            value=str(table_state.get("sort_by", "id")),
                                            label="Sort By",
                                            on_change=lambda e: (
                                                table_state.__setitem__("sort_by", str(e.value)),
                                                table_state.__setitem__("page", 1),
                                                render_trace_selection.refresh(),
                                            ),
                                        ).props("dense outlined options-dense").classes("w-44")
                                        ui.select(
                                            {False: "Ascending", True: "Descending"},
                                            value=bool(table_state.get("descending", False)),
                                            label="Order",
                                            on_change=lambda e: (
                                                table_state.__setitem__(
                                                    "descending",
                                                    bool(e.value),
                                                ),
                                                table_state.__setitem__("page", 1),
                                                render_trace_selection.refresh(),
                                            ),
                                        ).props("dense outlined options-dense").classes("w-40")

                                    selected_ids = current_selected_trace_ids()
                                    trace_selection_rows = [
                                        {
                                            "selected": (
                                                "✓"
                                                if _to_int(row.get("id"), 0) in selected_ids
                                                else ""
                                            ),
                                            "id": _to_int(row.get("id"), 0),
                                            "mode": (
                                                "Sideband"
                                                if _trace_row_mode_key(row) == "sideband"
                                                else "Base"
                                            ),
                                            "parameter": str(row["parameter"]),
                                            "representation": str(row["representation"]),
                                        }
                                        for row in visible_trace_rows
                                    ]
                                    trace_selection_columns = [
                                        {
                                            "name": "selected",
                                            "label": "",
                                            "field": "selected",
                                            "align": "center",
                                            "sortable": False,
                                        },
                                        {
                                            "name": "id",
                                            "label": "ID",
                                            "field": "id",
                                            "align": "left",
                                            "sortable": True,
                                        },
                                        {
                                            "name": "mode",
                                            "label": "Mode",
                                            "field": "mode",
                                            "align": "left",
                                            "sortable": True,
                                        },
                                        {
                                            "name": "parameter",
                                            "label": "Parameter",
                                            "field": "parameter",
                                            "align": "left",
                                            "sortable": True,
                                        },
                                        {
                                            "name": "representation",
                                            "label": "Representation",
                                            "field": "representation",
                                            "align": "left",
                                            "sortable": True,
                                        },
                                    ]
                                    trace_table = (
                                        ui.table(
                                            columns=trace_selection_columns,
                                            rows=trace_selection_rows,
                                            row_key="id",
                                            pagination=0,
                                        )
                                        .classes("w-full mb-2")
                                        .props("dense flat bordered separator=horizontal")
                                    )

                                    def on_trace_row_click(event: Any) -> None:
                                        row_data = event.args[1] if len(event.args) > 1 else {}
                                        if not isinstance(row_data, dict):
                                            return
                                        row_id = row_data.get("id")
                                        if not isinstance(row_id, int):
                                            return
                                        updated_ids = current_selected_trace_ids()
                                        if row_id in updated_ids:
                                            updated_ids.remove(row_id)
                                        else:
                                            updated_ids.add(row_id)
                                        set_selected_trace_ids(updated_ids)
                                        refresh_run_controls()
                                        render_trace_selection.refresh()

                                    trace_table.on("rowClick", on_trace_row_click)
                                    with ui.row().classes(
                                        "w-full justify-between items-center flex-wrap gap-2 mb-2"
                                    ):
                                        ui.label(
                                            f"Filtered {total_filtered} traces · "
                                            f"Page {current_page} / {total_pages}"
                                        ).classes("text-xs text-muted")
                                        with ui.row().classes("items-center gap-2"):
                                            ui.select(
                                                {
                                                    10: "10 / page",
                                                    20: "20 / page",
                                                    50: "50 / page",
                                                },
                                                value=page_size,
                                                on_change=lambda e: (
                                                    table_state.__setitem__(
                                                        "page_size",
                                                        _to_int(e.value, page_size),
                                                    ),
                                                    table_state.__setitem__("page", 1),
                                                    render_trace_selection.refresh(),
                                                ),
                                            ).props("dense outlined options-dense").classes("w-28")
                                            prev_button = ui.button(
                                                "Prev",
                                                on_click=lambda: (
                                                    table_state.__setitem__(
                                                        "page",
                                                        max(1, current_page - 1),
                                                    ),
                                                    render_trace_selection.refresh(),
                                                ),
                                            ).props("dense flat no-caps")
                                            if current_page <= 1:
                                                prev_button.disable()
                                            next_button = ui.button(
                                                "Next",
                                                on_click=lambda: (
                                                    table_state.__setitem__(
                                                        "page",
                                                        min(total_pages, current_page + 1),
                                                    ),
                                                    render_trace_selection.refresh(),
                                                ),
                                            ).props("dense flat no-caps")
                                            if current_page >= total_pages:
                                                next_button.disable()

                                render_trace_selection()

                                config_fields = selected_run_analysis.get("config_fields", [])
                                if config_fields:
                                    with ui.row().classes("w-full gap-4 mt-3 flex-wrap"):
                                        for field in config_fields:
                                            field_name = str(field.get("name", ""))
                                            if not field_name:
                                                continue
                                            if field["type"] == "select":
                                                run_config_selects[field_name] = (
                                                    ui.select(
                                                        options=field["options"],
                                                        value=field.get("default"),
                                                        label=field["label"],
                                                    )
                                                    .props("dense outlined options-dense")
                                                    .classes("w-44")
                                                )
                                            elif field["type"] == "number":
                                                run_config_numbers[field_name] = (
                                                    ui.number(
                                                        label=field["label"],
                                                        value=field.get("default"),
                                                    )
                                                    .props("dense outlined")
                                                    .classes("w-40")
                                                )

                                ui.separator().classes("my-4 bg-border")
                                with ui.row().classes("w-full items-center gap-2 mb-2"):
                                    ui.icon("terminal", size="xs").classes("text-primary")
                                    ui.label("Analysis Log").classes(
                                        "text-sm font-bold text-fg uppercase tracking-wider"
                                    )
                                runtime_state.analysis_log_container = ui.column().classes(
                                    "w-full gap-2"
                                )
                                render_analysis_status()

                            with _with_test_id(
                                ui.card().classes("w-full bg-surface rounded-xl p-6"),
                                "characterization-result-view-card",
                            ):
                                with ui.row().classes(
                                    "w-full items-center justify-between gap-3 flex-wrap mb-3"
                                ):
                                    with ui.row().classes("items-center gap-2"):
                                        ui.icon("insights", size="sm").classes("text-primary")
                                        ui.label("Result View").classes("text-lg font-bold text-fg")
                                    ui.label(
                                        "Switch tabs to inspect completed analyses "
                                        "without rerunning."
                                    ).classes("text-sm text-muted")

                                if not completed_analysis_ids:
                                    with ui.column().classes(
                                        "w-full py-8 items-center justify-center"
                                    ):
                                        ui.icon("hourglass_empty", size="md").classes(
                                            "text-muted opacity-40 mb-2"
                                        )
                                        ui.label("No completed analysis yet.").classes(
                                            "text-sm text-muted"
                                        )
                                else:
                                    tab_options = {
                                        str(analysis["id"]): str(analysis["label"])
                                        for analysis in analyses
                                        if str(analysis["id"]) in completed_analysis_ids
                                    }
                                    tabs = ui.tabs().classes("w-full")
                                    tabs.set_value(selected_result_analysis_id)
                                    for analysis_id, label in tab_options.items():
                                        ui.tab(analysis_id, label=label)
                                    tabs.on_value_change(
                                        lambda e: (
                                            _save_dataset_text_selection(
                                                _ANALYSIS_RESULT_SELECTED_KEY,
                                                active_id,
                                                str(e.value),
                                            ),
                                            render_dataset_view.refresh(),
                                        )
                                    )
                                    selected_analysis_groups_raw = analysis_method_groups.get(
                                        selected_result_analysis_id,
                                        {},
                                    )
                                    analysis_scope_key = _analysis_scope_key(
                                        active_id,
                                        selected_result_analysis_id,
                                    )
                                    trace_mode_options = _trace_mode_filter_options(
                                        selected_analysis_groups_raw
                                    )
                                    selected_trace_mode_filter = _resolve_selected_option(
                                        _load_scope_text_selection(
                                            _ANALYSIS_RESULT_TRACE_MODE_SELECTED_KEY,
                                            analysis_scope_key,
                                        ),
                                        list(trace_mode_options),
                                    )
                                    _save_scope_text_selection(
                                        _ANALYSIS_RESULT_TRACE_MODE_SELECTED_KEY,
                                        analysis_scope_key,
                                        selected_trace_mode_filter,
                                    )
                                    selected_analysis_groups = _filter_method_groups_by_trace_mode(
                                        selected_analysis_groups_raw,
                                        trace_mode_filter=selected_trace_mode_filter,
                                    )
                                    artifacts = _build_result_artifacts_for_analysis(
                                        analysis_id=selected_result_analysis_id,
                                        method_groups=selected_analysis_groups,
                                    )
                                    categories = _artifact_categories(artifacts)
                                    category_options = {
                                        category: _CATEGORY_LABELS.get(
                                            category,
                                            category.replace("_", " ").title(),
                                        )
                                        for category in categories
                                    }
                                    selected_category = _resolve_selected_option(
                                        _load_scope_text_selection(
                                            _ANALYSIS_RESULT_CATEGORY_SELECTED_KEY,
                                            analysis_scope_key,
                                        ),
                                        categories,
                                    )
                                    if categories:
                                        _save_scope_text_selection(
                                            _ANALYSIS_RESULT_CATEGORY_SELECTED_KEY,
                                            analysis_scope_key,
                                            selected_category,
                                        )

                                    with ui.row().classes(_result_view_controls_row_classes()):
                                        result_trace_mode_filter = (
                                            ui.select(
                                                options=trace_mode_options,
                                                value=selected_trace_mode_filter,
                                                label="Trace Mode Filter",
                                                on_change=lambda e: (
                                                    _save_scope_text_selection(
                                                        _ANALYSIS_RESULT_TRACE_MODE_SELECTED_KEY,
                                                        analysis_scope_key,
                                                        str(e.value),
                                                    ),
                                                    render_dataset_view.refresh(),
                                                ),
                                            )
                                            .props("dense outlined options-dense")
                                            .classes("w-64")
                                        )
                                        _with_test_id(
                                            result_trace_mode_filter,
                                            "characterization-result-trace-mode-filter-select",
                                        )
                                        if category_options:
                                            result_category_select = (
                                                ui.select(
                                                    options=category_options,
                                                    value=selected_category,
                                                    label="Category",
                                                    on_change=lambda e: (
                                                        _save_scope_text_selection(
                                                            _ANALYSIS_RESULT_CATEGORY_SELECTED_KEY,
                                                            analysis_scope_key,
                                                            str(e.value),
                                                        ),
                                                        render_dataset_view.refresh(),
                                                    ),
                                                )
                                                .props("dense outlined options-dense")
                                                .classes("w-64")
                                            )
                                            _with_test_id(
                                                result_category_select,
                                                "characterization-result-category-select",
                                            )
                                        else:
                                            category_placeholder = ui.select(
                                                options={"": "Category (N/A)"},
                                                value="",
                                                label="Category",
                                            ).props("dense outlined")
                                            category_placeholder.classes("w-64")
                                            category_placeholder.disable()

                                    if not artifacts:
                                        selected_mode_label = trace_mode_options.get(
                                            selected_trace_mode_filter,
                                            "All",
                                        )
                                        ui.label(
                                            _result_view_empty_state_message(
                                                selected_mode_label=selected_mode_label,
                                                selected_analysis_groups_raw=(
                                                    selected_analysis_groups_raw
                                                ),
                                                selected_analysis_groups=selected_analysis_groups,
                                            )
                                        ).classes("text-sm text-muted mt-3")
                                    else:
                                        artifacts_for_category = _artifacts_in_category(
                                            artifacts,
                                            category=selected_category,
                                        )
                                        artifact_ids = [
                                            artifact.artifact_id
                                            for artifact in artifacts_for_category
                                        ]
                                        selected_artifact_id = _resolve_selected_option(
                                            _load_scope_text_selection(
                                                _ANALYSIS_RESULT_ARTIFACT_SELECTED_KEY,
                                                analysis_scope_key,
                                            ),
                                            artifact_ids,
                                        )
                                        _save_scope_text_selection(
                                            _ANALYSIS_RESULT_ARTIFACT_SELECTED_KEY,
                                            analysis_scope_key,
                                            selected_artifact_id,
                                        )

                                        artifact_tabs = ui.tabs().classes("w-full")
                                        _with_test_id(
                                            artifact_tabs,
                                            "characterization-result-artifact-tabs",
                                        )
                                        artifact_tabs.set_value(selected_artifact_id)
                                        for artifact in artifacts_for_category:
                                            ui.tab(artifact.artifact_id, label=artifact.tab_label)
                                        artifact_tabs.on_value_change(
                                            lambda e: (
                                                _save_scope_text_selection(
                                                    _ANALYSIS_RESULT_ARTIFACT_SELECTED_KEY,
                                                    analysis_scope_key,
                                                    str(e.value),
                                                ),
                                                render_dataset_view.refresh(),
                                            )
                                        )

                                        artifact_lookup = {
                                            artifact.artifact_id: artifact
                                            for artifact in artifacts_for_category
                                        }
                                        selected_artifact = artifact_lookup[selected_artifact_id]
                                        payload = ResultViewQueryService(
                                            selected_analysis_groups
                                        ).load_payload(selected_artifact)
                                        _render_result_artifact(
                                            ds=ds,
                                            artifact=selected_artifact,
                                            payload=payload,
                                        )

                # --- Layout ---
                with ui.row().classes("w-full items-center gap-4 mb-4"):
                    ui.label("Dataset:").classes("text-sm font-bold text-fg")

                    def on_change(e):
                        app.storage.user["analysis_current_dataset"] = e.value
                        render_dataset_view.refresh()

                    dataset_select = (
                        ui.select(
                            options=ds_options,
                            value=current_ds_id,
                            on_change=on_change,
                        )
                        .props("dense outlined options-dense")
                        .classes("w-64")
                    )
                    _with_test_id(dataset_select, "characterization-dataset-select")

                render_dataset_view()

        except Exception as e:
            ui.label(f"Error loading characterization: {e}").classes("text-danger")

    app_shell(content)()
