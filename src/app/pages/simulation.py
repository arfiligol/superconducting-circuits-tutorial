"""Simulation page - Circuit visualization and analysis."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypedDict

import numpy as np
import plotly.graph_objects as go
from nicegui import app, run, ui

from app.layout import app_shell
from app.services.dataset_profile import (
    normalize_dataset_profile,
    profile_summary_text,
)
from core.shared.persistence import SqliteUnitOfWork, get_unit_of_work
from core.shared.persistence.models import (
    CircuitRecord,
    DataRecord,
    DatasetRecord,
    ResultBundleRecord,
)
from core.shared.visualization import get_plotly_layout
from core.simulation.application.post_processing import (
    PortMatrixSweep,
    apply_coordinate_transform,
    build_common_differential_transform,
    build_port_y_sweep,
    compensate_simulation_result_port_terminations,
    filtered_modes,
    infer_port_termination_resistance_ohm,
    kron_reduce,
)
from core.simulation.application.run_simulation import run_simulation
from core.simulation.domain.circuit import (
    CircuitDefinition,
    DriveSourceConfig,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
    format_expanded_circuit_definition,
    parse_circuit_definition_source,
)

_SIM_SETUP_STORAGE_KEY = "simulation_saved_setups_by_schema"
_SIM_SETUP_SELECTED_KEY = "simulation_selected_setup_id_by_schema"
_POST_PROCESS_SETUP_STORAGE_KEY = "simulation_post_process_saved_setups_by_schema"
_POST_PROCESS_SELECTED_KEY = "simulation_post_process_selected_setup_id_by_schema"
_JOSEPHSON_EXAMPLE_PREFIX = "JosephsonCircuits Examples: "
_SYSTEM_SIMULATION_CACHE_DATASET_NAME = "__system__:simulation_result_cache"
_RESULT_FAMILY_OPTIONS = {
    "s": "S",
    "gain": "Gain",
    "impedance": "Impedance (Z)",
    "admittance": "Admittance (Y)",
    "qe": "Quantum Efficiency (QE)",
    "cm": "Commutation (CM)",
    "complex": "Complex Plane",
}
_POST_PROCESSED_RESULT_FAMILY_OPTIONS = {
    "s": "S",
    "gain": "Gain",
    "impedance": "Impedance (Z)",
    "admittance": "Admittance (Y)",
    "complex": "Complex Plane",
}
_RESULT_METRIC_OPTIONS = {
    "s": {
        "magnitude_linear": "Magnitude (linear)",
        "magnitude_db": "Magnitude (dB)",
        "phase_deg": "Phase (deg)",
        "real": "Real",
        "imag": "Imaginary",
    },
    "gain": {
        "gain_db": "Gain (dB)",
        "gain_linear": "Gain (linear)",
    },
    "impedance": {
        "real": "Real(Z)",
        "imag": "Imag(Z)",
        "magnitude": "|Z|",
    },
    "admittance": {
        "real": "Real(Y)",
        "imag": "Imag(Y)",
        "magnitude": "|Y|",
    },
    "qe": {
        "linear": "QE",
    },
    "cm": {
        "value": "Value",
    },
    "complex": {
        "trajectory": "Trajectory",
    },
}
_RESULT_TRACE_OPTIONS = {
    "s": {"s_param": "S-Parameter"},
    "gain": {"gain_from_s": "Power Gain from S"},
    "impedance": {"impedance": "Impedance"},
    "admittance": {"admittance": "Admittance"},
    "qe": {
        "qe": "QE",
        "qe_ideal": "QE (Ideal)",
    },
    "cm": {"cm": "CM"},
    "complex": {
        "s": "S",
        "z": "Z",
        "y": "Y",
    },
}
_RESULT_TRACE_COLORS = [
    "rgb(99, 102, 241)",
    "rgb(14, 165, 233)",
    "rgb(16, 185, 129)",
    "rgb(245, 158, 11)",
    "rgb(239, 68, 68)",
    "rgb(168, 85, 247)",
]
_POST_PROCESS_MODE_FILTER_OPTIONS = {
    "base": "Base",
    "sideband": "Sideband",
    "all": "All Modes",
}
_TERMINATION_MODE_OPTIONS = {
    "auto": "Auto (Schema infer)",
    "manual": "Manual",
}
_TERMINATION_DEFAULT_RESISTANCE_OHM = 50.0
_Z0_CONTROL_PROPS = "dense outlined"
_Z0_CONTROL_CLASSES = "w-32"
_SIM_METADATA_TARGET_DATASET_KEY = "simulation_metadata_target_dataset_id"


class _ResultTraceSelection(TypedDict):
    trace: str
    output_mode: tuple[int, ...]
    output_port: int
    input_mode: tuple[int, ...]
    input_port: int


def _user_storage_get(key: str, default: Any = None) -> Any:
    """Safely read one value from user storage with non-UI-context fallback."""
    try:
        return app.storage.user.get(key, default)
    except RuntimeError:
        return default


def _user_storage_set(key: str, value: Any) -> None:
    """Safely write one value into user storage when UI context is available."""
    try:
        app.storage.user[key] = value
    except RuntimeError:
        return


def _hash_stable_json(payload: dict[str, Any]) -> str:
    """Return a stable hash for one JSON-compatible payload."""
    normalized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return f"sha256:{hashlib.sha256(normalized.encode('utf-8')).hexdigest()}"


def _hash_schema_source(source_text: str) -> str:
    """Return a stable hash for the stored source-form schema text."""
    return f"sha256:{hashlib.sha256(source_text.encode('utf-8')).hexdigest()}"


def _normalized_simulation_setup_snapshot(
    freq_range: FrequencyRange,
    config: SimulationConfig,
) -> dict[str, Any]:
    """Build the canonical setup snapshot used for cache identity."""
    if config.sources:
        resolved_sources = config.sources
    else:
        resolved_sources = [
            DriveSourceConfig(
                pump_freq_ghz=float(config.pump_freq_ghz),
                port=int(config.pump_port),
                current_amp=float(config.pump_current_amp),
                mode_components=(int(config.pump_mode_index),),
            )
        ]

    return {
        "freq_range": {
            "start_ghz": float(freq_range.start_ghz),
            "stop_ghz": float(freq_range.stop_ghz),
            "points": int(freq_range.points),
        },
        "sources": [
            {
                "pump_freq_ghz": float(source.pump_freq_ghz),
                "port": int(source.port),
                "current_amp": float(source.current_amp),
                "mode": [
                    int(value)
                    for value in (
                        source.mode_components
                        if source.mode_components is not None
                        else _normalize_source_mode_components(
                            None,
                            source_index=idx,
                            source_count=len(resolved_sources),
                        )
                    )
                ],
            }
            for idx, source in enumerate(resolved_sources)
        ],
        "harmonics": {
            "n_modulation_harmonics": int(config.n_modulation_harmonics),
            "n_pump_harmonics": int(config.n_pump_harmonics),
        },
        "advanced": {
            "include_dc": bool(config.include_dc),
            "enable_three_wave_mixing": bool(config.enable_three_wave_mixing),
            "enable_four_wave_mixing": bool(config.enable_four_wave_mixing),
            "max_intermod_order": (
                -1 if config.max_intermod_order is None else int(config.max_intermod_order)
            ),
            "max_iterations": int(config.max_iterations),
            "f_tol": float(config.f_tol),
            "line_search_switch_tol": float(config.line_search_switch_tol),
            "alpha_min": float(config.alpha_min),
        },
    }


def _ensure_simulation_cache_dataset(uow: SqliteUnitOfWork) -> DatasetRecord:
    """Return the hidden dataset used for automatic simulation-result caching."""
    existing = uow.datasets.get_by_name(_SYSTEM_SIMULATION_CACHE_DATASET_NAME)
    if existing is not None:
        if not existing.source_meta.get("system_hidden"):
            existing.source_meta = {
                **existing.source_meta,
                "system_hidden": True,
                "collection_origin": "system_cache",
                "cache_kind": "simulation_result",
            }
        return existing

    dataset = DatasetRecord(
        name=_SYSTEM_SIMULATION_CACHE_DATASET_NAME,
        source_meta={
            "collection_origin": "system_cache",
            "cache_kind": "simulation_result",
            "system_hidden": True,
        },
        parameters={},
    )
    uow.datasets.add(dataset)
    uow.flush()
    return dataset


def _load_cached_simulation_result(
    uow: SqliteUnitOfWork,
    *,
    schema_source_hash: str,
    simulation_setup_hash: str,
) -> tuple[int, SimulationResult] | None:
    """Load one cached simulation result from the hidden system dataset."""
    cache_dataset = _ensure_simulation_cache_dataset(uow)
    if cache_dataset.id is None:
        return None

    bundle = uow.result_bundles.find_simulation_cache(
        dataset_id=cache_dataset.id,
        schema_source_hash=schema_source_hash,
        simulation_setup_hash=simulation_setup_hash,
    )
    if bundle is None or not bundle.result_payload:
        return None

    try:
        result = SimulationResult.model_validate(bundle.result_payload)
    except Exception:
        return None

    if bundle.id is None:
        return None

    return (bundle.id, result)


def _persist_simulation_result_bundle(
    *,
    uow: SqliteUnitOfWork,
    dataset_id: int,
    result: SimulationResult,
    role: str,
    source_meta: dict[str, Any],
    config_snapshot: dict[str, Any],
    schema_source_hash: str | None = None,
    simulation_setup_hash: str | None = None,
    include_data_records: bool = True,
) -> int:
    """Persist one simulation result bundle plus its trace-level DataRecord rows."""
    bundle = ResultBundleRecord(
        dataset_id=dataset_id,
        bundle_type="circuit_simulation",
        role=role,
        status="completed",
        schema_source_hash=schema_source_hash,
        simulation_setup_hash=simulation_setup_hash,
        source_meta=dict(source_meta),
        config_snapshot=dict(config_snapshot),
        result_payload=result.model_dump(mode="json"),
        completed_at=datetime.utcnow(),
    )
    uow.result_bundles.add(bundle)
    uow.flush()

    if bundle.id is None:
        raise ValueError("Failed to allocate a result bundle id.")
    bundle_id = bundle.id

    if not include_data_records:
        return bundle_id

    records = _build_result_bundle_data_records(dataset_id=dataset_id, result=result)
    for record in records:
        uow.data_records.add(record)
    uow.flush()

    record_ids = [record.id for record in records if record.id is not None]
    if len(record_ids) != len(records):
        raise ValueError("Failed to allocate one or more data record ids.")

    uow.result_bundles.attach_data_records(bundle_id=bundle_id, data_record_ids=record_ids)
    return bundle_id


def _build_setup_payload(
    *,
    start_ghz: float,
    stop_ghz: float,
    points: int,
    n_modulation_harmonics: int,
    n_pump_harmonics: int,
    sources: list[dict[str, Any]],
    include_dc: bool = False,
    enable_three_wave_mixing: bool = False,
    enable_four_wave_mixing: bool = True,
    max_intermod_order: int = -1,
    max_iterations: int = 1000,
    f_tol: float = 1e-8,
    line_search_switch_tol: float = 1e-5,
    alpha_min: float = 1e-4,
) -> dict[str, Any]:
    """Build a saved-setup payload matching the UI save format."""
    return {
        "freq_range": {
            "start_ghz": start_ghz,
            "stop_ghz": stop_ghz,
            "points": points,
        },
        "harmonics": {
            "n_modulation_harmonics": n_modulation_harmonics,
            "n_pump_harmonics": n_pump_harmonics,
        },
        "sources": sources,
        "advanced": {
            "include_dc": include_dc,
            "enable_three_wave_mixing": enable_three_wave_mixing,
            "enable_four_wave_mixing": enable_four_wave_mixing,
            "max_intermod_order": max_intermod_order,
            "max_iterations": max_iterations,
            "f_tol": f_tol,
            "line_search_switch_tol": line_search_switch_tol,
            "alpha_min": alpha_min,
        },
    }


def _build_source_payload(
    *,
    pump_freq_ghz: float,
    port: int,
    current_amp: float,
    mode: tuple[int, ...] | list[int],
) -> dict[str, Any]:
    """Build one saved-setup source payload entry."""
    return {
        "pump_freq_ghz": float(pump_freq_ghz),
        "port": int(port),
        "current_amp": float(current_amp),
        "mode": [int(value) for value in mode],
    }


def _compress_source_mode_components(
    mode: tuple[int, ...] | list[int] | None,
) -> tuple[int, ...]:
    """Compress internal mode vectors into the shortest user-facing tuple."""
    if mode is None:
        return ()

    values = tuple(int(value) for value in mode)
    if not values:
        return ()

    if all(value == 0 for value in values):
        return (0,)

    highest_nonzero_index = max(idx for idx, value in enumerate(values) if value != 0)
    return values[: highest_nonzero_index + 1]


def _format_source_mode_text(mode: tuple[int, ...] | list[int] | None) -> str:
    """Format one source mode tuple for the UI text field."""
    if mode is None:
        return ""
    values = tuple(int(value) for value in mode)
    if not values:
        return ""
    return ", ".join(str(value) for value in values)


def _parse_source_mode_text(raw_value: object) -> tuple[int, ...] | None:
    """Parse the UI/source-payload mode field into a normalized tuple."""
    if raw_value is None:
        return None
    if isinstance(raw_value, list | tuple):
        parsed = tuple(int(value) for value in raw_value)
        return parsed or None

    text = str(raw_value).strip()
    if not text:
        return None

    normalized = text.strip("()[]")
    normalized = normalized.replace(";", ",")
    if not normalized:
        return None

    parts = [part.strip() for part in normalized.split(",") if part.strip()]
    if not parts:
        return None

    return tuple(int(part) for part in parts)


def _normalize_source_mode_components(
    mode: tuple[int, ...] | list[int] | None,
    *,
    source_index: int,
    source_count: int,
) -> tuple[int, ...]:
    """Normalize one source mode tuple to the current source-count width."""
    width = max(int(source_count), 1)
    clamped_index = min(max(int(source_index), 0), width - 1)

    if mode is None:
        fallback = [0] * width
        fallback[clamped_index] = 1
        return tuple(fallback)

    normalized = tuple(int(value) for value in mode)
    if not normalized:
        fallback = [0] * width
        fallback[clamped_index] = 1
        return tuple(fallback)

    if all(value == 0 for value in normalized):
        return tuple(0 for _ in range(width))

    if len(normalized) == 1:
        single_value = normalized[0]
        if single_value <= 0:
            return tuple(0 for _ in range(width))
        fallback = [0] * width
        slot_index = min(single_value, width) - 1
        fallback[slot_index] = 1
        return tuple(fallback)

    nonzero_indices = [idx for idx, value in enumerate(normalized) if value != 0]
    if len(nonzero_indices) == 1 and normalized[nonzero_indices[0]] > 0:
        if len(normalized) == width:
            return normalized
        fallback = [0] * width
        fallback[clamped_index] = 1
        return tuple(fallback)

    return normalized


_JOSEPHSON_BUILTIN_SETUP_PAYLOADS: dict[str, dict[str, Any]] = {
    "Josephson Parametric Amplifier (JPA)": _build_setup_payload(
        start_ghz=4.5,
        stop_ghz=5.0,
        points=501,
        n_modulation_harmonics=8,
        n_pump_harmonics=16,
        sources=[
            _build_source_payload(
                pump_freq_ghz=4.75001,
                port=1,
                current_amp=0.00565e-6,
                mode=(1,),
            )
        ],
    ),
    "Double-pumped Josephson Parametric Amplifier (JPA)": _build_setup_payload(
        start_ghz=4.5,
        stop_ghz=5.0,
        points=501,
        n_modulation_harmonics=8,
        n_pump_harmonics=8,
        sources=[
            _build_source_payload(
                pump_freq_ghz=4.65001,
                port=1,
                current_amp=0.00565e-6 * 1.7,
                mode=(1, 0),
            ),
            _build_source_payload(
                pump_freq_ghz=4.85001,
                port=1,
                current_amp=0.00565e-6 * 1.7,
                mode=(0, 1),
            ),
        ],
    ),
    "Flux-pumped Josephson Parametric Amplifier (JPA)": _build_setup_payload(
        start_ghz=9.7,
        stop_ghz=9.8,
        points=1001,
        n_modulation_harmonics=8,
        n_pump_harmonics=16,
        sources=[
            _build_source_payload(
                pump_freq_ghz=19.50,
                port=2,
                current_amp=140.3e-6,
                mode=(0,),
            ),
            _build_source_payload(
                pump_freq_ghz=19.50,
                port=2,
                current_amp=0.7e-6,
                mode=(1,),
            ),
        ],
        include_dc=True,
        enable_three_wave_mixing=True,
    ),
    "SNAIL Parametric Amplifier": _build_setup_payload(
        start_ghz=7.8,
        stop_ghz=8.2,
        points=401,
        n_modulation_harmonics=8,
        n_pump_harmonics=16,
        sources=[
            _build_source_payload(
                pump_freq_ghz=16.0,
                port=2,
                current_amp=0.000159,
                mode=(0,),
            ),
            _build_source_payload(
                pump_freq_ghz=16.0,
                port=2,
                current_amp=4.4e-6,
                mode=(1,),
            ),
        ],
        include_dc=True,
        enable_three_wave_mixing=True,
    ),
    "Josephson Traveling Wave Parametric Amplifier (JTWPA)": _build_setup_payload(
        start_ghz=1.0,
        stop_ghz=14.0,
        points=131,
        n_modulation_harmonics=10,
        n_pump_harmonics=20,
        sources=[
            _build_source_payload(
                pump_freq_ghz=7.12,
                port=1,
                current_amp=1.85e-6,
                mode=(1,),
            )
        ],
    ),
    "Floquet JTWPA": _build_setup_payload(
        start_ghz=1.0,
        stop_ghz=14.0,
        points=131,
        n_modulation_harmonics=10,
        n_pump_harmonics=20,
        sources=[
            _build_source_payload(
                pump_freq_ghz=7.9,
                port=1,
                current_amp=1.1e-6,
                mode=(1,),
            )
        ],
    ),
    "Floquet JTWPA with Dissipation": _build_setup_payload(
        start_ghz=1.0,
        stop_ghz=14.0,
        points=131,
        n_modulation_harmonics=10,
        n_pump_harmonics=20,
        sources=[
            _build_source_payload(
                pump_freq_ghz=7.9,
                port=1,
                current_amp=1.1e-6 * (1 + 125e-6),
                mode=(1,),
            )
        ],
    ),
    "Flux-Driven Josephson Traveling-Wave Parametric Amplifier (JTWPA)": _build_setup_payload(
        start_ghz=5.0,
        stop_ghz=25.0,
        points=500,
        n_modulation_harmonics=4,
        n_pump_harmonics=8,
        sources=[
            _build_source_payload(
                pump_freq_ghz=20.0,
                port=3,
                current_amp=0.00019921960989995077,
                mode=(0,),
            ),
            _build_source_payload(
                pump_freq_ghz=20.0,
                port=3,
                current_amp=1.1953176593997045e-05,
                mode=(1,),
            ),
        ],
        include_dc=True,
        enable_three_wave_mixing=True,
        max_iterations=200,
        line_search_switch_tol=1e-5,
        alpha_min=1e-7,
    ),
    "Impedance-engineered JPA": _build_setup_payload(
        start_ghz=4.0,
        stop_ghz=5.8,
        points=181,
        n_modulation_harmonics=4,
        n_pump_harmonics=8,
        sources=[
            _build_source_payload(
                pump_freq_ghz=9.8001,
                port=2,
                current_amp=0.686e-3,
                mode=(0,),
            ),
            _build_source_payload(
                pump_freq_ghz=9.8001,
                port=2,
                current_amp=0.247e-3,
                mode=(1,),
            ),
        ],
        include_dc=True,
        enable_three_wave_mixing=True,
        max_iterations=200,
        line_search_switch_tol=1e-5,
        alpha_min=1e-7,
    ),
}


def _builtin_saved_setups_for_schema(schema_name: str) -> list[dict[str, Any]]:
    """Return built-in saved setups for known JosephsonCircuits example schemas."""
    if not schema_name.startswith(_JOSEPHSON_EXAMPLE_PREFIX):
        return []

    example_name = schema_name.removeprefix(_JOSEPHSON_EXAMPLE_PREFIX).strip()
    payload = _JOSEPHSON_BUILTIN_SETUP_PAYLOADS.get(example_name)
    if payload is None:
        return []

    setup_slug = (
        example_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(",", "")
    )
    return [
        {
            "id": f"builtin:{setup_slug}:official-example",
            "name": "Official Example",
            "saved_at": "builtin",
            "payload": payload,
        }
    ]


def _merge_saved_setups_with_builtin(
    existing_setups: list[dict[str, Any]],
    builtin_setups: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge built-in saved setups while preserving user-created setups."""
    if not builtin_setups:
        return existing_setups

    user_setups = [s for s in existing_setups if str(s.get("saved_at")) != "builtin"]
    return [*builtin_setups, *user_setups]


def _ensure_builtin_saved_setups(schema_id: int, schema_name: str) -> list[dict[str, Any]]:
    """Persist built-in example setups into user storage and return merged list."""
    existing_setups = _load_saved_setups_for_schema(schema_id)
    builtin_setups = _builtin_saved_setups_for_schema(schema_name)
    merged_setups = _merge_saved_setups_with_builtin(existing_setups, builtin_setups)
    if merged_setups != existing_setups:
        _save_saved_setups_for_schema(schema_id, merged_setups)
    return merged_setups


def _has_selected_setup_entry(schema_id: int) -> bool:
    """Return True when user storage already tracks a selected setup for this schema."""
    raw_map = _user_storage_get(_SIM_SETUP_SELECTED_KEY, {})
    return isinstance(raw_map, dict) and str(schema_id) in raw_map


def _result_metric_options_for_family(view_family: str) -> dict[str, str]:
    """Return metric selector options for a result-view family."""
    return dict(_RESULT_METRIC_OPTIONS.get(view_family, _RESULT_METRIC_OPTIONS["s"]))


def _result_trace_options_for_family(view_family: str) -> dict[str, str]:
    """Return trace selector options for a result-view family."""
    return dict(_RESULT_TRACE_OPTIONS.get(view_family, _RESULT_TRACE_OPTIONS["s"]))


def _result_port_options(result: SimulationResult) -> dict[int, str]:
    """Return available output/input port options for the current result bundle."""
    return {port: str(port) for port in result.available_port_indices}


def _format_mode_label(mode: tuple[int, ...]) -> str:
    """Return a readable label for one signal/idler mode tuple."""
    values = ", ".join(str(value) for value in mode)
    if all(value == 0 for value in mode):
        return f"Signal ({values})"
    return f"Sideband ({values})"


def _result_mode_options(result: SimulationResult) -> dict[str, str]:
    """Return mode selector options for the current result bundle."""
    return {
        SimulationResult.mode_token(mode): _format_mode_label(mode)
        for mode in result.available_mode_indices
    }


def _first_option_key(options: dict[str, str]) -> str:
    """Return the first key from a non-empty options dict."""
    return next(iter(options))


def _coerce_int_value(value: object, default: int) -> int:
    """Convert a dynamic UI value to int with a safe fallback."""
    try:
        return int(float(str(value)))
    except Exception:
        return default


def _finite_float_or_none(value: float) -> float | None:
    """Return value only when finite, otherwise None for Plotly gaps."""
    import math

    return value if math.isfinite(value) else None


def _complex_component_series(
    values: list[complex],
    component: str,
) -> list[float | None]:
    """Project complex values to the requested scalar component."""
    import math

    if component == "real":
        return [_finite_float_or_none(value.real) for value in values]
    if component == "imag":
        return [_finite_float_or_none(value.imag) for value in values]
    if component == "magnitude":
        return [_finite_float_or_none(abs(value)) for value in values]
    if component == "phase_deg":
        return [
            _finite_float_or_none(math.degrees(math.atan2(value.imag, value.real)))
            for value in values
        ]
    raise ValueError(f"Unsupported complex component: {component}")


def _post_process_mode_options(
    result: SimulationResult,
    mode_filter: str,
) -> dict[str, str]:
    """Return mode options constrained by one post-processing mode filter."""
    filter_key = str(mode_filter).strip().lower()
    if filter_key == "sideband":
        options = filtered_modes(result, "sideband")
    elif filter_key == "all":
        options = filtered_modes(result, "all")
    else:
        options = filtered_modes(result, "base")
    return {SimulationResult.mode_token(mode): _format_mode_label(mode) for mode in options}


def _format_complex_scalar(value: complex) -> str:
    """Format one complex value into a compact string."""
    return f"{value.real:.4e}{value.imag:+.4e}j"


def _coordinate_weight_fields_editable(weight_mode: str) -> bool:
    """Return whether coordinate-transform alpha/beta fields are editable."""
    return str(weight_mode).strip().lower() == "manual"


def _normalize_termination_mode(mode: object) -> str:
    """Normalize termination compensation mode token."""
    normalized = str(mode or "auto").strip().lower()
    return normalized if normalized in _TERMINATION_MODE_OPTIONS else "auto"


def _normalize_termination_selected_ports(
    raw_ports: object,
    *,
    available_ports: list[int],
) -> list[int]:
    """Normalize one dynamic selected-port payload into sorted unique port indices."""
    if isinstance(raw_ports, int | float | str):
        candidates: list[object] = [raw_ports]
    elif isinstance(raw_ports, list | tuple | set):
        candidates = list(raw_ports)
    else:
        candidates = []
    normalized: set[int] = set()
    allowed = set(available_ports)
    for candidate in candidates:
        try:
            port = int(float(str(candidate)))
        except Exception:
            continue
        if port in allowed:
            normalized.add(port)
    return sorted(normalized)


def _normalize_manual_termination_resistance_map(
    raw_map: object,
    *,
    available_ports: list[int],
    default_ohm: float = _TERMINATION_DEFAULT_RESISTANCE_OHM,
) -> dict[int, float]:
    """Normalize one manual resistance mapping into positive Ohm values per available port."""
    normalized: dict[int, float] = {}
    source_map = raw_map if isinstance(raw_map, dict) else {}
    for port in available_ports:
        value = source_map.get(port, source_map.get(str(port), default_ohm))
        try:
            resistance = float(value)
        except Exception:
            resistance = float(default_ohm)
        if resistance <= 0:
            resistance = float(default_ohm)
        normalized[int(port)] = resistance
    return normalized


def _build_termination_compensation_plan(
    *,
    enabled: bool,
    mode: str,
    selected_ports: list[int],
    manual_resistance_ohm_by_port: dict[int, float],
    inferred_resistance_ohm_by_port: dict[int, float],
    inferred_source_by_port: dict[int, str],
    inferred_warning_by_port: dict[int, str],
    fallback_ohm: float = _TERMINATION_DEFAULT_RESISTANCE_OHM,
) -> dict[str, Any]:
    """Build one resolved termination-compensation execution plan."""
    normalized_mode = _normalize_termination_mode(mode)
    normalized_ports = sorted(set(int(port) for port in selected_ports))
    if not enabled or not normalized_ports:
        return {
            "enabled": False,
            "mode": normalized_mode,
            "selected_ports": normalized_ports,
            "resistance_ohm_by_port": {},
            "source_by_port": {},
            "warnings": [],
        }

    resolved_resistance: dict[int, float] = {}
    resolved_source: dict[int, str] = {}
    warnings: list[str] = []
    if normalized_mode == "manual":
        for port in normalized_ports:
            resistance = float(
                manual_resistance_ohm_by_port.get(port, _TERMINATION_DEFAULT_RESISTANCE_OHM)
            )
            if resistance <= 0:
                resistance = float(fallback_ohm)
                warnings.append(
                    f"Port {port}: invalid manual resistance; fallback to {fallback_ohm:g} Ohm."
                )
            resolved_resistance[port] = resistance
            resolved_source[port] = "manual"
    else:
        for port in normalized_ports:
            resistance = float(
                inferred_resistance_ohm_by_port.get(port, _TERMINATION_DEFAULT_RESISTANCE_OHM)
            )
            if resistance <= 0:
                resistance = float(fallback_ohm)
            resolved_resistance[port] = resistance
            resolved_source[port] = str(inferred_source_by_port.get(port, "fallback_default_50"))
            warning = inferred_warning_by_port.get(port)
            if warning:
                warnings.append(str(warning))

    return {
        "enabled": True,
        "mode": normalized_mode,
        "selected_ports": normalized_ports,
        "resistance_ohm_by_port": resolved_resistance,
        "source_by_port": resolved_source,
        "warnings": warnings,
    }


def _can_save_post_processed_results(
    sweep: PortMatrixSweep | None,
    flow_spec: dict[str, Any] | None,
) -> bool:
    """Return whether post-processed results are ready for dataset persistence."""
    return isinstance(sweep, PortMatrixSweep) and isinstance(flow_spec, dict)


def _build_post_processed_result_payload(
    sweep: PortMatrixSweep,
    *,
    reference_impedance_ohm: float,
) -> tuple[SimulationResult, dict[int, str]]:
    """Convert one post-processed Y sweep into a SimulationResult-like payload."""
    if reference_impedance_ohm <= 0:
        raise ValueError("Reference impedance must be positive.")
    if sweep.dimension < 1:
        raise ValueError("Post-processed sweep has no basis labels.")

    mode = SimulationResult.normalize_mode(sweep.mode)
    frequencies = [float(value) for value in sweep.frequencies_ghz]
    if not frequencies:
        raise ValueError("Post-processed sweep has no frequency points.")

    matrix_count = len(frequencies)
    dim = sweep.dimension
    identity = np.eye(dim, dtype=np.complex128)
    y_matrices: list[np.ndarray] = []
    z_matrices: list[np.ndarray] = []
    s_matrices: list[np.ndarray] = []
    for matrix in sweep.y_matrices:
        y_matrix = np.asarray(matrix, dtype=np.complex128)
        if y_matrix.shape != (dim, dim):
            raise ValueError("Post-processed sweep matrix shape is inconsistent.")
        y_matrices.append(y_matrix)
        try:
            z_matrix = np.linalg.solve(y_matrix, identity)
        except np.linalg.LinAlgError as exc:
            raise ValueError(f"Y->Z conversion failed: {exc}") from exc
        z_matrices.append(z_matrix)
        try:
            s_matrix = np.linalg.solve(
                (z_matrix + (reference_impedance_ohm * identity)).T,
                (z_matrix - (reference_impedance_ohm * identity)).T,
            ).T
        except np.linalg.LinAlgError as exc:
            raise ValueError(f"Z->S conversion failed: {exc}") from exc
        s_matrices.append(s_matrix)

    if len(y_matrices) != matrix_count:
        raise ValueError("Post-processed sweep matrix count does not match frequency points.")

    port_indices = list(range(1, dim + 1))
    port_options = {port: str(sweep.labels[port - 1]) for port in port_indices}
    s_mode_real: dict[str, list[float]] = {}
    s_mode_imag: dict[str, list[float]] = {}
    z_mode_real: dict[str, list[float]] = {}
    z_mode_imag: dict[str, list[float]] = {}
    y_mode_real: dict[str, list[float]] = {}
    y_mode_imag: dict[str, list[float]] = {}
    s_zero_mode_real: dict[str, list[float]] = {}
    s_zero_mode_imag: dict[str, list[float]] = {}

    for output_pos, output_port in enumerate(port_indices):
        for input_pos, input_port in enumerate(port_indices):
            mode_label = SimulationResult._mode_trace_label(mode, output_port, mode, input_port)
            zero_label = f"S{output_port}{input_port}"
            s_trace = [complex(matrix[output_pos, input_pos]) for matrix in s_matrices]
            z_trace = [complex(matrix[output_pos, input_pos]) for matrix in z_matrices]
            y_trace = [complex(matrix[output_pos, input_pos]) for matrix in y_matrices]
            s_mode_real[mode_label] = [float(value.real) for value in s_trace]
            s_mode_imag[mode_label] = [float(value.imag) for value in s_trace]
            z_mode_real[mode_label] = [float(value.real) for value in z_trace]
            z_mode_imag[mode_label] = [float(value.imag) for value in z_trace]
            y_mode_real[mode_label] = [float(value.real) for value in y_trace]
            y_mode_imag[mode_label] = [float(value.imag) for value in y_trace]
            if all(value == 0 for value in mode):
                s_zero_mode_real[zero_label] = list(s_mode_real[mode_label])
                s_zero_mode_imag[zero_label] = list(s_mode_imag[mode_label])

    s11_label = SimulationResult._mode_trace_label(mode, 1, mode, 1)
    s11_real = list(s_mode_real.get(s11_label, [0.0] * matrix_count))
    s11_imag = list(s_mode_imag.get(s11_label, [0.0] * matrix_count))
    converted = SimulationResult(
        frequencies_ghz=frequencies,
        s11_real=s11_real,
        s11_imag=s11_imag,
        port_indices=port_indices,
        mode_indices=[mode],
        s_parameter_real=s_zero_mode_real,
        s_parameter_imag=s_zero_mode_imag,
        s_parameter_mode_real=s_mode_real,
        s_parameter_mode_imag=s_mode_imag,
        z_parameter_mode_real=z_mode_real,
        z_parameter_mode_imag=z_mode_imag,
        y_parameter_mode_real=y_mode_real,
        y_parameter_mode_imag=y_mode_imag,
    )
    return (converted, port_options)


def _default_result_trace_selection(
    result: SimulationResult,
    family: str,
    *,
    port_options: dict[int, str],
) -> _ResultTraceSelection:
    """Return the default trace-card payload for one result family."""
    mode_options = _result_mode_options(result)
    trace_options = _result_trace_options_for_family(family)
    default_mode_token = _first_option_key(mode_options) if mode_options else "0"
    default_port = next(iter(port_options)) if port_options else 1
    return {
        "trace": _first_option_key(trace_options),
        "output_mode": SimulationResult.parse_mode_token(default_mode_token),
        "output_port": default_port,
        "input_mode": SimulationResult.parse_mode_token(default_mode_token),
        "input_port": default_port,
    }


def _render_result_family_explorer(
    *,
    container: Any,
    view_state: dict[str, Any],
    family_options: dict[str, str],
    result_provider: Callable[[float], tuple[SimulationResult, dict[int, str]] | None],
    header_message: str,
    empty_message: str,
    save_button_label: str | None = None,
    on_save_click: Callable[[], None] | None = None,
    save_enabled: bool = True,
    context_line: str | None = None,
) -> None:
    """Render one family/metric/trace-card result explorer into a container."""

    def render() -> None:
        container.clear()
        with container:
            with ui.row().classes("w-full items-center justify-between gap-3 mb-3 flex-wrap"):
                ui.label(header_message).classes("text-xs text-muted")
                if save_button_label is not None and on_save_click is not None:
                    save_button = ui.button(
                        save_button_label,
                        icon="save",
                        on_click=on_save_click,
                    ).props("outline color=primary size=sm")
                    if not save_enabled:
                        save_button.disable()

            if context_line:
                ui.label(context_line).classes("text-xs text-muted mb-2")

            z0_value = float(view_state.get("z0", 50.0) or 50.0)
            try:
                resolved_payload = result_provider(z0_value)
            except Exception as exc:
                with ui.column().classes("w-full items-center justify-center py-10"):
                    ui.icon("error", size="lg").classes("text-danger mb-3")
                    ui.label(f"Result View rendering failed: {exc}").classes("text-sm text-danger")
                return
            if resolved_payload is None:
                with ui.column().classes("w-full items-center justify-center py-10"):
                    ui.icon("show_chart", size="xl").classes("text-muted mb-3 opacity-50")
                    ui.label(empty_message).classes("text-sm text-muted")
                return

            result_to_render, port_options = resolved_payload
            mode_options = _result_mode_options(result_to_render)
            if not port_options:
                port_options = _result_port_options(result_to_render)
            if not mode_options or not port_options:
                ui.label("Result bundle does not contain selectable mode/port entries.").classes(
                    "text-sm text-warning"
                )
                return

            family_tabs = list(family_options.items())
            family_keys = {family for family, _ in family_tabs}
            family_label_to_key = {label.casefold(): family for family, label in family_tabs}
            fallback_family = family_tabs[0][0] if family_tabs else "s"
            view_family = str(view_state.get("family", fallback_family))
            if view_family not in family_keys:
                view_family = fallback_family
                view_state["family"] = view_family

            metric_options = _result_metric_options_for_family(view_family)
            metric_key = str(view_state.get("metric", ""))
            if metric_key not in metric_options:
                metric_key = _first_option_key(metric_options)
                view_state["metric"] = metric_key

            trace_options = _result_trace_options_for_family(view_family)
            normalized_traces: list[_ResultTraceSelection] = []
            for trace in list(view_state.get("traces") or []):
                trace_key = str(trace.get("trace", _first_option_key(trace_options)))
                if trace_key not in trace_options:
                    trace_key = _first_option_key(trace_options)
                output_mode = trace.get("output_mode", (0,))
                input_mode = trace.get("input_mode", (0,))
                output_port = _coerce_int_value(trace.get("output_port"), next(iter(port_options)))
                input_port = _coerce_int_value(trace.get("input_port"), next(iter(port_options)))
                output_mode_token = SimulationResult.mode_token(tuple(output_mode))
                input_mode_token = SimulationResult.mode_token(tuple(input_mode))
                if output_mode_token not in mode_options:
                    output_mode = SimulationResult.parse_mode_token(_first_option_key(mode_options))
                if input_mode_token not in mode_options:
                    input_mode = SimulationResult.parse_mode_token(_first_option_key(mode_options))
                if output_port not in port_options:
                    output_port = next(iter(port_options))
                if input_port not in port_options:
                    input_port = next(iter(port_options))
                normalized_traces.append(
                    {
                        "trace": trace_key,
                        "output_mode": tuple(output_mode),
                        "output_port": output_port,
                        "input_mode": tuple(input_mode),
                        "input_port": input_port,
                    }
                )
            if not normalized_traces:
                normalized_traces = [
                    _default_result_trace_selection(
                        result_to_render,
                        view_family,
                        port_options=port_options,
                    )
                ]
            view_state["traces"] = normalized_traces

            with ui.row().classes("w-full items-end justify-between gap-3 flex-wrap"):
                with ui.tabs(value=view_family).classes("mb-1") as family_switch:
                    for family_key, family_label in family_tabs:
                        ui.tab(family_key, label=family_label)
                metric_select = (
                    ui.select(label="Metric", options=metric_options, value=metric_key)
                    .props("dense outlined options-dense")
                    .classes("w-64")
                )
                z0_input = (
                    ui.number(
                        "Z0 (Ohm)",
                        value=float(view_state.get("z0", 50.0) or 50.0),
                        format="%.6g",
                    )
                    .props(_Z0_CONTROL_PROPS)
                    .classes(_Z0_CONTROL_CLASSES)
                )

            def _on_family_change(e: Any) -> None:
                selected_family = str(e.value or fallback_family).strip()
                if selected_family not in family_keys:
                    selected_family = family_label_to_key.get(
                        selected_family.casefold(),
                        fallback_family,
                    )
                view_state["family"] = selected_family
                view_state["metric"] = _first_option_key(
                    _result_metric_options_for_family(selected_family)
                )
                view_state["traces"] = [
                    _default_result_trace_selection(
                        result_to_render,
                        selected_family,
                        port_options=port_options,
                    )
                ]
                render()

            def _on_metric_change(e: Any) -> None:
                view_state["metric"] = str(e.value or _first_option_key(metric_options))
                render()

            def _on_z0_change(e: Any) -> None:
                view_state["z0"] = float(e.value or 50.0)
                render()

            family_switch.on_value_change(_on_family_change)
            metric_select.on_value_change(_on_metric_change)
            z0_input.on_value_change(_on_z0_change)

            with ui.row().classes("w-full items-center gap-3 mt-1"):
                ui.button(
                    "Add Trace",
                    icon="add",
                    on_click=lambda: (
                        view_state["traces"].append(
                            _default_result_trace_selection(
                                result_to_render,
                                view_family,
                                port_options=port_options,
                            )
                        ),
                        render(),
                    ),
                ).props("outline color=primary")

            trace_cards = list(view_state["traces"])
            for idx, selection in enumerate(trace_cards, start=1):
                with ui.card().classes(
                    "w-full bg-elevated border border-border rounded-lg p-4 mt-3"
                ):
                    with ui.row().classes("w-full items-center gap-3 mb-2"):
                        ui.label(f"Trace {idx}").classes("text-sm font-bold text-fg")
                        if len(trace_cards) > 1:
                            ui.button(
                                "",
                                icon="delete",
                                on_click=lambda _e, target=idx - 1: (
                                    view_state["traces"].pop(target),
                                    render(),
                                ),
                            ).props("flat color=negative round").classes("ml-auto")
                    with ui.row().classes("w-full gap-3 items-end flex-wrap"):
                        trace_select = (
                            ui.select(
                                label="Trace",
                                options=trace_options,
                                value=selection["trace"],
                            )
                            .props("dense outlined options-dense")
                            .classes("w-56")
                        )
                        output_mode_select = (
                            ui.select(
                                label="Output Mode",
                                options=mode_options,
                                value=SimulationResult.mode_token(selection["output_mode"]),
                            )
                            .props("dense outlined options-dense")
                            .classes("w-52")
                        )
                        input_mode_select = (
                            ui.select(
                                label="Input Mode",
                                options=mode_options,
                                value=SimulationResult.mode_token(selection["input_mode"]),
                            )
                            .props("dense outlined options-dense")
                            .classes("w-52")
                        )
                        output_port_select = (
                            ui.select(
                                label="Output Port",
                                options=port_options,
                                value=selection["output_port"],
                            )
                            .props("dense outlined")
                            .classes("w-40")
                        )
                        input_port_select = (
                            ui.select(
                                label="Input Port",
                                options=port_options,
                                value=selection["input_port"],
                            )
                            .props("dense outlined")
                            .classes("w-40")
                        )

                    def _update_trace_config(
                        *,
                        trace_index: int,
                        field: str,
                        value: Any,
                    ) -> None:
                        target = view_state["traces"][trace_index]
                        target[field] = value
                        render()

                    trace_select.on_value_change(
                        lambda e, trace_index=idx - 1: _update_trace_config(
                            trace_index=trace_index,
                            field="trace",
                            value=str(e.value or _first_option_key(trace_options)),
                        )
                    )
                    output_mode_select.on_value_change(
                        lambda e, trace_index=idx - 1: _update_trace_config(
                            trace_index=trace_index,
                            field="output_mode",
                            value=SimulationResult.parse_mode_token(str(e.value or "0")),
                        )
                    )
                    input_mode_select.on_value_change(
                        lambda e, trace_index=idx - 1: _update_trace_config(
                            trace_index=trace_index,
                            field="input_mode",
                            value=SimulationResult.parse_mode_token(str(e.value or "0")),
                        )
                    )
                    output_port_select.on_value_change(
                        lambda e, trace_index=idx - 1: _update_trace_config(
                            trace_index=trace_index,
                            field="output_port",
                            value=_coerce_int_value(e.value, next(iter(port_options))),
                        )
                    )
                    input_port_select.on_value_change(
                        lambda e, trace_index=idx - 1: _update_trace_config(
                            trace_index=trace_index,
                            field="input_port",
                            value=_coerce_int_value(e.value, next(iter(port_options))),
                        )
                    )

            selections = list(view_state["traces"])
            lead = selections[0]
            figure = _build_simulation_result_figure(
                result=result_to_render,
                view_family=view_family,
                metric=str(view_state.get("metric", metric_key)),
                trace=str(lead["trace"]),
                output_mode=tuple(lead["output_mode"]),
                output_port=int(lead["output_port"]),
                input_mode=tuple(lead["input_mode"]),
                input_port=int(lead["input_port"]),
                reference_impedance_ohm=float(view_state.get("z0", 50.0)),
                dark_mode=bool(_user_storage_get("dark_mode", True)),
                trace_selections=selections,
                port_label_by_index=port_options,
            )
            ui.plotly(figure).classes("w-full min-h-[420px] mt-3")

    render()


def _port_signal_node_map(circuit_definition: CircuitDefinition) -> dict[int, str]:
    """Map each declared port index to its non-ground signal node."""
    mapping: dict[int, str] = {}
    for row in circuit_definition.expanded_definition.topology:
        if not row.is_port:
            continue
        try:
            port_index = int(row.value_ref)
        except Exception:
            continue
        if circuit_definition.is_ground_node(row.node1) and not circuit_definition.is_ground_node(
            row.node2
        ):
            mapping[port_index] = str(row.node2)
            continue
        if circuit_definition.is_ground_node(row.node2) and not circuit_definition.is_ground_node(
            row.node1
        ):
            mapping[port_index] = str(row.node1)
    return mapping


def _estimate_port_ground_cap_weights(
    circuit_definition: CircuitDefinition,
    *,
    port_a: int,
    port_b: int,
) -> tuple[float, float] | None:
    """Estimate electrical-centroid weights from capacitor-to-ground totals."""
    port_nodes = _port_signal_node_map(circuit_definition)
    node_a = port_nodes.get(port_a)
    node_b = port_nodes.get(port_b)
    if node_a is None or node_b is None:
        return None

    cap_to_ground: dict[str, float] = {node_a: 0.0, node_b: 0.0}
    for element in circuit_definition.to_ir().elements:
        if element.kind != "capacitor" or element.is_port or element.is_mutual_coupling:
            continue
        if not isinstance(element.value_ref, str):
            continue
        if circuit_definition.is_ground_node(element.node1) and str(element.node2) in cap_to_ground:
            cap_to_ground[str(element.node2)] += circuit_definition.resolve_component_value(
                element.value_ref
            )
        elif (
            circuit_definition.is_ground_node(element.node2) and str(element.node1) in cap_to_ground
        ):
            cap_to_ground[str(element.node1)] += circuit_definition.resolve_component_value(
                element.value_ref
            )

    weight_a = cap_to_ground[node_a]
    weight_b = cap_to_ground[node_b]
    total = weight_a + weight_b
    if total <= 0:
        return None
    return (weight_a / total, weight_b / total)


def _render_post_processing_panel(
    *,
    result: SimulationResult,
    circuit_definition: CircuitDefinition | None = None,
    schema_id: int | None = None,
    schema_name: str | None = None,
    append_status: Callable[[str, str], None] | None = None,
    on_result: Callable[[PortMatrixSweep | None, dict[str, Any] | None], None] | None = None,
) -> None:
    """Render one dynamic card-list style Port-Level post-processing pipeline."""

    def log_info(message: str) -> None:
        if append_status is not None:
            append_status("info", message)

    def emit_result(
        sweep: PortMatrixSweep | None,
        flow_spec: dict[str, Any] | None,
    ) -> None:
        if on_result is not None:
            on_result(sweep, flow_spec)

    port_options = _result_port_options(result)
    default_ports = list(port_options)
    default_port_a = default_ports[0] if default_ports else None
    default_port_b = default_ports[1] if len(default_ports) > 1 else default_port_a
    saved_post_setups = (
        _load_saved_post_process_setups_for_schema(schema_id)
        if isinstance(schema_id, int) and schema_id > 0
        else []
    )
    saved_post_setup_by_id: dict[str, dict[str, Any]] = {
        str(setup.get("id")): setup
        for setup in saved_post_setups
        if setup.get("id") and setup.get("name")
    }
    selected_post_setup_id = (
        _load_selected_post_process_setup_id(schema_id)
        if isinstance(schema_id, int) and schema_id > 0
        else ""
    )
    if selected_post_setup_id not in saved_post_setup_by_id:
        selected_post_setup_id = ""

    ui.label(
        "Port-Level only: Post Processing consumes simulated port-space Y(ω). "
        "Nodal/internal-node elimination is intentionally out of scope in M1. "
        "Auto alpha/beta currently uses schema capacitor-to-ground weights."
    ).classes("text-xs text-muted mb-3")

    with ui.column().classes("w-full gap-3"):
        with ui.card().classes("w-full bg-elevated border border-border rounded-lg p-4"):
            ui.label("Input Node").classes("text-sm font-bold text-fg mb-2")
            with ui.row().classes("w-full items-end gap-3 mb-3 flex-wrap"):
                post_setup_options = {"": "Current (Unsaved)"}
                post_setup_options.update(
                    {
                        setup_id: str(setup.get("name"))
                        for setup_id, setup in saved_post_setup_by_id.items()
                    }
                )
                post_setup_select = (
                    ui.select(
                        label="Post-Processing Setup",
                        options=post_setup_options,
                        value=selected_post_setup_id,
                    )
                    .props("dense outlined options-dense")
                    .classes("w-80")
                )
                save_post_setup_button = (
                    ui.button("Save Setup", icon="bookmark_add")
                    .props("outline color=primary")
                    .classes("shrink-0")
                )
                delete_post_setup_button = (
                    ui.button("", icon="delete")
                    .props("outline color=negative round")
                    .classes("shrink-0")
                )
                if not selected_post_setup_id:
                    delete_post_setup_button.disable()
            with ui.row().classes("w-full items-end gap-3 flex-wrap"):
                mode_filter_select = (
                    ui.select(
                        label="Mode Filter",
                        options=_POST_PROCESS_MODE_FILTER_OPTIONS,
                        value="base",
                    )
                    .props("dense outlined options-dense")
                    .classes("w-40")
                )
                mode_select = (
                    ui.select(
                        label="Mode",
                        options=_post_process_mode_options(result, "base"),
                    )
                    .props("dense outlined options-dense")
                    .classes("w-52")
                )
                z0_input = (
                    ui.number("Z0 (Ohm)", value=50.0, format="%.6g")
                    .props(_Z0_CONTROL_PROPS)
                    .classes(_Z0_CONTROL_CLASSES)
                )
                step_type_select = (
                    ui.select(
                        label="Step Type",
                        options={
                            "coordinate_transform": "Coordinate Transformation",
                            "kron_reduction": "Kron Reduction",
                        },
                        value="coordinate_transform",
                    )
                    .props("dense outlined options-dense")
                    .classes("w-64")
                )
                add_step_button = (
                    ui.button("Add Step", icon="add").props("outline color=primary")
                ).classes("shrink-0")
                run_button = (
                    ui.button("Run Post Processing", icon="tune").props("color=primary")
                ).classes("ml-auto")
            mode_hint = ui.label("").classes("text-xs text-muted mt-2")

        steps_container = ui.column().classes("w-full gap-3")

        with ui.card().classes("w-full bg-elevated border border-border rounded-lg p-4"):
            ui.label("Output Node").classes("text-sm font-bold text-fg mb-2")
            output_container = ui.column().classes("w-full gap-2")

    step_sequence: list[dict[str, Any]] = []
    step_id_seed: dict[str, int] = {"value": 1}
    applying_saved_post_setup = False

    def _make_step_config(step_type: str) -> dict[str, Any]:
        normalized = str(step_type).strip().lower()
        if normalized == "kron_reduction":
            return {
                "type": "kron_reduction",
                "enabled": True,
                "keep_labels": [],
            }
        return {
            "type": "coordinate_transform",
            "enabled": True,
            "template": "cm_dm",
            "weight_mode": "auto",
            "alpha": 0.5,
            "beta": 0.5,
            "port_a": default_port_a,
            "port_b": default_port_b,
        }

    def invalidate_processed_state() -> None:
        emit_result(None, None)

    def _serialized_post_step(step: dict[str, Any]) -> dict[str, Any]:
        step_type = str(step.get("type", "coordinate_transform"))
        if step_type == "kron_reduction":
            return {
                "type": "kron_reduction",
                "enabled": bool(step.get("enabled", True)),
                "keep_labels": [str(label) for label in (step.get("keep_labels") or [])],
            }
        return {
            "type": "coordinate_transform",
            "enabled": bool(step.get("enabled", True)),
            "template": str(step.get("template", "cm_dm")),
            "weight_mode": str(step.get("weight_mode", "auto")),
            "alpha": float(step.get("alpha", 0.5)),
            "beta": float(step.get("beta", 0.5)),
            "port_a": step.get("port_a"),
            "port_b": step.get("port_b"),
        }

    def collect_current_post_setup_payload() -> dict[str, Any]:
        return {
            "mode_filter": str(mode_filter_select.value or "base"),
            "mode_token": str(mode_select.value or ""),
            "reference_impedance_ohm": float(z0_input.value or 50.0),
            "steps": [_serialized_post_step(step) for step in step_sequence],
        }

    def apply_saved_post_setup(setup_record: dict[str, Any]) -> None:
        nonlocal applying_saved_post_setup
        payload = setup_record.get("payload")
        if not isinstance(payload, dict):
            ui.notify("Selected post-processing setup payload is invalid.", type="warning")
            return

        applying_saved_post_setup = True
        try:
            mode_filter_select.value = str(payload.get("mode_filter", "base"))
            refresh_mode_selector()
            desired_mode_token = str(payload.get("mode_token", mode_select.value or ""))
            if (
                desired_mode_token
                and isinstance(mode_select.options, dict)
                and desired_mode_token in mode_select.options
            ):
                mode_select.value = desired_mode_token
            z0_input.value = float(payload.get("reference_impedance_ohm", 50.0))

            step_sequence.clear()
            step_id_seed["value"] = 1
            for raw_step in payload.get("steps", []):
                if not isinstance(raw_step, dict):
                    continue
                normalized = _make_step_config(str(raw_step.get("type", "coordinate_transform")))
                normalized["id"] = step_id_seed["value"]
                step_id_seed["value"] += 1
                normalized["enabled"] = bool(raw_step.get("enabled", normalized["enabled"]))
                if normalized["type"] == "coordinate_transform":
                    normalized["template"] = str(raw_step.get("template", normalized["template"]))
                    normalized["weight_mode"] = str(
                        raw_step.get("weight_mode", normalized["weight_mode"])
                    )
                    normalized["alpha"] = float(raw_step.get("alpha", normalized["alpha"]))
                    normalized["beta"] = float(raw_step.get("beta", normalized["beta"]))
                    normalized["port_a"] = raw_step.get("port_a", normalized["port_a"])
                    normalized["port_b"] = raw_step.get("port_b", normalized["port_b"])
                else:
                    keep_labels = [str(label) for label in (raw_step.get("keep_labels") or [])]
                    normalized["keep_labels"] = keep_labels
                step_sequence.append(normalized)

            invalidate_processed_state()
            render_step_cards.refresh()
        finally:
            applying_saved_post_setup = False

    def refresh_saved_post_setup_select(preferred_id: str | None = None) -> None:
        nonlocal saved_post_setups, saved_post_setup_by_id, selected_post_setup_id
        if not isinstance(schema_id, int) or schema_id <= 0:
            return

        saved_post_setups = _load_saved_post_process_setups_for_schema(schema_id)
        saved_post_setup_by_id = {
            str(setup.get("id")): setup
            for setup in saved_post_setups
            if setup.get("id") and setup.get("name")
        }
        options = {"": "Current (Unsaved)"}
        options.update(
            {setup_id: str(setup.get("name")) for setup_id, setup in saved_post_setup_by_id.items()}
        )
        post_setup_select.options = options
        selected_value = (
            preferred_id if preferred_id in options else str(post_setup_select.value or "")
        )
        if selected_value not in options:
            selected_value = ""
        selected_post_setup_id = selected_value
        post_setup_select.value = selected_value
        _save_selected_post_process_setup_id(schema_id, selected_value)
        if selected_value:
            delete_post_setup_button.enable()
        else:
            delete_post_setup_button.disable()

    def on_post_setup_change(e: Any) -> None:
        nonlocal selected_post_setup_id
        if applying_saved_post_setup:
            return
        selected_value = str(e.value or "")
        selected_post_setup_id = selected_value
        if isinstance(schema_id, int) and schema_id > 0:
            _save_selected_post_process_setup_id(schema_id, selected_value)
        if selected_value:
            delete_post_setup_button.enable()
        else:
            delete_post_setup_button.disable()

        setup_record = saved_post_setup_by_id.get(selected_value)
        if setup_record is None:
            return
        apply_saved_post_setup(setup_record)
        ui.notify(f"Loaded post-processing setup: {setup_record.get('name')}", type="positive")

    def on_save_post_setup_click() -> None:
        if not isinstance(schema_id, int) or schema_id <= 0:
            ui.notify("Save setup requires a selected schema.", type="warning")
            return

        with ui.dialog() as dialog, ui.card().classes("w-full max-w-md bg-surface p-4"):
            ui.label("Save Post-Processing Setup").classes("text-lg font-bold text-fg mb-3")
            default_name = (
                f"{schema_name or 'Schema'} Post-Processing Setup {len(saved_post_setups) + 1}"
            )
            name_input = ui.input("Setup Name", value=default_name).classes("w-full")

            def do_save() -> None:
                setup_name = str(name_input.value or "").strip()
                if not setup_name:
                    ui.notify("Setup name is required.", type="warning")
                    return

                payload = collect_current_post_setup_payload()
                existing = next(
                    (s for s in saved_post_setups if str(s.get("name")) == setup_name),
                    None,
                )
                setup_id = (
                    str(existing.get("id"))
                    if existing is not None and existing.get("id")
                    else datetime.now().strftime("%Y%m%d%H%M%S%f")
                )
                record = {
                    "id": setup_id,
                    "name": setup_name,
                    "saved_at": datetime.now().isoformat(),
                    "payload": payload,
                }
                updated = [s for s in saved_post_setups if str(s.get("id")) != setup_id]
                updated.append(record)
                _save_saved_post_process_setups_for_schema(schema_id, updated)
                refresh_saved_post_setup_select(preferred_id=setup_id)
                ui.notify(f"Saved post-processing setup: {setup_name}", type="positive")
                dialog.close()

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Save", on_click=do_save).props("color=primary")

        dialog.open()

    def on_delete_post_setup_click() -> None:
        if not isinstance(schema_id, int) or schema_id <= 0:
            return
        setup_id = str(post_setup_select.value or "")
        if not setup_id:
            return
        updated = [s for s in saved_post_setups if str(s.get("id")) != setup_id]
        _save_saved_post_process_setups_for_schema(schema_id, updated)
        refresh_saved_post_setup_select(preferred_id="")
        ui.notify("Deleted post-processing setup.", type="positive")

    def _pipeline_labels_before_step(step_id: int | None = None) -> tuple[str, ...]:
        labels = tuple(str(port) for port in sorted(result.available_port_indices))
        if not labels:
            return labels

        for step in step_sequence:
            if step_id is not None and int(step.get("id", -1)) == step_id:
                break
            if not bool(step.get("enabled", True)):
                continue

            step_type = str(step.get("type", ""))
            if step_type == "coordinate_transform":
                if str(step.get("template", "identity")) != "cm_dm":
                    continue
                if not labels:
                    break
                port_a = _coerce_int_value(step.get("port_a"), int(labels[0]))
                port_b = _coerce_int_value(step.get("port_b"), int(labels[-1]))
                label_to_index = {
                    int(label): idx for idx, label in enumerate(labels) if str(label).isdigit()
                }
                if port_a == port_b or port_a not in label_to_index or port_b not in label_to_index:
                    continue
                updated = list(labels)
                idx_a = label_to_index[port_a]
                idx_b = label_to_index[port_b]
                updated[idx_a] = f"cm({port_a},{port_b})"
                updated[idx_b] = f"dm({port_a},{port_b})"
                labels = tuple(updated)
                continue

            if step_type == "kron_reduction":
                keep_labels = [str(label) for label in (step.get("keep_labels") or [])]
                filtered_keep = [label for label in labels if label in set(keep_labels)]
                if filtered_keep:
                    labels = tuple(filtered_keep)

        return labels

    @ui.refreshable
    def render_step_cards() -> None:
        if not step_sequence:
            with ui.card().classes(
                "w-full bg-elevated border border-dashed border-border rounded-lg p-4"
            ):
                ui.label("No steps yet. Use Add Step to build a post-processing pipeline.").classes(
                    "text-sm text-muted"
                )
            return

        for index, step in enumerate(list(step_sequence), start=1):
            step_id = int(step.get("id", -1))
            step_type = str(step.get("type", "coordinate_transform"))
            step_label = (
                "Coordinate Transformation"
                if step_type == "coordinate_transform"
                else "Kron Reduction"
            )
            with ui.card().classes("w-full bg-elevated border border-border rounded-lg p-4"):
                with ui.row().classes("w-full items-center gap-3 mb-2"):
                    ui.label(f"Step {index} · {step_label}").classes("text-sm font-bold text-fg")
                    step_type_select_local = (
                        ui.select(
                            label="Type",
                            options={
                                "coordinate_transform": "Coordinate Transformation",
                                "kron_reduction": "Kron Reduction",
                            },
                            value=step_type,
                        )
                        .props("dense outlined options-dense")
                        .classes("w-64")
                    )
                    enabled_switch_local = ui.switch(
                        "Enable", value=bool(step.get("enabled", True))
                    )
                    delete_button = (
                        ui.button("", icon="delete")
                        .props("flat color=negative round")
                        .classes("ml-auto")
                    )

                def _on_step_type_change(
                    e: Any, target_step: dict[str, Any], target_step_id: int
                ) -> None:
                    replacement = _make_step_config(str(e.value or "coordinate_transform"))
                    replacement["id"] = target_step_id
                    target_step.clear()
                    target_step.update(replacement)
                    invalidate_processed_state()
                    render_step_cards.refresh()

                def _on_step_enable_change(e: Any, target_step: dict[str, Any]) -> None:
                    target_step["enabled"] = bool(e.value)
                    invalidate_processed_state()
                    render_step_cards.refresh()

                def _on_delete_step(target_step_id: int) -> None:
                    step_sequence[:] = [
                        existing
                        for existing in step_sequence
                        if int(existing.get("id", -1)) != target_step_id
                    ]
                    invalidate_processed_state()
                    render_step_cards.refresh()

                step_type_select_local.on_value_change(
                    lambda e, target_step=step, target_step_id=step_id: _on_step_type_change(
                        e,
                        target_step,
                        target_step_id,
                    )
                )
                enabled_switch_local.on_value_change(
                    lambda e, target_step=step: _on_step_enable_change(e, target_step)
                )
                delete_button.on_click(
                    lambda _e, target_step_id=step_id: _on_delete_step(target_step_id)
                )

                if step_type == "coordinate_transform":
                    is_weight_editable = _coordinate_weight_fields_editable(
                        str(step.get("weight_mode", "auto"))
                    )
                    with ui.row().classes("w-full gap-3 items-end flex-wrap"):
                        template_select_local = (
                            ui.select(
                                label="Template",
                                options={
                                    "identity": "Identity",
                                    "cm_dm": "Common/Differential (2 ports)",
                                },
                                value=str(step.get("template", "cm_dm")),
                            )
                            .props("dense outlined options-dense")
                            .classes("w-56")
                        )
                        weight_mode_local = (
                            ui.select(
                                label="Weight Mode",
                                options={
                                    "auto": "Auto (from schema C-to-ground)",
                                    "manual": "Manual",
                                },
                                value=str(step.get("weight_mode", "auto")),
                            )
                            .props("dense outlined options-dense")
                            .classes("w-64")
                        )
                        alpha_local = ui.number(
                            "alpha",
                            value=float(step.get("alpha", 0.5)),
                            format="%.6g",
                        ).classes("w-24")
                        beta_local = ui.number(
                            "beta",
                            value=float(step.get("beta", 0.5)),
                            format="%.6g",
                        ).classes("w-24")
                        if not is_weight_editable:
                            alpha_local.disable()
                            beta_local.disable()
                    with ui.row().classes("w-full gap-3 items-end flex-wrap mt-2"):
                        port_a_local = (
                            ui.select(
                                label="Port A",
                                options=port_options,
                                value=step.get("port_a"),
                            )
                            .props("dense outlined")
                            .classes("w-28")
                        )
                        port_b_local = (
                            ui.select(
                                label="Port B",
                                options=port_options,
                                value=step.get("port_b"),
                            )
                            .props("dense outlined")
                            .classes("w-28")
                        )

                    def _on_coord_change(
                        *,
                        target_step: dict[str, Any],
                        field: str,
                        value: Any,
                        refresh: bool,
                    ) -> None:
                        target_step[field] = value
                        invalidate_processed_state()
                        if refresh:
                            render_step_cards.refresh()

                    template_select_local.on_value_change(
                        lambda e, target_step=step: _on_coord_change(
                            target_step=target_step,
                            field="template",
                            value=str(e.value or "identity"),
                            refresh=True,
                        )
                    )
                    weight_mode_local.on_value_change(
                        lambda e, target_step=step: _on_coord_change(
                            target_step=target_step,
                            field="weight_mode",
                            value=str(e.value or "auto"),
                            refresh=True,
                        )
                    )
                    alpha_local.on_value_change(
                        lambda e, target_step=step: _on_coord_change(
                            target_step=target_step,
                            field="alpha",
                            value=float(e.value or 0.0),
                            refresh=False,
                        )
                    )
                    beta_local.on_value_change(
                        lambda e, target_step=step: _on_coord_change(
                            target_step=target_step,
                            field="beta",
                            value=float(e.value or 0.0),
                            refresh=False,
                        )
                    )
                    port_a_local.on_value_change(
                        lambda e, target_step=step: _on_coord_change(
                            target_step=target_step,
                            field="port_a",
                            value=e.value,
                            refresh=True,
                        )
                    )
                    port_b_local.on_value_change(
                        lambda e, target_step=step: _on_coord_change(
                            target_step=target_step,
                            field="port_b",
                            value=e.value,
                            refresh=True,
                        )
                    )
                else:
                    current_labels = _pipeline_labels_before_step(step_id)
                    selected_keep = {str(label) for label in (step.get("keep_labels") or [])}
                    normalized_keep = [label for label in current_labels if label in selected_keep]
                    if not normalized_keep and current_labels:
                        normalized_keep = list(current_labels)
                    step["keep_labels"] = normalized_keep

                    def _toggle_kron_keep(
                        target_step: dict[str, Any],
                        keep_label: str,
                        available_labels: tuple[str, ...],
                    ) -> None:
                        selected = {str(value) for value in (target_step.get("keep_labels") or [])}
                        if keep_label in selected:
                            selected.remove(keep_label)
                        else:
                            selected.add(keep_label)
                        target_step["keep_labels"] = [
                            label for label in available_labels if label in selected
                        ]
                        invalidate_processed_state()
                        render_step_cards.refresh()

                    def _select_all_kron_keep(
                        target_step: dict[str, Any],
                        available_labels: tuple[str, ...],
                    ) -> None:
                        target_step["keep_labels"] = list(available_labels)
                        invalidate_processed_state()
                        render_step_cards.refresh()

                    def _clear_kron_keep(target_step: dict[str, Any]) -> None:
                        target_step["keep_labels"] = []
                        invalidate_processed_state()
                        render_step_cards.refresh()

                    with ui.column().classes("w-full gap-2"):
                        ui.label("Keep Basis Labels").classes("text-xs text-muted")
                        available_labels_snapshot = current_labels

                        def _on_select_all(
                            _e: Any,
                            target_step: dict[str, Any] = step,
                            labels: tuple[str, ...] = available_labels_snapshot,
                        ) -> None:
                            _select_all_kron_keep(target_step, labels)

                        with ui.row().classes("w-full gap-2 flex-wrap"):
                            for label in available_labels_snapshot:
                                selected = label in set(normalized_keep)
                                button_classes = (
                                    "px-3 py-1 rounded-md text-xs border "
                                    "border-primary bg-primary/10 text-primary"
                                    if selected
                                    else "px-3 py-1 rounded-md text-xs border border-border text-fg"
                                )
                                ui.button(
                                    label,
                                    on_click=(
                                        lambda _e,
                                        keep_label=label,
                                        target_step=step,
                                        labels=available_labels_snapshot: _toggle_kron_keep(
                                            target_step,
                                            keep_label,
                                            labels,
                                        )
                                    ),
                                ).props("no-caps dense flat").classes(button_classes)
                        with ui.row().classes("w-full gap-2 items-center flex-wrap"):
                            ui.button(
                                "Select All",
                                on_click=_on_select_all,
                            ).props("dense flat no-caps")
                            ui.button(
                                "Clear",
                                on_click=lambda _e, target_step=step: _clear_kron_keep(target_step),
                            ).props("dense flat no-caps")
                            ui.label(
                                "Current basis: "
                                + (", ".join(current_labels) if current_labels else "(empty)")
                            ).classes("text-xs text-muted")

    def refresh_mode_selector() -> None:
        options = _post_process_mode_options(result, str(mode_filter_select.value or "base"))
        mode_select.options = options
        if not options:
            mode_select.value = None
            mode_select.disable()
            run_button.disable()
            mode_hint.text = "No compatible modes for this filter."
            invalidate_processed_state()
            return
        if mode_select.value not in options:
            mode_select.value = next(iter(options))
        mode_select.enable()
        run_button.enable()
        mode_hint.text = f"{len(options)} mode(s) available."

    def add_step() -> None:
        step_type = str(step_type_select.value or "coordinate_transform")
        step_config = _make_step_config(step_type)
        step_config["id"] = step_id_seed["value"]
        step_id_seed["value"] += 1
        if step_type == "kron_reduction":
            step_config["keep_labels"] = list(_pipeline_labels_before_step())
        step_sequence.append(step_config)
        invalidate_processed_state()
        render_step_cards.refresh()

    def run_post_processing() -> None:
        output_container.clear()
        try:
            mode_token = str(mode_select.value or "").strip()
            if not mode_token:
                raise ValueError("Please select one mode before running post-processing.")
            mode = SimulationResult.parse_mode_token(mode_token)
            z0 = float(z0_input.value or 50.0)
            if z0 <= 0:
                raise ValueError("Z0 must be positive.")

            sweep = build_port_y_sweep(
                result=result,
                mode=mode,
                reference_impedance_ohm=z0,
            )
            flow_steps: list[dict[str, Any]] = []

            for step in step_sequence:
                if not bool(step.get("enabled", True)):
                    continue

                step_type = str(step.get("type", "coordinate_transform"))
                if step_type == "coordinate_transform":
                    template = str(step.get("template", "identity"))
                    if template == "cm_dm":
                        if sweep.dimension < 2:
                            raise ValueError(
                                "Common/Differential transform requires "
                                "at least two available ports."
                            )
                        default_label = sweep.labels[0] if sweep.labels else "1"
                        fallback_port = int(default_label) if default_label.isdigit() else 1
                        selected_port_a = _coerce_int_value(step.get("port_a"), fallback_port)
                        selected_port_b = _coerce_int_value(step.get("port_b"), fallback_port)
                        if selected_port_a == selected_port_b:
                            raise ValueError("Port A and Port B must be different.")

                        label_to_index = {
                            int(label): idx
                            for idx, label in enumerate(sweep.labels)
                            if label.isdigit()
                        }
                        if (
                            selected_port_a not in label_to_index
                            or selected_port_b not in label_to_index
                        ):
                            raise ValueError(
                                "Selected ports are not available in current sweep basis."
                            )

                        if str(step.get("weight_mode", "auto")) == "auto":
                            if circuit_definition is None:
                                raise ValueError(
                                    "Auto weight mode requires a loaded circuit definition."
                                )
                            estimated = _estimate_port_ground_cap_weights(
                                circuit_definition,
                                port_a=selected_port_a,
                                port_b=selected_port_b,
                            )
                            if estimated is None:
                                raise ValueError(
                                    "Unable to estimate auto weights from "
                                    "capacitor-to-ground topology. "
                                    "Switch to manual mode."
                                )
                            alpha, beta = estimated
                            step["alpha"] = alpha
                            step["beta"] = beta
                        else:
                            alpha = float(step.get("alpha", 0.0))
                            beta = float(step.get("beta", 0.0))

                        transform = build_common_differential_transform(
                            dimension=sweep.dimension,
                            first_index=label_to_index[selected_port_a],
                            second_index=label_to_index[selected_port_b],
                            alpha=alpha,
                            beta=beta,
                        )
                        labels = list(sweep.labels)
                        idx_a = label_to_index[selected_port_a]
                        idx_b = label_to_index[selected_port_b]
                        labels[idx_a] = f"cm({selected_port_a},{selected_port_b})"
                        labels[idx_b] = f"dm({selected_port_a},{selected_port_b})"
                        sweep = apply_coordinate_transform(
                            sweep,
                            transform_matrix=transform,
                            labels=tuple(labels),
                        )
                        flow_steps.append(
                            {
                                "step_id": int(step.get("id", -1)),
                                "type": "coordinate_transform",
                                "template": "cm_dm",
                                "weight_mode": str(step.get("weight_mode", "auto")),
                                "port_a": selected_port_a,
                                "port_b": selected_port_b,
                                "alpha": alpha,
                                "beta": beta,
                            }
                        )
                    else:
                        flow_steps.append(
                            {
                                "step_id": int(step.get("id", -1)),
                                "type": "coordinate_transform",
                                "template": "identity",
                            }
                        )
                    continue

                keep_tokens = {str(label) for label in (step.get("keep_labels") or [])}
                selected_keep_labels = [label for label in sweep.labels if label in keep_tokens]
                keep_indices = [
                    index for index, label in enumerate(sweep.labels) if label in keep_tokens
                ]
                if not keep_indices:
                    raise ValueError("Kron reduction requires at least one kept basis label.")
                sweep = kron_reduce(sweep, keep_indices=keep_indices)
                flow_steps.append(
                    {
                        "step_id": int(step.get("id", -1)),
                        "type": "kron_reduction",
                        "keep_indices": list(keep_indices),
                        "keep_labels": selected_keep_labels,
                    }
                )

            flow_spec: dict[str, Any] = {
                "mode_filter": str(mode_filter_select.value or "base"),
                "mode_token": SimulationResult.mode_token(mode),
                "reference_impedance_ohm": z0,
                "steps": flow_steps,
            }
            emit_result(sweep, flow_spec)
            render_step_cards.refresh()

            log_info(
                "Post Processing completed: "
                f"mode={sweep.mode}, dim={sweep.dimension}, source={sweep.source_kind}."
            )

            with output_container:
                ui.label("Pipeline output ready. Post Processing Result View is updated.").classes(
                    "text-sm text-positive"
                )
                ui.label(
                    f"Basis labels: {', '.join(sweep.labels)} | "
                    f"dim={sweep.dimension} | "
                    f"mode={SimulationResult.mode_token(sweep.mode)}"
                ).classes("text-xs text-muted")
        except Exception as exc:
            invalidate_processed_state()
            log_info(f"Post Processing failed: {exc}")
            with output_container:
                ui.label(f"Post Processing failed: {exc}").classes("text-sm text-danger")

    post_setup_select.on_value_change(on_post_setup_change)
    save_post_setup_button.on_click(lambda _e: on_save_post_setup_click())
    delete_post_setup_button.on_click(lambda _e: on_delete_post_setup_click())
    if isinstance(schema_id, int) and schema_id > 0:
        refresh_saved_post_setup_select(preferred_id=selected_post_setup_id)
        selected_setup_record = saved_post_setup_by_id.get(str(post_setup_select.value or ""))
        if isinstance(selected_setup_record, dict):
            apply_saved_post_setup(selected_setup_record)

    mode_filter_select.on_value_change(
        lambda _e: (invalidate_processed_state(), refresh_mode_selector())
    )
    mode_select.on_value_change(lambda _e: invalidate_processed_state())
    z0_input.on_value_change(lambda _e: invalidate_processed_state())
    add_step_button.on_click(lambda _e: add_step())
    run_button.on("click", lambda _e: run_post_processing())

    refresh_mode_selector()
    with steps_container:
        render_step_cards()


def _format_export_suffix(
    output_mode: tuple[int, ...],
    input_mode: tuple[int, ...] | None = None,
) -> str:
    """Build a concise mode suffix for exported dataset parameter names."""
    if input_mode is None:
        if all(value == 0 for value in output_mode):
            return ""
        return f" [om={output_mode}]"

    if all(value == 0 for value in output_mode) and all(value == 0 for value in input_mode):
        return ""
    return f" [om={output_mode}, im={input_mode}]"


def _format_mode_matrix_parameter_name(
    prefix: str,
    label: str,
) -> str:
    """Convert an internal mode-aware trace key into a user-facing parameter name."""
    parsed = SimulationResult._parse_mode_trace_label(label)
    if parsed is None:
        return f"{prefix}?"
    output_mode, output_port, input_mode, input_port = parsed
    base = f"{prefix}{output_port}{input_port}"
    return f"{base}{_format_export_suffix(output_mode, input_mode)}"


def _format_mode_cm_parameter_name(label: str) -> str:
    """Convert an internal CM trace key into a user-facing parameter name."""
    parsed = SimulationResult._parse_cm_trace_label(label)
    if parsed is None:
        return "CM?"
    output_mode, output_port = parsed
    base = f"CM{output_port}"
    return f"{base}{_format_export_suffix(output_mode)}"


def _build_mode_complex_data_records(
    *,
    dataset_id: int,
    data_type: str,
    parameter_prefix: str,
    real_map: dict[str, list[float]],
    imag_map: dict[str, list[float]],
    frequencies_ghz: list[float],
) -> list[DataRecord]:
    """Convert one complex-valued bundle into DataRecord rows."""
    frequency_axis = [{"name": "frequency", "unit": "GHz", "values": frequencies_ghz}]
    records: list[DataRecord] = []

    for label in sorted(set(real_map) & set(imag_map)):
        parameter_name = _format_mode_matrix_parameter_name(parameter_prefix, label)
        records.append(
            DataRecord(
                dataset_id=dataset_id,
                data_type=data_type,
                parameter=parameter_name,
                representation="real",
                axes=frequency_axis,
                values=real_map[label],
            )
        )
        records.append(
            DataRecord(
                dataset_id=dataset_id,
                data_type=data_type,
                parameter=parameter_name,
                representation="imaginary",
                axes=frequency_axis,
                values=imag_map[label],
            )
        )

    return records


def _build_mode_scalar_data_records(
    *,
    dataset_id: int,
    data_type: str,
    parameter_prefix: str,
    values_map: dict[str, list[float]],
    frequencies_ghz: list[float],
) -> list[DataRecord]:
    """Convert one scalar-valued bundle into DataRecord rows."""
    frequency_axis = [{"name": "frequency", "unit": "GHz", "values": frequencies_ghz}]
    records: list[DataRecord] = []

    for label in sorted(values_map):
        parameter_name = (
            _format_mode_cm_parameter_name(label)
            if parameter_prefix == "CM"
            else _format_mode_matrix_parameter_name(parameter_prefix, label)
        )
        records.append(
            DataRecord(
                dataset_id=dataset_id,
                data_type=data_type,
                parameter=parameter_name,
                representation="value",
                axes=frequency_axis,
                values=values_map[label],
            )
        )

    return records


def _sanitize_postprocess_label_token(label: str) -> str:
    """Sanitize one transformed basis label for parameter naming."""
    sanitized = (
        str(label)
        .replace(" ", "")
        .replace("(", "_")
        .replace(")", "")
        .replace(",", "_")
        .replace("[", "_")
        .replace("]", "")
        .replace("/", "_")
        .replace("-", "_")
    )
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    return sanitized.strip("_") or "x"


def _format_post_processed_y_parameter_name(
    *,
    row_label: str,
    col_label: str,
    mode: tuple[int, ...],
) -> str:
    """Build one output parameter name for a post-processed Y-matrix entry."""
    if row_label.isdigit() and col_label.isdigit():
        base = f"Y{row_label}{col_label}"
    else:
        sanitized_row = _sanitize_postprocess_label_token(row_label)
        sanitized_col = _sanitize_postprocess_label_token(col_label)
        base = f"Y_{sanitized_row}_{sanitized_col}"
    return f"{base}{_format_export_suffix(mode, mode)}"


def _build_post_processed_y_data_records(
    *,
    dataset_id: int,
    sweep: PortMatrixSweep,
) -> list[DataRecord]:
    """Convert one post-processed Y sweep into real/imaginary DataRecord rows."""
    frequency_axis = [{"name": "frequency", "unit": "GHz", "values": list(sweep.frequencies_ghz)}]
    records: list[DataRecord] = []

    for row_index, row_label in enumerate(sweep.labels):
        for col_index, col_label in enumerate(sweep.labels):
            parameter_name = _format_post_processed_y_parameter_name(
                row_label=row_label,
                col_label=col_label,
                mode=sweep.mode,
            )
            trace_values = sweep.trace(row_index, col_index)
            records.append(
                DataRecord(
                    dataset_id=dataset_id,
                    data_type="y_params",
                    parameter=parameter_name,
                    representation="real",
                    axes=frequency_axis,
                    values=[_finite_float_or_none(value.real) for value in trace_values],
                )
            )
            records.append(
                DataRecord(
                    dataset_id=dataset_id,
                    data_type="y_params",
                    parameter=parameter_name,
                    representation="imaginary",
                    axes=frequency_axis,
                    values=[_finite_float_or_none(value.imag) for value in trace_values],
                )
            )
    return records


def _port_label_token(label: str) -> str:
    """Convert one port label into a stable matrix-name token."""
    normalized = str(label).strip()
    if not normalized:
        return "x"
    head = normalized.split("(", maxsplit=1)[0].strip()
    candidate = head or normalized
    if candidate.isdigit():
        return candidate
    sanitized = re.sub(r"[^0-9a-zA-Z]+", "_", candidate).strip("_")
    return (sanitized or "x").lower()


def _matrix_element_name(
    *,
    matrix_symbol: str,
    output_port: int,
    input_port: int,
    port_label_by_index: dict[int, str] | None,
) -> str:
    """Build one matrix element name aligned with trace-card port labels."""
    output_label = (
        str(port_label_by_index.get(output_port, output_port))
        if port_label_by_index
        else str(output_port)
    )
    input_label = (
        str(port_label_by_index.get(input_port, input_port))
        if port_label_by_index
        else str(input_port)
    )
    output_token = _port_label_token(output_label)
    input_token = _port_label_token(input_label)

    labels_are_plain_numeric = (not port_label_by_index) or all(
        str(label).strip().isdigit() for label in port_label_by_index.values()
    )
    if (
        labels_are_plain_numeric
        and output_token.isdigit()
        and input_token.isdigit()
    ):
        return f"{matrix_symbol}{output_token}{input_token}"
    return f"{matrix_symbol}_{output_token}_{input_token}"


def _build_simulation_result_figure(
    result: SimulationResult,
    view_family: str,
    metric: str,
    trace: str,
    output_mode: tuple[int, ...],
    output_port: int,
    input_mode: tuple[int, ...],
    input_port: int,
    reference_impedance_ohm: float,
    dark_mode: bool,
    trace_selections: list[_ResultTraceSelection] | None = None,
    port_label_by_index: dict[int, str] | None = None,
) -> go.Figure:
    """Build the selected simulation result figure from the cached result bundle."""
    freq_values = result.frequencies_ghz
    fig = go.Figure()
    x_axis_title = "Frequency (GHz)"
    y_axis_title = "Value"
    title = "Simulation Result"
    single_selection: _ResultTraceSelection = {
        "trace": trace,
        "output_mode": output_mode,
        "output_port": output_port,
        "input_mode": input_mode,
        "input_port": input_port,
    }
    resolved_selections = trace_selections or [single_selection]
    trace_titles: list[str] = []

    def add_trace_for_selection(
        *,
        trace_index: int,
        selected_trace: str,
        selected_output_mode: tuple[int, ...],
        selected_output_port: int,
        selected_input_mode: tuple[int, ...],
        selected_input_port: int,
    ) -> str:
        nonlocal x_axis_title, y_axis_title

        mode_suffix = _format_export_suffix(selected_output_mode, selected_input_mode)
        s_name = _matrix_element_name(
            matrix_symbol="S",
            output_port=selected_output_port,
            input_port=selected_input_port,
            port_label_by_index=port_label_by_index,
        )
        z_name = _matrix_element_name(
            matrix_symbol="Z",
            output_port=selected_output_port,
            input_port=selected_input_port,
            port_label_by_index=port_label_by_index,
        )
        y_name = _matrix_element_name(
            matrix_symbol="Y",
            output_port=selected_output_port,
            input_port=selected_input_port,
            port_label_by_index=port_label_by_index,
        )
        gain_name = _matrix_element_name(
            matrix_symbol="Gain",
            output_port=selected_output_port,
            input_port=selected_input_port,
            port_label_by_index=port_label_by_index,
        )
        s_label = f"{s_name}{mode_suffix}"
        z_label = f"{z_name}{mode_suffix}"
        y_label = f"{y_name}{mode_suffix}"
        gain_label = f"{gain_name}{mode_suffix}"
        line_style = dict(
            color=_RESULT_TRACE_COLORS[trace_index % len(_RESULT_TRACE_COLORS)],
            width=2,
        )

        if view_family == "s":
            if metric == "magnitude_db":
                y_values = result.get_mode_s_parameter_db(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Magnitude (dB)"
                trace_title = f"{s_label} Magnitude (dB)"
            elif metric == "phase_deg":
                y_values = result.get_mode_s_parameter_phase_deg(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Phase (deg)"
                trace_title = f"{s_label} Phase"
            elif metric == "real":
                y_values = result.get_mode_s_parameter_real(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Real"
                trace_title = f"{s_label} Real Part"
            elif metric == "imag":
                y_values = result.get_mode_s_parameter_imag(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Imaginary"
                trace_title = f"{s_label} Imaginary Part"
            else:
                y_values = result.get_mode_s_parameter_magnitude(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Magnitude (linear)"
                trace_title = f"{s_label} Magnitude"

            fig.add_trace(
                go.Scatter(
                    x=freq_values,
                    y=y_values,
                    mode="lines",
                    name=s_label,
                    line=line_style,
                )
            )
            return trace_title

        if view_family == "gain":
            if metric == "gain_linear":
                y_values = result.get_mode_gain_linear(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Gain (linear)"
                trace_title = f"{gain_label} (linear)"
            else:
                y_values = result.get_mode_gain_db(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                y_axis_title = "Gain (dB)"
                trace_title = f"{gain_label} (dB)"

            fig.add_trace(
                go.Scatter(
                    x=freq_values,
                    y=y_values,
                    mode="lines",
                    name=gain_label,
                    line=line_style,
                )
            )
            return trace_title

        if view_family == "impedance":
            try:
                z_values = result.get_mode_z_parameter_complex(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
            except KeyError:
                z_values = result.calculate_input_impedance_ohm(
                    reference_impedance_ohm,
                    port=selected_output_port,
                )
            y_values = _complex_component_series(z_values, metric)
            if metric == "real":
                trace_title = f"{z_label} Real Part"
                y_axis_title = "Real (Ohm)"
            elif metric == "imag":
                trace_title = f"{z_label} Imaginary Part"
                y_axis_title = "Imaginary (Ohm)"
            else:
                trace_title = f"{z_label} Magnitude"
                y_axis_title = "Magnitude (Ohm)"

            fig.add_trace(
                go.Scatter(
                    x=freq_values,
                    y=y_values,
                    mode="lines",
                    name=z_label,
                    line=line_style,
                )
            )
            return trace_title

        if view_family == "admittance":
            try:
                y_values_complex = result.get_mode_y_parameter_complex(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
            except KeyError:
                y_values_complex = result.calculate_input_admittance_s(
                    reference_impedance_ohm,
                    port=selected_output_port,
                )
            y_values = _complex_component_series(y_values_complex, metric)
            if metric == "real":
                trace_title = f"{y_label} Real Part"
                y_axis_title = "Real (S)"
            elif metric == "imag":
                trace_title = f"{y_label} Imaginary Part"
                y_axis_title = "Imaginary (S)"
            else:
                trace_title = f"{y_label} Magnitude"
                y_axis_title = "Magnitude (S)"

            fig.add_trace(
                go.Scatter(
                    x=freq_values,
                    y=y_values,
                    mode="lines",
                    name=y_label,
                    line=line_style,
                )
            )
            return trace_title

        if view_family == "qe":
            if selected_trace == "qe_ideal":
                y_values = result.get_mode_qe_ideal(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                trace_title = f"QE Ideal {selected_output_port}{selected_input_port}{mode_suffix}"
            else:
                y_values = result.get_mode_qe(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                trace_title = f"QE {selected_output_port}{selected_input_port}{mode_suffix}"
            y_axis_title = "Quantum Efficiency"
            fig.add_trace(
                go.Scatter(
                    x=freq_values,
                    y=y_values,
                    mode="lines",
                    name=trace_title,
                    line=line_style,
                )
            )
            return trace_title

        if view_family == "cm":
            y_values = result.get_mode_cm(selected_output_mode, selected_output_port)
            trace_title = f"CM{selected_output_port}{_format_export_suffix(selected_output_mode)}"
            y_axis_title = "Commutation"
            fig.add_trace(
                go.Scatter(
                    x=freq_values,
                    y=y_values,
                    mode="lines",
                    name=trace_title,
                    line=line_style,
                )
            )
            return trace_title

        if view_family == "complex":
            if selected_trace == "z":
                try:
                    complex_values = result.get_mode_z_parameter_complex(
                        selected_output_mode,
                        selected_output_port,
                        selected_input_mode,
                        selected_input_port,
                    )
                except KeyError:
                    complex_values = result.calculate_input_impedance_ohm(
                        reference_impedance_ohm,
                        port=selected_output_port,
                    )
                trace_name = z_label
                trace_title = f"{z_label} Complex Plane"
            elif selected_trace == "y":
                try:
                    complex_values = result.get_mode_y_parameter_complex(
                        selected_output_mode,
                        selected_output_port,
                        selected_input_mode,
                        selected_input_port,
                    )
                except KeyError:
                    complex_values = result.calculate_input_admittance_s(
                        reference_impedance_ohm,
                        port=selected_output_port,
                    )
                trace_name = y_label
                trace_title = f"{y_label} Complex Plane"
            else:
                complex_values = result.get_mode_s_parameter_complex(
                    selected_output_mode,
                    selected_output_port,
                    selected_input_mode,
                    selected_input_port,
                )
                trace_name = s_label
                trace_title = f"{s_label} Complex Plane"

            fig.add_trace(
                go.Scatter(
                    x=[_finite_float_or_none(value.real) for value in complex_values],
                    y=[_finite_float_or_none(value.imag) for value in complex_values],
                    mode="lines+markers",
                    name=trace_name,
                    line=line_style,
                    marker=dict(size=5, color=line_style["color"]),
                    customdata=freq_values,
                    hovertemplate=(
                        "Re=%{x}<br>Im=%{y}<br>f=%{customdata:.6f} GHz"
                        f"<extra>{trace_name}</extra>"
                    ),
                )
            )
            x_axis_title = "Real"
            y_axis_title = "Imaginary"
            return trace_title

        raise ValueError(f"Unsupported result view family: {view_family}")

    for idx, selection in enumerate(resolved_selections):
        trace_titles.append(
            add_trace_for_selection(
                trace_index=idx,
                selected_trace=selection["trace"],
                selected_output_mode=selection["output_mode"],
                selected_output_port=selection["output_port"],
                selected_input_mode=selection["input_mode"],
                selected_input_port=selection["input_port"],
            )
        )

    title_suffix = ""
    if len(trace_titles) > 1:
        preview_titles = ", ".join(trace_titles[:3])
        if len(trace_titles) > 3:
            preview_titles = f"{preview_titles}, +{len(trace_titles) - 3} more"
        title_suffix = f": {preview_titles}"

    if len(trace_titles) == 1:
        title = trace_titles[0]
    elif view_family == "complex":
        title = f"Complex Plane Comparison{title_suffix}"
    elif view_family == "gain":
        title = (
            f"Gain Comparison{title_suffix}"
            if metric == "gain_linear"
            else f"Gain (dB) Comparison{title_suffix}"
        )
    elif view_family == "impedance":
        title = f"Impedance Comparison{title_suffix}"
    elif view_family == "admittance":
        title = f"Admittance Comparison{title_suffix}"
    elif view_family == "qe":
        title = f"Quantum Efficiency Comparison{title_suffix}"
    elif view_family == "cm":
        title = f"Commutation Comparison{title_suffix}"
    elif view_family == "s":
        if metric == "magnitude_db":
            title = f"S-Parameter Magnitude (dB){title_suffix}"
        elif metric == "phase_deg":
            title = f"S-Parameter Phase{title_suffix}"
        elif metric == "real":
            title = f"S-Parameter Real Part{title_suffix}"
        elif metric == "imag":
            title = f"S-Parameter Imaginary Part{title_suffix}"
        else:
            title = f"S-Parameter Magnitude{title_suffix}"
    else:
        raise ValueError(f"Unsupported result view family: {view_family}")

    theme_layout = get_plotly_layout(dark=dark_mode)
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        margin=dict(l=40, r=20, t=40, b=40),
        showlegend=True,
        hovermode="closest" if view_family == "complex" else "x unified",
        **theme_layout,
    )
    return fig


def _build_s_parameter_data_records(dataset_id: int, result: SimulationResult) -> list[DataRecord]:
    """Convert the cached zero-mode S-parameter bundle into DataRecord rows."""
    frequency_axis = [{"name": "frequency", "unit": "GHz", "values": result.frequencies_ghz}]
    records: list[DataRecord] = []

    for trace_label in result.available_s_parameter_labels:
        records.append(
            DataRecord(
                dataset_id=dataset_id,
                data_type="s_params",
                parameter=trace_label,
                representation="real",
                axes=frequency_axis,
                values=result.get_s_parameter_real_by_label(trace_label),
            )
        )
        records.append(
            DataRecord(
                dataset_id=dataset_id,
                data_type="s_params",
                parameter=trace_label,
                representation="imaginary",
                axes=frequency_axis,
                values=result.get_s_parameter_imag_by_label(trace_label),
            )
        )

    return records


def _build_result_bundle_data_records(
    dataset_id: int,
    result: SimulationResult,
) -> list[DataRecord]:
    """Convert all cached simulation bundles into DataRecord rows."""
    records: list[DataRecord] = []

    records.extend(
        _build_mode_complex_data_records(
            dataset_id=dataset_id,
            data_type="s_params",
            parameter_prefix="S",
            real_map=result.s_parameter_mode_real or result._resolved_mode_s_parameter_real(),
            imag_map=result.s_parameter_mode_imag or result._resolved_mode_s_parameter_imag(),
            frequencies_ghz=result.frequencies_ghz,
        )
    )
    records.extend(
        _build_mode_complex_data_records(
            dataset_id=dataset_id,
            data_type="z_params",
            parameter_prefix="Z",
            real_map=result.z_parameter_mode_real,
            imag_map=result.z_parameter_mode_imag,
            frequencies_ghz=result.frequencies_ghz,
        )
    )
    records.extend(
        _build_mode_complex_data_records(
            dataset_id=dataset_id,
            data_type="y_params",
            parameter_prefix="Y",
            real_map=result.y_parameter_mode_real,
            imag_map=result.y_parameter_mode_imag,
            frequencies_ghz=result.frequencies_ghz,
        )
    )
    records.extend(
        _build_mode_scalar_data_records(
            dataset_id=dataset_id,
            data_type="qe",
            parameter_prefix="QE",
            values_map=result.qe_parameter_mode,
            frequencies_ghz=result.frequencies_ghz,
        )
    )
    records.extend(
        _build_mode_scalar_data_records(
            dataset_id=dataset_id,
            data_type="qe_ideal",
            parameter_prefix="QEideal",
            values_map=result.qe_ideal_parameter_mode,
            frequencies_ghz=result.frequencies_ghz,
        )
    )
    records.extend(
        _build_mode_scalar_data_records(
            dataset_id=dataset_id,
            data_type="commutation",
            parameter_prefix="CM",
            values_map=result.cm_parameter_mode,
            frequencies_ghz=result.frequencies_ghz,
        )
    )

    if not records:
        records.extend(_build_s_parameter_data_records(dataset_id, result))

    return records


def _summarize_simulation_error(error: Exception | str) -> tuple[str, str]:
    """Map raw Julia/Python errors to a user-friendly summary and detail."""
    detail = str(error)
    if len(detail) > 4000:
        detail = f"{detail[:4000]}\n... (truncated)"

    if "SimulationInputError:" in detail:
        message = detail.split("SimulationInputError:", maxsplit=1)[1].strip().splitlines()[0]
        return (f"Input error: {message}", detail)
    if "SimulationNumericalError:" in detail:
        message = detail.split("SimulationNumericalError:", maxsplit=1)[1].strip().splitlines()[0]
        return (f"Numerical solver error: {message}", detail)
    if "Ports without resistors detected" in detail:
        return (
            "Invalid schema: each port needs a matching resistor (for example 50 Ohm).",
            detail,
        )
    if "SingularException" in detail:
        return (
            "Simulation matrix became singular. Check topology connectivity and parameter values.",
            detail,
        )
    if "Package JosephsonCircuits not found" in detail:
        return (
            "Julia dependency is not ready in this worker process. Please retry once.",
            detail,
        )

    first_line = next(
        (line.strip() for line in detail.splitlines() if line.strip()),
        "Unknown error",
    )
    return (first_line[:220], detail)


def _load_latest_circuit_definition(schema_id: int) -> tuple[CircuitRecord, CircuitDefinition]:
    """Load the latest schema record from DB and parse CircuitDefinition."""
    with get_unit_of_work() as uow:
        latest_record = uow.circuits.get(schema_id)

    if latest_record is None:
        raise ValueError(f"SimulationInputError: schema id={schema_id} was not found.")

    try:
        circuit_def = parse_circuit_definition_source(latest_record.definition_json)
    except Exception as exc:
        raise ValueError(
            "SimulationInputError: active schema is invalid. "
            "Required fields: name, components, topology."
        ) from exc

    return latest_record, circuit_def


def _extract_available_port_indices(circuit: CircuitDefinition) -> set[int]:
    """Collect schema-declared port indices from public port declarations."""
    return set(circuit.available_port_indices)


def _detect_harmonic_grid_coincidences(
    freq_range: FrequencyRange,
    sources: list[DriveSourceConfig],
    max_pump_harmonic: int,
) -> list[tuple[int, int, float, int]]:
    """Find source harmonic frequencies that land exactly on a sweep grid point."""
    if freq_range.points < 2 or max_pump_harmonic < 1 or not sources:
        return []

    start = float(freq_range.start_ghz)
    stop = float(freq_range.stop_ghz)
    step = (stop - start) / float(freq_range.points - 1)
    if step <= 0:
        return []

    hits: list[tuple[int, int, float, int]] = []
    for source_index, source in enumerate(sources, start=1):
        if source.mode_components is not None and all(
            value == 0 for value in source.mode_components
        ):
            continue
        fp = float(source.pump_freq_ghz)
        if fp <= 0:
            continue

        for harmonic in range(1, max_pump_harmonic + 1):
            target = harmonic * fp
            if target < start or target > stop:
                continue

            grid_position = (target - start) / step
            nearest_index = round(grid_position)
            if nearest_index < 0 or nearest_index >= freq_range.points:
                continue

            grid_freq = start + nearest_index * step
            tolerance = max(abs(step) * 1e-6, abs(target) * 1e-12, 1e-12)
            if abs(grid_freq - target) <= tolerance:
                hits.append((source_index, harmonic, target, nearest_index))

    return hits


def _format_harmonic_grid_hint(hits: list[tuple[int, int, float, int]], limit: int = 3) -> str:
    """Build a concise user-facing hint for harmonic/grid coincidence hits."""
    if not hits:
        return ""

    shown = hits[:limit]
    parts = [
        (f"S{source_index}: {harmonic}*fp={freq_ghz:.6f} GHz (sweep index={grid_index})")
        for source_index, harmonic, freq_ghz, grid_index in shown
    ]
    suffix = "" if len(hits) <= limit else f"; +{len(hits) - limit} more"
    return (
        "Potential harmonic/grid coincidence detected (can trigger singular matrix): "
        + "; ".join(parts)
        + suffix
    )


def _estimate_mode_lattice_size(
    sources: list[DriveSourceConfig],
    n_modulation_harmonics: int,
) -> int:
    """Estimate the size of the mode lattice implied by the current source configuration."""
    if n_modulation_harmonics < 0:
        return 1

    tone_count = (
        max(
            1,
            max(
                len(source.mode_components) if source.mode_components is not None else 1
                for source in sources
            ),
        )
        if sources
        else 1
    )
    span_per_tone = max(1, 2 * n_modulation_harmonics + 1)
    lattice_size = 1
    for _ in range(tone_count):
        lattice_size *= span_per_tone
    return lattice_size


def _format_mode_lattice_hint(
    sources: list[DriveSourceConfig],
    n_modulation_harmonics: int,
) -> str:
    """Build a concise warning for potentially slow multi-tone hbsolve runs."""
    tone_count = (
        max(
            1,
            max(
                len(source.mode_components) if source.mode_components is not None else 1
                for source in sources
            ),
        )
        if sources
        else 1
    )
    lattice_size = _estimate_mode_lattice_size(sources, n_modulation_harmonics)
    return (
        "Estimated mode lattice: "
        f"{lattice_size} sideband states "
        f"({tone_count} tone(s), Nmod={n_modulation_harmonics}). "
        "Multi-pump runs can take significantly longer."
    )


def _load_saved_setups_for_schema(schema_id: int) -> list[dict[str, Any]]:
    """Load saved simulation setups for one schema from user storage."""
    raw_store = _user_storage_get(_SIM_SETUP_STORAGE_KEY, {})
    if not isinstance(raw_store, dict):
        return []

    setups = raw_store.get(str(schema_id), [])
    if not isinstance(setups, list):
        return []
    return [s for s in setups if isinstance(s, dict)]


def _save_saved_setups_for_schema(schema_id: int, setups: list[dict[str, Any]]) -> None:
    """Persist saved simulation setups for one schema into user storage."""
    raw_store = _user_storage_get(_SIM_SETUP_STORAGE_KEY, {})
    store_dict = dict(raw_store) if isinstance(raw_store, dict) else {}
    store_dict[str(schema_id)] = setups
    _user_storage_set(_SIM_SETUP_STORAGE_KEY, store_dict)


def _load_selected_setup_id(schema_id: int) -> str:
    """Load currently selected setup id for one schema from user storage."""
    raw_map = _user_storage_get(_SIM_SETUP_SELECTED_KEY, {})
    if not isinstance(raw_map, dict):
        return ""

    selected = raw_map.get(str(schema_id), "")
    return selected if isinstance(selected, str) else ""


def _save_selected_setup_id(schema_id: int, setup_id: str) -> None:
    """Persist selected setup id for one schema into user storage."""
    raw_map = _user_storage_get(_SIM_SETUP_SELECTED_KEY, {})
    selected_map = dict(raw_map) if isinstance(raw_map, dict) else {}
    selected_map[str(schema_id)] = setup_id
    _user_storage_set(_SIM_SETUP_SELECTED_KEY, selected_map)


def _load_saved_post_process_setups_for_schema(schema_id: int) -> list[dict[str, Any]]:
    """Load saved post-processing setups for one schema from user storage."""
    raw_store = _user_storage_get(_POST_PROCESS_SETUP_STORAGE_KEY, {})
    if not isinstance(raw_store, dict):
        return []

    setups = raw_store.get(str(schema_id), [])
    if not isinstance(setups, list):
        return []
    return [s for s in setups if isinstance(s, dict)]


def _save_saved_post_process_setups_for_schema(
    schema_id: int,
    setups: list[dict[str, Any]],
) -> None:
    """Persist saved post-processing setups for one schema into user storage."""
    raw_store = _user_storage_get(_POST_PROCESS_SETUP_STORAGE_KEY, {})
    store_dict = dict(raw_store) if isinstance(raw_store, dict) else {}
    store_dict[str(schema_id)] = setups
    _user_storage_set(_POST_PROCESS_SETUP_STORAGE_KEY, store_dict)


def _load_selected_post_process_setup_id(schema_id: int) -> str:
    """Load currently selected post-processing setup id for one schema."""
    raw_map = _user_storage_get(_POST_PROCESS_SELECTED_KEY, {})
    if not isinstance(raw_map, dict):
        return ""

    selected = raw_map.get(str(schema_id), "")
    return selected if isinstance(selected, str) else ""


def _save_selected_post_process_setup_id(schema_id: int, setup_id: str) -> None:
    """Persist selected post-processing setup id for one schema into user storage."""
    raw_map = _user_storage_get(_POST_PROCESS_SELECTED_KEY, {})
    selected_map = dict(raw_map) if isinstance(raw_map, dict) else {}
    selected_map[str(schema_id)] = setup_id
    _user_storage_set(_POST_PROCESS_SELECTED_KEY, selected_map)


@ui.page("/simulation")
def simulation_page():
    def content():
        ui.label("Circuit Simulation").classes("text-2xl font-bold text-fg mb-6")
        _render_simulation_environment()

    app_shell(content)()


def _render_simulation_environment():
    """Render the Simulation Execution environment."""

    @ui.refreshable
    def sim_env():
        try:
            with get_unit_of_work() as uow:
                circuits = uow.circuits.list_all()
        except Exception:
            circuits = []

        if not circuits:
            with ui.column().classes(
                "w-full p-12 items-center justify-center "
                "border-2 border-dashed border-border rounded-xl"
            ):
                ui.icon("warning", size="xl").classes("text-warning mb-4")
                ui.label("No Schemas Available").classes("text-xl text-fg font-bold")
                ui.label("Please create a circuit schema in the Schema Manager first.").classes(
                    "text-sm text-muted mt-2"
                )
                ui.button("Go to Schemas", on_click=lambda: ui.navigate.to("/schemas")).props(
                    "outline color=primary mt-4"
                )
            return

        circuit_options = {c.id: c.name for c in circuits}

        # Load from storage or default to first
        active_circuit_id = _user_storage_get("simulation_active_circuit")
        if active_circuit_id not in circuit_options:
            active_circuit_id = circuits[0].id
            _user_storage_set("simulation_active_circuit", active_circuit_id)

        # --- Top Selector ---
        with ui.row().classes("w-full items-center gap-4 mb-4 bg-surface p-4 rounded-xl"):
            ui.label("Active Schema:").classes("text-sm font-bold text-fg")

            def on_circuit_change(e: Any) -> None:
                _user_storage_set("simulation_active_circuit", e.value)
                sim_env.refresh()

            ui.select(
                options=circuit_options, value=active_circuit_id, on_change=on_circuit_change
            ).props("dense outlined options-dense").classes("w-64")

        try:
            with get_unit_of_work() as uow:
                editable_datasets = uow.datasets.list_all()
        except Exception:
            editable_datasets = []

        metadata_dataset_options = {
            int(dataset.id): str(dataset.name)
            for dataset in editable_datasets
            if dataset.id is not None
        }
        metadata_target_dataset_id = _user_storage_get(_SIM_METADATA_TARGET_DATASET_KEY)
        if metadata_target_dataset_id not in metadata_dataset_options:
            metadata_target_dataset_id = next(iter(metadata_dataset_options), None)
            _user_storage_set(_SIM_METADATA_TARGET_DATASET_KEY, metadata_target_dataset_id)
        metadata_target_dataset = next(
            (dataset for dataset in editable_datasets if dataset.id == metadata_target_dataset_id),
            None,
        )
        metadata_profile = normalize_dataset_profile(
            metadata_target_dataset.source_meta if metadata_target_dataset is not None else {}
        )

        with ui.card().classes("w-full bg-surface rounded-xl p-6"):
            with ui.row().classes("items-center gap-2 mb-3"):
                ui.icon("inventory_2", size="sm").classes("text-primary")
                ui.label("Dataset Metadata Summary").classes("text-lg font-bold text-fg")
            ui.label("Read-only profile summary used by Characterization hints.").classes(
                "text-sm text-muted mb-3"
            )

            if not metadata_dataset_options:
                ui.label("No datasets available for metadata summary.").classes(
                    "text-sm text-muted"
                )
            else:

                def _on_target_dataset_change(event: Any) -> None:
                    selected = event.value
                    dataset_id = int(selected) if isinstance(selected, int) else None
                    _user_storage_set(_SIM_METADATA_TARGET_DATASET_KEY, dataset_id)
                    sim_env.refresh()

                ui.select(
                    options=metadata_dataset_options,
                    value=metadata_target_dataset_id,
                    label="Target Dataset",
                    on_change=_on_target_dataset_change,
                ).props("dense outlined options-dense").classes("w-80 mb-2")

                ui.label(
                    profile_summary_text(
                        {
                            "device_type": metadata_profile["device_type"],
                            "capabilities": metadata_profile["capabilities"],
                            "source": metadata_profile["source"],
                        }
                    )
                ).classes("text-xs text-muted mb-2")

                with ui.row().classes("w-full items-center justify-between gap-3 flex-wrap"):
                    ui.label(
                        "Metadata editing is centralized in Pipeline Dashboard."
                    ).classes("text-xs text-muted")
                    ui.button(
                        "Edit in Dashboard",
                        icon="dashboard",
                        on_click=lambda: ui.navigate.to("/dashboard"),
                    ).props("outline color=primary no-caps")

        # Get active record
        active_record = next((c for c in circuits if c.id == active_circuit_id), circuits[0])
        active_record_id = active_record.id
        if active_record_id is None:
            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                ui.label("Selected schema is missing a persistent id.").classes("text-danger")
            return
        try:
            active_record, active_circuit_def = _load_latest_circuit_definition(active_record_id)
        except Exception as e:
            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                ui.label(f"Error parsing selected schema: {e}").classes("text-danger")
            return
        active_record_id = active_record.id
        if active_record_id is None:
            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                ui.label("Selected schema is missing a persistent id.").classes("text-danger")
            return
        displayed_netlist = format_expanded_circuit_definition(active_circuit_def)
        latest_circuit_definition_ref: dict[str, CircuitDefinition] = {
            "definition": active_circuit_def
        }

        status_history: list[dict[str, str]] = []
        status_container: Any | None = None
        simulation_results_container: Any | None = None
        post_processing_container: Any | None = None
        post_processing_results_container: Any | None = None
        latest_pipeline_result: dict[str, Any] = {
            "sweep": None,
            "flow_spec": None,
            "circuit_record": None,
            "source_simulation_bundle_id": None,
            "schema_source_hash": None,
            "simulation_setup_hash": None,
        }
        latest_simulation_result: dict[str, SimulationResult | None] = {"result": None}
        latest_raw_save_action: dict[str, Callable[[], None] | None] = {"callback": None}
        raw_view_state: dict[str, Any] = {
            "family": "s",
            "metric": "magnitude_linear",
            "z0": 50.0,
            "traces": [],
        }
        post_view_state: dict[str, Any] = {
            "family": "s",
            "metric": "magnitude_linear",
            "z0": 50.0,
            "traces": [],
        }
        available_setup_ports = sorted(active_circuit_def.available_port_indices)
        termination_inferred_resistance_ohm_by_port: dict[int, float] = {
            port: _TERMINATION_DEFAULT_RESISTANCE_OHM for port in available_setup_ports
        }
        termination_inferred_source_by_port: dict[int, str] = {
            port: "fallback_default_50" for port in available_setup_ports
        }
        termination_inferred_warning_by_port: dict[int, str] = {
            port: (
                f"Port {port}: fallback to {_TERMINATION_DEFAULT_RESISTANCE_OHM:g} Ohm "
                "because schema inference is unavailable."
            )
            for port in available_setup_ports
        }
        try:
            termination_inference = infer_port_termination_resistance_ohm(active_circuit_def)
            termination_inferred_resistance_ohm_by_port = dict(
                termination_inference.resistance_ohm_by_port
            )
            termination_inferred_source_by_port = dict(termination_inference.source_by_port)
            termination_inferred_warning_by_port = dict(termination_inference.warning_by_port)
        except Exception as inference_exc:
            for port in available_setup_ports:
                termination_inferred_warning_by_port[port] = (
                    f"Port {port}: schema inference failed ({inference_exc}); "
                    f"fallback to {_TERMINATION_DEFAULT_RESISTANCE_OHM:g} Ohm."
                )

        termination_state: dict[str, Any] = {
            "enabled": False,
            "mode": "auto",
            "selected_ports": list(available_setup_ports),
            "manual_resistance_ohm_by_port": {
                int(port): _TERMINATION_DEFAULT_RESISTANCE_OHM for port in available_setup_ports
            },
        }
        termination_view_elements: dict[str, Any] = {
            "enabled_switch": None,
            "mode_select": None,
            "ports_select": None,
            "reset_button": None,
            "summary_label": None,
            "details_container": None,
        }
        termination_last_warning: dict[str, str] = {"message": ""}
        termination_last_summary: dict[str, str] = {"message": ""}

        def append_status(level: str, message: str) -> None:
            status_history.append(
                {
                    "level": level,
                    "message": message,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
            )
            if len(status_history) > 30:
                status_history.pop(0)
            render_status()

        def reset_status(message: str | None = None) -> None:
            status_history.clear()
            if message:
                append_status("info", message)
            else:
                render_status()

        def render_status() -> None:
            if status_container is None:
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

            status_container.clear()
            with status_container:
                if not status_history:
                    ui.label("No logs yet. Run a simulation to see process messages.").classes(
                        "text-sm text-muted"
                    )
                    return

                for item in status_history:
                    with ui.row().classes("w-full items-start gap-2"):
                        ui.icon(icon_map.get(item["level"], "info"), size="xs").classes(
                            color_map.get(item["level"], "text-primary mt-1")
                        )
                        ui.label(f"[{item['time']}] {item['message']}").classes(
                            "text-sm text-fg whitespace-pre-wrap break-all"
                        )

        def _reset_result_view_state(
            view_state: dict[str, Any],
            family_options: dict[str, str],
        ) -> None:
            fallback_family = next(iter(family_options), "s")
            selected_family = str(view_state.get("family", fallback_family))
            if selected_family not in family_options:
                selected_family = fallback_family
            metric_options = _result_metric_options_for_family(selected_family)
            view_state["family"] = selected_family
            view_state["metric"] = (
                _first_option_key(metric_options) if metric_options else "magnitude_linear"
            )
            view_state["traces"] = []

        def _resolved_termination_plan() -> dict[str, Any]:
            return _build_termination_compensation_plan(
                enabled=bool(termination_state.get("enabled", False)),
                mode=_normalize_termination_mode(termination_state.get("mode", "auto")),
                selected_ports=_normalize_termination_selected_ports(
                    termination_state.get("selected_ports", []),
                    available_ports=available_setup_ports,
                ),
                manual_resistance_ohm_by_port=_normalize_manual_termination_resistance_map(
                    termination_state.get("manual_resistance_ohm_by_port", {}),
                    available_ports=available_setup_ports,
                    default_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
                ),
                inferred_resistance_ohm_by_port=termination_inferred_resistance_ohm_by_port,
                inferred_source_by_port=termination_inferred_source_by_port,
                inferred_warning_by_port=termination_inferred_warning_by_port,
                fallback_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
            )

        def _termination_plan_summary(plan: dict[str, Any]) -> str:
            if not bool(plan.get("enabled", False)):
                return "Termination compensation: disabled."
            selected_ports = [int(port) for port in plan.get("selected_ports", [])]
            resistance_map = dict(plan.get("resistance_ohm_by_port", {}))
            source_map = dict(plan.get("source_by_port", {}))
            details = []
            for port in selected_ports:
                resistance = float(resistance_map.get(port, _TERMINATION_DEFAULT_RESISTANCE_OHM))
                source = str(source_map.get(port, "manual"))
                details.append(f"p{port}={resistance:g} Ohm ({source})")
            mode = str(plan.get("mode", "auto"))
            return (
                "Termination compensation: "
                f"enabled, mode={mode}, ports={selected_ports or []}, values={'; '.join(details)}."
            )

        def _effective_simulation_result(
            *,
            reference_impedance_ohm: float,
        ) -> SimulationResult | None:
            result = latest_simulation_result.get("result")
            if not isinstance(result, SimulationResult):
                return None
            plan = _resolved_termination_plan()
            if not bool(plan.get("enabled", False)):
                return result
            try:
                return compensate_simulation_result_port_terminations(
                    result,
                    resistance_ohm_by_port=dict(plan.get("resistance_ohm_by_port", {})),
                    reference_impedance_ohm=reference_impedance_ohm,
                )
            except Exception as exc:
                message = f"Termination compensation skipped: {exc}"
                if termination_last_warning["message"] != message:
                    termination_last_warning["message"] = message
                    append_status("warning", message)
                return result

        def _render_post_processing_input_panel() -> None:
            if post_processing_container is None:
                return
            post_processing_container.clear()
            result_for_post_processing = _effective_simulation_result(
                reference_impedance_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
            )
            if not isinstance(result_for_post_processing, SimulationResult):
                with post_processing_container:
                    ui.label(
                        "Run a simulation first, then apply port-level coordinate transforms "
                        "and Kron reduction here."
                    ).classes("text-sm text-muted")
                return

            with post_processing_container:
                _render_post_processing_panel(
                    result=result_for_post_processing,
                    circuit_definition=latest_circuit_definition_ref["definition"],
                    schema_id=active_record_id,
                    schema_name=active_record.name,
                    append_status=append_status,
                    on_result=handle_post_processing_result,
                )

        def _raw_result_provider(
            _reference_impedance: float,
        ) -> tuple[SimulationResult, dict[int, str]] | None:
            result = _effective_simulation_result(
                reference_impedance_ohm=float(_reference_impedance),
            )
            if not isinstance(result, SimulationResult):
                return None
            return (result, _result_port_options(result))

        def _post_processed_result_provider(
            reference_impedance: float,
        ) -> tuple[SimulationResult, dict[int, str]] | None:
            sweep = latest_pipeline_result.get("sweep")
            if not isinstance(sweep, PortMatrixSweep):
                return None
            return _build_post_processed_result_payload(
                sweep,
                reference_impedance_ohm=reference_impedance,
            )

        def render_simulation_result_view() -> None:
            if simulation_results_container is None:
                return

            raw_save_callback = latest_raw_save_action["callback"]
            _render_result_family_explorer(
                container=simulation_results_container,
                view_state=raw_view_state,
                family_options=_RESULT_FAMILY_OPTIONS,
                result_provider=_raw_result_provider,
                header_message="Raw quick-inspect view from latest simulation run.",
                empty_message="Run simulation to inspect raw result traces.",
                save_button_label="Save Raw Simulation Results" if raw_save_callback else None,
                on_save_click=raw_save_callback,
                save_enabled=raw_save_callback is not None,
            )

        def _save_post_processed_results_from_view() -> None:
            sweep = latest_pipeline_result.get("sweep")
            flow_spec = latest_pipeline_result.get("flow_spec")
            if not _can_save_post_processed_results(sweep, flow_spec):
                ui.notify("Run Post Processing first.", type="warning")
                return
            _save_post_processed_results_dialog(
                sweep=sweep,
                flow_spec=dict(flow_spec),
                circuit_record=latest_pipeline_result.get("circuit_record"),
                source_simulation_bundle_id=latest_pipeline_result.get(
                    "source_simulation_bundle_id"
                ),
                schema_source_hash=latest_pipeline_result.get("schema_source_hash"),
                simulation_setup_hash=latest_pipeline_result.get("simulation_setup_hash"),
            )

        def render_post_processed_result_view() -> None:
            if post_processing_results_container is None:
                return

            sweep = latest_pipeline_result.get("sweep")
            flow_spec = latest_pipeline_result.get("flow_spec")
            save_enabled = _can_save_post_processed_results(sweep, flow_spec)
            context_line = None
            if save_enabled:
                typed_sweep = sweep
                typed_flow_spec = flow_spec
                if not isinstance(typed_sweep, PortMatrixSweep) or not isinstance(
                    typed_flow_spec, dict
                ):
                    typed_sweep = None
                    typed_flow_spec = None
                if isinstance(typed_sweep, PortMatrixSweep) and isinstance(typed_flow_spec, dict):
                    step_count = len(typed_flow_spec.get("steps", []))
                    context_line = (
                        f"Pipeline steps applied: {step_count} | "
                        f"mode={SimulationResult.mode_token(typed_sweep.mode)} | "
                        f"basis={', '.join(typed_sweep.labels)}"
                    )
            _render_result_family_explorer(
                container=post_processing_results_container,
                view_state=post_view_state,
                family_options=_POST_PROCESSED_RESULT_FAMILY_OPTIONS,
                result_provider=_post_processed_result_provider,
                header_message=(
                    "Result View consumes the latest Post Processing pipeline output node."
                ),
                empty_message="Run Post Processing to generate the pipeline output node.",
                save_button_label="Save Post-Processed Results",
                on_save_click=_save_post_processed_results_from_view,
                save_enabled=save_enabled,
                context_line=context_line,
            )

        def handle_post_processing_result(
            sweep: PortMatrixSweep | None,
            flow_spec: dict[str, Any] | None,
        ) -> None:
            latest_pipeline_result["sweep"] = sweep
            latest_pipeline_result["flow_spec"] = flow_spec
            _reset_result_view_state(post_view_state, _POST_PROCESSED_RESULT_FAMILY_OPTIONS)
            render_post_processed_result_view()

        # --- Single-column full-width flow ---
        with ui.column().classes("w-full gap-6"):
            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                with ui.row().classes("items-center gap-2 mb-4"):
                    ui.icon("description", size="sm").classes("text-primary")
                    ui.label("Netlist Configuration").classes("text-lg font-bold text-fg")
                ui.label(
                    "This is the expanded netlist that will actually be sent to the simulator. "
                    "It uses the same repeat-expansion pipeline as the Schema Editor preview."
                ).classes("text-sm text-muted mb-3")
                with ui.element("div").classes(
                    "w-full max-h-[480px] overflow-auto rounded-lg border border-border bg-bg p-3"
                ):
                    ui.markdown(f"```python\n{displayed_netlist}\n```").classes("w-full")

            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                had_selected_setup_entry = _has_selected_setup_entry(active_record_id)
                saved_setups = _ensure_builtin_saved_setups(active_record_id, active_record.name)
                saved_setup_by_id = {
                    str(setup.get("id")): setup
                    for setup in saved_setups
                    if setup.get("id") and setup.get("name")
                }
                saved_setup_options = {"": "Current (Unsaved)"}
                saved_setup_options.update(
                    {
                        setup_id: str(setup.get("name"))
                        for setup_id, setup in saved_setup_by_id.items()
                    }
                )
                selected_setup_id = _load_selected_setup_id(active_record_id)
                builtin_setup_ids = [
                    str(setup.get("id"))
                    for setup in saved_setups
                    if str(setup.get("saved_at")) == "builtin" and setup.get("id")
                ]
                default_builtin_setup_id = builtin_setup_ids[0] if builtin_setup_ids else ""
                if selected_setup_id not in saved_setup_options:
                    selected_setup_id = default_builtin_setup_id or ""
                elif not had_selected_setup_entry and default_builtin_setup_id:
                    selected_setup_id = default_builtin_setup_id
                _save_selected_setup_id(active_record_id, selected_setup_id)

                with ui.row().classes("w-full items-center justify-between mb-4"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("settings", size="sm").classes("text-primary")
                        ui.label("Simulation Setup").classes("text-lg font-bold text-fg")
                    with ui.row().classes("items-center gap-2"):
                        saved_setup_select: Any = (
                            ui.select(
                                label="Saved Setup",
                                options=saved_setup_options,
                                value=selected_setup_id,
                            )
                            .props("dense outlined options-dense")
                            .classes("w-60")
                        )
                        save_setup_button = ui.button("Save", icon="save").props(
                            "outline color=primary size=sm"
                        )

                with ui.row().classes("w-full gap-4"):
                    start_input = ui.number("Start Freq (GHz)", value=1.0).classes("flex-grow")
                    stop_input = ui.number("Stop Freq (GHz)", value=10.0).classes("flex-grow")
                    points_input = ui.number("Points", value=1001, format="%.0f").classes(
                        "flex-grow"
                    )

                ui.separator().classes("my-3 w-full")

                ui.label("HB Solve Pump/Source Settings").classes("text-sm text-muted mb-2")
                with ui.row().classes("w-full gap-4"):
                    n_mod_input = ui.number(
                        "Nmodulation Harmonics",
                        value=10,
                        format="%.0f",
                    ).classes("flex-grow")
                    n_pump_input = ui.number(
                        "Npump Harmonics",
                        value=20,
                        format="%.0f",
                    ).classes("flex-grow")

                source_forms: list[dict[str, Any]] = []
                sources_container = ui.column().classes("w-full gap-3 mt-2")
                applying_saved_setup = False

                def normalize_source_mode_inputs() -> None:
                    for source_form in source_forms:
                        mode_input = source_form["mode_input"]
                        try:
                            parsed_mode = _parse_source_mode_text(mode_input.value)
                        except ValueError:
                            continue
                        normalized_text = _format_source_mode_text(parsed_mode)
                        if mode_input.value != normalized_text:
                            mode_input.value = normalized_text

                def refresh_source_forms() -> None:
                    has_multiple_sources = len(source_forms) > 1
                    for idx, source_form in enumerate(source_forms, start=1):
                        title = source_form["title"]
                        remove_button = source_form["remove_button"]
                        title.text = f"Source {idx}"
                        remove_button.enabled = has_multiple_sources
                    normalize_source_mode_inputs()

                def remove_source_form(source_card: Any) -> None:
                    if len(source_forms) <= 1:
                        ui.notify("At least one source is required.", type="warning")
                        return

                    for idx, source_form in enumerate(source_forms):
                        card = source_form["card"]
                        if card is source_card:
                            source_forms.pop(idx)
                            card.delete()
                            refresh_source_forms()
                            return

                def add_source_form(initial: DriveSourceConfig | None = None) -> None:
                    if initial is None:
                        next_index = len(source_forms)
                        fallback_mode = [0] * (next_index + 1)
                        fallback_mode[next_index] = 1
                        source_defaults = DriveSourceConfig(mode_components=tuple(fallback_mode))
                    else:
                        source_defaults = initial
                    with (
                        sources_container,
                        ui.card().classes(
                            "w-full bg-elevated border border-border rounded-lg p-4"
                        ) as source_card,
                    ):
                        with ui.row().classes("w-full items-center justify-between mb-2"):
                            title_label = ui.label("").classes("text-sm font-bold text-fg")
                            remove_button = ui.button(
                                icon="delete",
                                on_click=lambda card=source_card: remove_source_form(card),
                            ).props("flat dense round color=negative")

                        with ui.row().classes("w-full gap-4"):
                            source_pump_freq_input = ui.number(
                                "Pump Freq (GHz)",
                                value=float(source_defaults.pump_freq_ghz),
                            ).classes("flex-grow")
                            port_input = ui.number(
                                "Source Port",
                                value=int(source_defaults.port),
                                format="%.0f",
                            ).classes("flex-grow")
                            current_input = ui.number(
                                "Source Current Ip (A)",
                                value=float(source_defaults.current_amp),
                            ).classes("flex-grow")
                            mode_input = ui.input(
                                "Source Mode",
                                value=_format_source_mode_text(source_defaults.mode_components),
                                placeholder="e.g. 1 or 0, 1",
                            ).classes("flex-grow")

                    source_forms.append(
                        {
                            "card": source_card,
                            "title": title_label,
                            "remove_button": remove_button,
                            "source_pump_freq_input": source_pump_freq_input,
                            "port_input": port_input,
                            "current_input": current_input,
                            "mode_input": mode_input,
                        }
                    )
                    refresh_source_forms()

                with ui.row().classes("w-full items-center justify-between mt-3"):
                    ui.label("Sources").classes("text-sm font-bold text-fg")
                    ui.button("Add Source", icon="add", on_click=add_source_form).props(
                        "outline color=primary size=sm"
                    )

                add_source_form(
                    DriveSourceConfig(
                        pump_freq_ghz=5.0,
                        port=1,
                        current_amp=0.0,
                        mode_components=(1,),
                    )
                )

                termination_state["selected_ports"] = list(available_setup_ports)
                termination_state["manual_resistance_ohm_by_port"] = {
                    int(port): _TERMINATION_DEFAULT_RESISTANCE_OHM for port in available_setup_ports
                }

                with ui.card().classes(
                    "w-full bg-elevated border border-border rounded-lg p-4 mt-4"
                ):
                    ui.label("Port Termination Compensation (Optional)").classes(
                        "text-sm font-bold text-fg mb-2"
                    )
                    with ui.row().classes("w-full items-end gap-3 flex-wrap"):
                        termination_enabled_switch = ui.switch(
                            "Enable",
                            value=bool(termination_state["enabled"]),
                        )
                        termination_mode_select = (
                            ui.select(
                                label="Mode",
                                options=_TERMINATION_MODE_OPTIONS,
                                value=str(termination_state["mode"]),
                            )
                            .props("dense outlined options-dense")
                            .classes("w-56")
                        )
                        termination_ports_select = (
                            ui.select(
                                label="Compensate Ports",
                                options={port: str(port) for port in available_setup_ports},
                                value=list(termination_state["selected_ports"]),
                                multiple=True,
                            )
                            .props("dense outlined options-dense use-chips")
                            .classes("w-64")
                        )
                        termination_reset_button = (
                            ui.button(
                                "Reset Manual to 50 Ohm",
                                icon="restart_alt",
                            )
                            .props("outline color=primary size=sm")
                            .classes("shrink-0")
                        )
                    termination_summary_label = ui.label("").classes("text-xs text-muted mt-2")
                    termination_details_container = ui.column().classes("w-full gap-1 mt-2")

                termination_view_elements["enabled_switch"] = termination_enabled_switch
                termination_view_elements["mode_select"] = termination_mode_select
                termination_view_elements["ports_select"] = termination_ports_select
                termination_view_elements["reset_button"] = termination_reset_button
                termination_view_elements["summary_label"] = termination_summary_label
                termination_view_elements["details_container"] = termination_details_container

                def refresh_termination_controls() -> None:
                    enabled_switch = termination_view_elements.get("enabled_switch")
                    mode_select = termination_view_elements.get("mode_select")
                    ports_select = termination_view_elements.get("ports_select")
                    reset_button = termination_view_elements.get("reset_button")
                    summary_label = termination_view_elements.get("summary_label")
                    details_container = termination_view_elements.get("details_container")
                    if (
                        enabled_switch is None
                        or mode_select is None
                        or ports_select is None
                        or reset_button is None
                        or summary_label is None
                        or details_container is None
                    ):
                        return

                    normalized_mode = _normalize_termination_mode(mode_select.value)
                    mode_select.value = normalized_mode
                    selected_ports = _normalize_termination_selected_ports(
                        ports_select.value,
                        available_ports=available_setup_ports,
                    )
                    if enabled_switch.value and not selected_ports and available_setup_ports:
                        selected_ports = [available_setup_ports[0]]
                    ports_select.value = selected_ports

                    normalized_manual_map = _normalize_manual_termination_resistance_map(
                        termination_state.get("manual_resistance_ohm_by_port", {}),
                        available_ports=available_setup_ports,
                        default_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
                    )
                    termination_state["enabled"] = bool(enabled_switch.value)
                    termination_state["mode"] = normalized_mode
                    termination_state["selected_ports"] = list(selected_ports)
                    termination_state["manual_resistance_ohm_by_port"] = normalized_manual_map

                    resolved_plan = _resolved_termination_plan()
                    summary_label.text = _termination_plan_summary(resolved_plan)
                    if normalized_mode == "manual":
                        reset_button.enable()
                    else:
                        reset_button.disable()

                    details_container.clear()
                    with details_container:
                        if not bool(resolved_plan.get("enabled", False)):
                            ui.label("Disabled: raw solver output is used directly.").classes(
                                "text-xs text-muted"
                            )
                            return

                        selected = [int(port) for port in resolved_plan.get("selected_ports", [])]
                        resolved_values = dict(resolved_plan.get("resistance_ohm_by_port", {}))
                        source_values = dict(resolved_plan.get("source_by_port", {}))
                        for port in selected:
                            source = str(source_values.get(port, "manual"))
                            resistance = float(
                                resolved_values.get(port, _TERMINATION_DEFAULT_RESISTANCE_OHM)
                            )
                            if normalized_mode == "manual":
                                row_label = f"Port {port} · Manual R (Ohm)"
                                manual_input = (
                                    ui.number(
                                        row_label,
                                        value=float(
                                            normalized_manual_map.get(
                                                port,
                                                _TERMINATION_DEFAULT_RESISTANCE_OHM,
                                            )
                                        ),
                                        format="%.6g",
                                    )
                                    .props("dense outlined")
                                    .classes("w-56")
                                )

                                def _on_manual_change(
                                    e: Any,
                                    *,
                                    target_port: int,
                                ) -> None:
                                    manual_map = dict(
                                        termination_state.get(
                                            "manual_resistance_ohm_by_port",
                                            {},
                                        )
                                    )
                                    try:
                                        value = float(e.value)
                                    except Exception:
                                        value = _TERMINATION_DEFAULT_RESISTANCE_OHM
                                    manual_map[target_port] = value
                                    termination_state["manual_resistance_ohm_by_port"] = manual_map
                                    if not applying_saved_setup:
                                        on_termination_setup_change()
                                    else:
                                        refresh_termination_controls()

                                manual_input.on_value_change(
                                    lambda e, target_port=port: _on_manual_change(
                                        e,
                                        target_port=target_port,
                                    )
                                )
                                ui.label(f"Resolved: {resistance:g} Ohm ({source})").classes(
                                    "text-xs text-muted"
                                )
                            else:
                                ui.label(f"Port {port}: {resistance:g} Ohm ({source})").classes(
                                    "text-xs text-fg"
                                )

                        for warning in list(resolved_plan.get("warnings", [])):
                            ui.label(str(warning)).classes("text-xs text-warning")

                def on_termination_setup_change() -> None:
                    refresh_termination_controls()
                    if applying_saved_setup:
                        return
                    if not isinstance(latest_simulation_result.get("result"), SimulationResult):
                        return
                    handle_post_processing_result(None, None)
                    render_simulation_result_view()
                    _render_post_processing_input_panel()
                    render_post_processed_result_view()
                    summary_text = _termination_plan_summary(_resolved_termination_plan())
                    if termination_last_summary["message"] != summary_text:
                        termination_last_summary["message"] = summary_text
                        append_status(
                            "info",
                            (
                                "Termination compensation updated without Julia rerun. "
                                f"{summary_text}"
                            ),
                        )

                termination_enabled_switch.on_value_change(lambda _e: on_termination_setup_change())
                termination_mode_select.on_value_change(lambda _e: on_termination_setup_change())
                termination_ports_select.on_value_change(lambda _e: on_termination_setup_change())

                def on_reset_termination_manual_defaults() -> None:
                    manual_map = _normalize_manual_termination_resistance_map(
                        termination_state.get("manual_resistance_ohm_by_port", {}),
                        available_ports=available_setup_ports,
                        default_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
                    )
                    selected_ports = _normalize_termination_selected_ports(
                        termination_state.get("selected_ports", []),
                        available_ports=available_setup_ports,
                    )
                    for port in selected_ports:
                        manual_map[port] = _TERMINATION_DEFAULT_RESISTANCE_OHM
                    termination_state["manual_resistance_ohm_by_port"] = manual_map
                    on_termination_setup_change()

                termination_reset_button.on_click(lambda _e: on_reset_termination_manual_defaults())
                refresh_termination_controls()

                def collect_current_setup_payload() -> dict[str, Any] | None:
                    required_values = [
                        start_input.value,
                        stop_input.value,
                        points_input.value,
                        n_mod_input.value,
                        n_pump_input.value,
                    ]
                    if any(value is None for value in required_values):
                        ui.notify("Please fill all simulation parameters first.", type="warning")
                        return None

                    setup_sources: list[dict[str, float | int]] = []
                    for idx, source_form in enumerate(source_forms, start=1):
                        source_pump_freq_input = source_form["source_pump_freq_input"]
                        port_input = source_form["port_input"]
                        current_input = source_form["current_input"]
                        mode_input = source_form["mode_input"]

                        if (
                            source_pump_freq_input.value is None
                            or port_input.value is None
                            or current_input.value is None
                        ):
                            ui.notify(f"Source {idx} has missing parameters.", type="warning")
                            return None

                        try:
                            parsed_mode = _parse_source_mode_text(mode_input.value)
                        except ValueError:
                            ui.notify(
                                (
                                    f"Source {idx} has an invalid mode tuple. "
                                    "Use comma-separated integers, for example 0 or 1, 0."
                                ),
                                type="warning",
                            )
                            return None

                        normalized_mode = _normalize_source_mode_components(
                            parsed_mode,
                            source_index=idx - 1,
                            source_count=len(source_forms),
                        )
                        persisted_mode = (
                            _compress_source_mode_components(parsed_mode)
                            if parsed_mode is not None
                            else _compress_source_mode_components(normalized_mode)
                        )

                        setup_sources.append(
                            _build_source_payload(
                                pump_freq_ghz=float(source_pump_freq_input.value),
                                port=int(port_input.value),
                                current_amp=float(current_input.value),
                                mode=persisted_mode,
                            )
                        )

                    return {
                        "freq_range": {
                            "start_ghz": float(start_input.value),
                            "stop_ghz": float(stop_input.value),
                            "points": int(points_input.value),
                        },
                        "harmonics": {
                            "n_modulation_harmonics": int(n_mod_input.value),
                            "n_pump_harmonics": int(n_pump_input.value),
                        },
                        "sources": setup_sources,
                        "advanced": {
                            "include_dc": bool(include_dc_switch.value),
                            "enable_three_wave_mixing": bool(three_wave_switch.value),
                            "enable_four_wave_mixing": bool(four_wave_switch.value),
                            "max_intermod_order": int(max_intermod_input.value),
                            "max_iterations": int(max_iterations_input.value),
                            "f_tol": float(ftol_input.value),
                            "line_search_switch_tol": float(linesearch_tol_input.value),
                            "alpha_min": float(alpha_min_input.value),
                        },
                        "termination_compensation": {
                            "enabled": bool(termination_state.get("enabled", False)),
                            "mode": _normalize_termination_mode(
                                termination_state.get("mode", "auto")
                            ),
                            "selected_ports": _normalize_termination_selected_ports(
                                termination_state.get("selected_ports", []),
                                available_ports=available_setup_ports,
                            ),
                            "manual_resistance_ohm_by_port": {
                                str(port): float(value)
                                for port, value in _normalize_manual_termination_resistance_map(
                                    termination_state.get("manual_resistance_ohm_by_port", {}),
                                    available_ports=available_setup_ports,
                                    default_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
                                ).items()
                            },
                        },
                    }

                def apply_saved_setup(setup_record: dict[str, Any]) -> None:
                    nonlocal applying_saved_setup
                    payload = setup_record.get("payload")
                    if not isinstance(payload, dict):
                        ui.notify("Selected setup payload is invalid.", type="warning")
                        return

                    freq_payload = payload.get("freq_range", {})
                    harmonics_payload = payload.get("harmonics", {})
                    sources_payload = payload.get("sources", [])
                    advanced_payload = payload.get("advanced", {})
                    termination_payload = payload.get("termination_compensation", {})

                    applying_saved_setup = True
                    try:
                        start_input.value = float(freq_payload.get("start_ghz", 1.0))
                        stop_input.value = float(freq_payload.get("stop_ghz", 10.0))
                        points_input.value = int(freq_payload.get("points", 1001))
                        n_mod_input.value = int(harmonics_payload.get("n_modulation_harmonics", 10))
                        n_pump_input.value = int(harmonics_payload.get("n_pump_harmonics", 20))
                        include_dc_switch.value = bool(advanced_payload.get("include_dc", False))
                        three_wave_switch.value = bool(
                            advanced_payload.get("enable_three_wave_mixing", False)
                        )
                        four_wave_switch.value = bool(
                            advanced_payload.get("enable_four_wave_mixing", True)
                        )
                        max_intermod_input.value = int(
                            advanced_payload.get("max_intermod_order", -1)
                        )
                        max_iterations_input.value = int(
                            advanced_payload.get("max_iterations", 1000)
                        )
                        ftol_input.value = float(advanced_payload.get("f_tol", 1e-8))
                        linesearch_tol_input.value = float(
                            advanced_payload.get("line_search_switch_tol", 1e-5)
                        )
                        alpha_min_input.value = float(advanced_payload.get("alpha_min", 1e-4))
                        termination_enabled = bool(
                            termination_payload.get("enabled", False)
                            if isinstance(termination_payload, dict)
                            else False
                        )
                        termination_mode = _normalize_termination_mode(
                            termination_payload.get("mode", "auto")
                            if isinstance(termination_payload, dict)
                            else "auto"
                        )
                        termination_selected_ports = _normalize_termination_selected_ports(
                            termination_payload.get("selected_ports", available_setup_ports)
                            if isinstance(termination_payload, dict)
                            else available_setup_ports,
                            available_ports=available_setup_ports,
                        )
                        termination_manual_map = _normalize_manual_termination_resistance_map(
                            termination_payload.get("manual_resistance_ohm_by_port", {})
                            if isinstance(termination_payload, dict)
                            else {},
                            available_ports=available_setup_ports,
                            default_ohm=_TERMINATION_DEFAULT_RESISTANCE_OHM,
                        )
                        termination_state["enabled"] = termination_enabled
                        termination_state["mode"] = termination_mode
                        termination_state["selected_ports"] = list(termination_selected_ports)
                        termination_state["manual_resistance_ohm_by_port"] = termination_manual_map
                        if termination_view_elements.get("enabled_switch") is not None:
                            termination_view_elements["enabled_switch"].value = termination_enabled
                        if termination_view_elements.get("mode_select") is not None:
                            termination_view_elements["mode_select"].value = termination_mode
                        if termination_view_elements.get("ports_select") is not None:
                            termination_view_elements[
                                "ports_select"
                            ].value = termination_selected_ports
                        refresh_termination_controls()

                        for source_form in list(source_forms):
                            source_card = source_form["card"]
                            source_card.delete()
                        source_forms.clear()

                        valid_sources = [
                            source
                            for source in sources_payload
                            if isinstance(source, dict)
                            and source.get("pump_freq_ghz") is not None
                            and source.get("port") is not None
                            and source.get("current_amp") is not None
                        ]
                        if not valid_sources:
                            valid_sources = [{"pump_freq_ghz": 5.0, "port": 1, "current_amp": 0.0}]

                        generated_mode_width = max(len(valid_sources), 1)
                        for source_index, source in enumerate(valid_sources, start=1):
                            raw_mode = source.get("mode")
                            try:
                                parsed_mode = _parse_source_mode_text(raw_mode)
                            except ValueError:
                                parsed_mode = None
                            display_mode = (
                                parsed_mode
                                if parsed_mode is not None
                                else _normalize_source_mode_components(
                                    None,
                                    source_index=source_index - 1,
                                    source_count=generated_mode_width,
                                )
                            )
                            add_source_form(
                                DriveSourceConfig(
                                    pump_freq_ghz=float(source["pump_freq_ghz"]),
                                    port=int(source["port"]),
                                    current_amp=float(source["current_amp"]),
                                    mode_components=display_mode,
                                )
                            )
                    finally:
                        applying_saved_setup = False

                def refresh_saved_setup_select(preferred_id: str | None = None) -> None:
                    nonlocal saved_setups, saved_setup_by_id
                    saved_setups = _ensure_builtin_saved_setups(
                        active_record_id,
                        active_record.name,
                    )
                    saved_setup_by_id = {
                        str(setup.get("id")): setup
                        for setup in saved_setups
                        if setup.get("id") and setup.get("name")
                    }
                    options = {"": "Current (Unsaved)"}
                    options.update(
                        {
                            setup_id: str(setup.get("name"))
                            for setup_id, setup in saved_setup_by_id.items()
                        }
                    )
                    saved_setup_select.options = options

                    current = preferred_id if preferred_id in options else saved_setup_select.value
                    if current not in options:
                        current = ""
                    saved_setup_select.value = current
                    _save_selected_setup_id(active_record_id, str(current))
                    if current and current in saved_setup_by_id:
                        apply_saved_setup(saved_setup_by_id[current])

                def on_saved_setup_change(e: Any) -> None:
                    if applying_saved_setup:
                        return

                    setup_id = str(e.value or "")
                    _save_selected_setup_id(active_record_id, setup_id)
                    if not setup_id:
                        return

                    setup_record = saved_setup_by_id.get(setup_id)
                    if setup_record is None:
                        ui.notify("Saved setup not found.", type="warning")
                        return
                    apply_saved_setup(setup_record)
                    on_termination_setup_change()
                    ui.notify(f"Loaded setup: {setup_record.get('name')}", type="positive")

                saved_setup_select.on_value_change(on_saved_setup_change)

                def on_save_setup_click() -> None:
                    with ui.dialog() as dialog, ui.card().classes("w-full max-w-md bg-surface p-4"):
                        ui.label("Save Simulation Setup").classes("text-lg font-bold text-fg mb-3")
                        default_name = f"{active_record.name} Setup {len(saved_setups) + 1}"
                        name_input = ui.input("Setup Name", value=default_name).classes("w-full")

                        def do_save() -> None:
                            setup_name = str(name_input.value or "").strip()
                            if not setup_name:
                                ui.notify("Setup name is required.", type="warning")
                                return

                            payload = collect_current_setup_payload()
                            if payload is None:
                                return

                            existing = next(
                                (s for s in saved_setups if str(s.get("name")) == setup_name),
                                None,
                            )
                            setup_id = (
                                str(existing.get("id"))
                                if existing is not None and existing.get("id")
                                else datetime.now().strftime("%Y%m%d%H%M%S%f")
                            )

                            setup_record = {
                                "id": setup_id,
                                "name": setup_name,
                                "saved_at": datetime.now().isoformat(),
                                "payload": payload,
                            }
                            updated_setups = [
                                s for s in saved_setups if str(s.get("id")) != setup_id
                            ]
                            updated_setups.append(setup_record)
                            _save_saved_setups_for_schema(active_record_id, updated_setups)
                            refresh_saved_setup_select(preferred_id=setup_id)
                            ui.notify(f"Saved setup: {setup_name}", type="positive")
                            dialog.close()

                        with ui.row().classes("w-full justify-end gap-2 mt-4"):
                            ui.button("Cancel", on_click=dialog.close).props("flat")
                            ui.button("Save", on_click=do_save).props("color=primary")

                    dialog.open()

                save_setup_button.on("click", on_save_setup_click)

                with ui.expansion("Advanced hbsolve Options").classes("w-full mt-2"):
                    with ui.row().classes("w-full gap-6 items-center"):
                        include_dc_switch = ui.switch("Include DC", value=False)
                        three_wave_switch = ui.switch("Enable 3-Wave Mixing", value=False)
                        four_wave_switch = ui.switch("Enable 4-Wave Mixing", value=True)
                    with ui.row().classes("w-full gap-4 mt-3"):
                        max_intermod_input = ui.number(
                            "Max Intermod Order (-1 = Inf)",
                            value=-1,
                            format="%.0f",
                        ).classes("flex-grow")
                        max_iterations_input = ui.number(
                            "Max Iterations",
                            value=1000,
                            format="%.0f",
                        ).classes("flex-grow")
                    with ui.row().classes("w-full gap-4 mt-3"):
                        ftol_input = ui.number("f_tol", value=1e-8).classes("flex-grow")
                        linesearch_tol_input = ui.number(
                            "Line Search Switch Tol",
                            value=1e-5,
                        ).classes("flex-grow")
                        alpha_min_input = ui.number("alpha_min", value=1e-4).classes("flex-grow")

                if selected_setup_id and selected_setup_id in saved_setup_by_id:
                    apply_saved_setup(saved_setup_by_id[selected_setup_id])
                    on_termination_setup_change()

                async def run_sim():
                    harmonic_grid_hits: list[tuple[int, int, float, int]] = []
                    try:
                        # Always fetch latest schema from DB at run-time.
                        latest_record, latest_circuit_def = _load_latest_circuit_definition(
                            active_record_id
                        )
                        latest_circuit_definition_ref["definition"] = latest_circuit_def

                        # Basic validation
                        required_values = [
                            start_input.value,
                            stop_input.value,
                            points_input.value,
                            n_mod_input.value,
                            n_pump_input.value,
                            max_intermod_input.value,
                            max_iterations_input.value,
                            ftol_input.value,
                            linesearch_tol_input.value,
                            alpha_min_input.value,
                        ]
                        if any(value is None for value in required_values):
                            reset_status()
                            append_status("warning", "Please fill all simulation parameters.")
                            ui.notify("Please fill all simulation parameters", type="warning")
                            return

                        freq_range = FrequencyRange(
                            start_ghz=start_input.value,
                            stop_ghz=stop_input.value,
                            points=int(points_input.value),
                        )
                        if freq_range.points < 2:
                            reset_status()
                            append_status("warning", "Points must be >= 2.")
                            ui.notify("Points must be >= 2", type="warning")
                            return

                        if not source_forms:
                            reset_status()
                            append_status("warning", "At least one source is required.")
                            ui.notify("Please add at least one source", type="warning")
                            return

                        sources: list[DriveSourceConfig] = []
                        for idx, source_form in enumerate(source_forms, start=1):
                            source_pump_freq_input = source_form["source_pump_freq_input"]
                            port_input = source_form["port_input"]
                            current_input = source_form["current_input"]
                            mode_input = source_form["mode_input"]

                            if (
                                source_pump_freq_input.value is None
                                or port_input.value is None
                                or current_input.value is None
                            ):
                                reset_status()
                                append_status(
                                    "warning",
                                    f"Source {idx} has missing parameters.",
                                )
                                ui.notify(f"Source {idx} has missing parameters", type="warning")
                                return

                            try:
                                parsed_mode = _parse_source_mode_text(mode_input.value)
                            except ValueError:
                                reset_status()
                                append_status(
                                    "warning",
                                    (
                                        f"Source {idx} has an invalid mode tuple. "
                                        "Use comma-separated integers."
                                    ),
                                )
                                ui.notify(
                                    (f"Source {idx} has an invalid mode tuple (e.g. 0 or 1, 0)."),
                                    type="warning",
                                )
                                return

                            normalized_mode = _normalize_source_mode_components(
                                parsed_mode,
                                source_index=idx - 1,
                                source_count=len(source_forms),
                            )

                            sources.append(
                                DriveSourceConfig(
                                    pump_freq_ghz=float(source_pump_freq_input.value),
                                    port=int(port_input.value),
                                    current_amp=float(current_input.value),
                                    mode_components=normalized_mode,
                                )
                            )

                        available_ports = _extract_available_port_indices(latest_circuit_def)
                        if available_ports:
                            invalid_sources = [
                                source for source in sources if source.port not in available_ports
                            ]
                            if invalid_sources:
                                valid_ports = ", ".join(str(p) for p in sorted(available_ports))
                                reset_status()
                                append_status(
                                    "warning",
                                    (f"Source port mismatch. Schema ports: {valid_ports}."),
                                )
                                ui.notify(
                                    (
                                        "Source port mismatch with schema "
                                        f"(valid ports: {valid_ports})"
                                    ),
                                    type="warning",
                                )
                                return

                        max_intermod_order = (
                            None
                            if int(max_intermod_input.value) < 0
                            else int(max_intermod_input.value)
                        )
                        config = SimulationConfig(
                            pump_freq_ghz=float(sources[0].pump_freq_ghz),
                            sources=sources,
                            pump_current_amp=float(sources[0].current_amp),
                            pump_port=int(sources[0].port),
                            pump_mode_index=1,
                            n_modulation_harmonics=int(n_mod_input.value),
                            n_pump_harmonics=int(n_pump_input.value),
                            include_dc=bool(include_dc_switch.value),
                            enable_three_wave_mixing=bool(three_wave_switch.value),
                            enable_four_wave_mixing=bool(four_wave_switch.value),
                            max_intermod_order=max_intermod_order,
                            max_iterations=int(max_iterations_input.value),
                            f_tol=float(ftol_input.value),
                            line_search_switch_tol=float(linesearch_tol_input.value),
                            alpha_min=float(alpha_min_input.value),
                        )
                        harmonic_grid_hits = _detect_harmonic_grid_coincidences(
                            freq_range=freq_range,
                            sources=sources,
                            max_pump_harmonic=config.n_pump_harmonics,
                        )
                        estimated_mode_lattice = _estimate_mode_lattice_size(
                            sources,
                            config.n_modulation_harmonics,
                        )

                        # Show loading state
                        sim_button.props("loading")
                        latest_simulation_result["result"] = None
                        latest_pipeline_result["circuit_record"] = None
                        latest_pipeline_result["source_simulation_bundle_id"] = None
                        latest_pipeline_result["schema_source_hash"] = None
                        latest_pipeline_result["simulation_setup_hash"] = None
                        handle_post_processing_result(None, None)
                        simulation_results_container.clear()
                        post_processing_container.clear()
                        post_processing_results_container.clear()
                        with simulation_results_container:
                            ui.spinner(size="3em").classes("text-primary")
                            ui.label("Checking cached results...").classes("text-muted mt-2")
                        with post_processing_container:
                            ui.label(
                                "Post Processing will be available after simulation completes."
                            ).classes("text-sm text-muted")
                        with post_processing_results_container:
                            ui.label(
                                "Run Post Processing to populate post-processed output traces."
                            ).classes("text-sm text-muted")
                        reset_status("Simulation started.")
                        append_status(
                            "info",
                            (
                                f"Sweep: {freq_range.start_ghz:.3f} to "
                                f"{freq_range.stop_ghz:.3f} GHz, {freq_range.points} points."
                            ),
                        )
                        append_status(
                            "info",
                            (
                                f"Loaded latest schema: {latest_record.name} "
                                f"(id={latest_record.id})."
                            ),
                        )
                        append_status(
                            "info",
                            (
                                f"Configured {len(sources)} source(s). "
                                "Each source has independent pump frequency."
                            ),
                        )
                        for source_idx, source in enumerate(sources, start=1):
                            mode_label = (
                                str(source.mode_components)
                                if source.mode_components is not None
                                else "auto"
                            )
                            append_status(
                                "info",
                                (
                                    f"S{source_idx}: fp={source.pump_freq_ghz:.5f} GHz, "
                                    f"port={source.port}, mode={mode_label}, "
                                    f"Ip={source.current_amp:.3e} A."
                                ),
                            )
                        append_status(
                            "info",
                            (
                                f"Harmonics: Nmod={config.n_modulation_harmonics}, "
                                f"Npump={config.n_pump_harmonics}, DC={config.include_dc}, "
                                f"3WM={config.enable_three_wave_mixing}, "
                                f"4WM={config.enable_four_wave_mixing}."
                            ),
                        )
                        if all(abs(source.current_amp) < 1e-18 for source in sources):
                            append_status(
                                "info",
                                "All source currents are zero (Ip=0, linear drive case).",
                            )
                        if harmonic_grid_hits:
                            append_status(
                                "warning",
                                _format_harmonic_grid_hint(harmonic_grid_hits),
                            )
                        if estimated_mode_lattice >= 128:
                            append_status(
                                "warning",
                                _format_mode_lattice_hint(
                                    sources,
                                    config.n_modulation_harmonics,
                                ),
                            )
                        termination_plan = _resolved_termination_plan()
                        append_status("info", _termination_plan_summary(termination_plan))
                        for warning in list(termination_plan.get("warnings", [])):
                            append_status("warning", str(warning))
                        setup_snapshot = _normalized_simulation_setup_snapshot(freq_range, config)
                        schema_source_hash = _hash_schema_source(latest_record.definition_json)
                        simulation_setup_hash = _hash_stable_json(setup_snapshot)
                        append_status("info", "Normalized simulation setup snapshot prepared.")
                        append_status("info", "Checking result cache...")

                        cache_bundle_id: int | None = None
                        cache_result = None
                        with get_unit_of_work() as uow:
                            cache_result = _load_cached_simulation_result(
                                uow,
                                schema_source_hash=schema_source_hash,
                                simulation_setup_hash=simulation_setup_hash,
                            )

                        if cache_result is not None:
                            cache_bundle_id, result = cache_result
                            append_status(
                                "positive",
                                (
                                    "Cache hit. "
                                    "Loaded result bundle "
                                    f"#{cache_bundle_id} without rerunning Julia."
                                ),
                            )
                        else:
                            append_status("info", "Cache miss.")
                            append_status("info", "Submitting job to Julia worker...")
                            simulation_results_container.clear()
                            post_processing_container.clear()
                            with simulation_results_container:
                                ui.spinner(size="3em").classes("text-primary")
                                ui.label("Running Simulation...").classes("text-muted mt-2")
                            with post_processing_container:
                                ui.label("Waiting for simulation output...").classes(
                                    "text-sm text-muted"
                                )

                            try:
                                # Run Julia simulation in a process to prevent GIL blocking
                                job_started_at = datetime.now()
                                result_task = asyncio.create_task(
                                    run.cpu_bound(
                                        run_simulation,
                                        latest_circuit_def,
                                        freq_range,
                                        config,
                                    )
                                )
                                result = None
                                while result is None:
                                    try:
                                        result = await asyncio.wait_for(
                                            asyncio.shield(result_task),
                                            timeout=5.0,
                                        )
                                    except TimeoutError:
                                        elapsed_seconds = max(
                                            1,
                                            int((datetime.now() - job_started_at).total_seconds()),
                                        )
                                        append_status(
                                            "info",
                                            (
                                                "Julia worker still running... "
                                                f"{elapsed_seconds}s elapsed."
                                            ),
                                        )
                            except ImportError as e:
                                summary, detail = _summarize_simulation_error(e)
                                append_status("negative", summary)
                                latest_simulation_result["result"] = None
                                simulation_results_container.clear()
                                with simulation_results_container:
                                    ui.icon("error", size="lg").classes("text-danger mb-2")
                                    ui.label(summary).classes("text-danger text-sm")
                                    with ui.expansion("Technical Details").classes("w-full mt-3"):
                                        ui.label(detail).classes(
                                            "text-xs text-muted whitespace-pre-wrap break-all"
                                        )
                                post_processing_container.clear()
                                with post_processing_container:
                                    ui.label(
                                        "Post Processing is unavailable because simulation failed."
                                    ).classes("text-sm text-muted")
                                post_processing_results_container.clear()
                                with post_processing_results_container:
                                    ui.label(
                                        "Post Processing Result View is unavailable "
                                        "because simulation failed."
                                    ).classes("text-sm text-muted")
                                sim_button.props(remove="loading")
                                return

                            try:
                                with get_unit_of_work() as uow:
                                    cache_dataset = _ensure_simulation_cache_dataset(uow)
                                    if cache_dataset.id is None:
                                        raise ValueError("Failed to allocate cache dataset id.")
                                    cache_bundle_id = _persist_simulation_result_bundle(
                                        uow=uow,
                                        dataset_id=cache_dataset.id,
                                        result=result,
                                        role="cache",
                                        source_meta={
                                            "origin": "circuit_simulation",
                                            "storage": "system_cache",
                                            "circuit_id": latest_record.id,
                                            "circuit_name": latest_record.name,
                                        },
                                        config_snapshot=setup_snapshot,
                                        schema_source_hash=schema_source_hash,
                                        simulation_setup_hash=simulation_setup_hash,
                                        include_data_records=False,
                                    )
                                    uow.commit()
                                append_status(
                                    "info",
                                    f"Cached result bundle #{cache_bundle_id} stored for reuse.",
                                )
                            except Exception as cache_exc:
                                append_status(
                                    "warning",
                                    f"Result cache write skipped: {cache_exc}",
                                )

                        # Save state for persistence
                        last_sim_result = result
                        last_freq_range = freq_range
                        last_setup_snapshot = setup_snapshot
                        last_schema_source_hash = schema_source_hash
                        last_simulation_setup_hash = simulation_setup_hash
                        append_status(
                            "positive",
                            (
                                "Simulation completed successfully "
                                f"({len(result.frequencies_ghz)} points)."
                            ),
                        )

                        def on_save_click():
                            _save_simulation_results_dialog(
                                latest_record,
                                last_freq_range,
                                last_sim_result,
                                setup_snapshot=last_setup_snapshot,
                                schema_source_hash=last_schema_source_hash,
                                simulation_setup_hash=last_simulation_setup_hash,
                            )

                        latest_raw_save_action["callback"] = on_save_click
                        latest_simulation_result["result"] = last_sim_result
                        _reset_result_view_state(raw_view_state, _RESULT_FAMILY_OPTIONS)
                        latest_pipeline_result["circuit_record"] = latest_record
                        latest_pipeline_result["source_simulation_bundle_id"] = cache_bundle_id
                        latest_pipeline_result["schema_source_hash"] = last_schema_source_hash
                        latest_pipeline_result["simulation_setup_hash"] = last_simulation_setup_hash
                        render_simulation_result_view()
                        handle_post_processing_result(None, None)
                        _render_post_processing_input_panel()
                        render_post_processed_result_view()

                    except Exception as e:
                        summary, detail = _summarize_simulation_error(e)
                        if (
                            "Numerical solver error:" in summary
                            and "solver matrix became singular" in summary
                            and harmonic_grid_hits
                        ):
                            hint = _format_harmonic_grid_hint(harmonic_grid_hits)
                            append_status("warning", hint)
                            detail = f"{detail}\n\nLikely cause from current configuration:\n{hint}"
                        append_status("negative", summary)
                        latest_raw_save_action["callback"] = None
                        latest_simulation_result["result"] = None
                        latest_pipeline_result["circuit_record"] = None
                        latest_pipeline_result["source_simulation_bundle_id"] = None
                        latest_pipeline_result["schema_source_hash"] = None
                        latest_pipeline_result["simulation_setup_hash"] = None
                        handle_post_processing_result(None, None)
                        simulation_results_container.clear()
                        post_processing_container.clear()
                        post_processing_results_container.clear()
                        with post_processing_container:
                            ui.label(
                                "Post Processing is unavailable because simulation failed."
                            ).classes("text-sm text-muted")
                        with post_processing_results_container:
                            ui.label(
                                "Post Processing Result View is unavailable "
                                "because simulation failed."
                            ).classes("text-sm text-muted")
                        with simulation_results_container:
                            ui.icon("error", size="lg").classes("text-danger mb-2")
                            ui.label(summary).classes("text-danger text-sm")
                            with ui.expansion("Technical Details").classes("w-full mt-3"):
                                ui.label(detail).classes(
                                    "text-xs text-muted whitespace-pre-wrap break-all"
                                )
                    finally:
                        sim_button.props(remove="loading")

                sim_button = (
                    ui.button("Run Simulation", on_click=run_sim, icon="play_arrow")
                    .props("color=primary")
                    .classes("w-full mt-4")
                )

            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                with ui.row().classes("items-center gap-2 mb-3"):
                    ui.icon("terminal", size="sm").classes("text-primary")
                    ui.label("Simulation Log").classes("text-lg font-bold text-fg")
                status_container = ui.column().classes("w-full gap-2")
                render_status()

            with ui.card().classes("w-full bg-surface rounded-xl p-6 min-h-[360px]"):
                with ui.row().classes("items-center gap-2 mb-4"):
                    ui.icon("bar_chart", size="sm").classes("text-primary")
                    ui.label("Simulation Results").classes("text-lg font-bold text-fg")

                simulation_results_container = ui.column().classes(
                    "w-full h-full flex items-center justify-center p-4"
                )
                with simulation_results_container:
                    ui.icon("show_chart", size="xl").classes("text-muted mb-4 opacity-50")
                    ui.label("Run simulation to inspect raw result families.").classes(
                        "text-sm text-muted mt-2"
                    )

            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                with ui.row().classes("items-center gap-2 mb-3"):
                    ui.icon("tune", size="sm").classes("text-primary")
                    ui.label("Post Processing").classes("text-lg font-bold text-fg")
                post_processing_container = ui.column().classes("w-full gap-3")
                with post_processing_container:
                    ui.label(
                        "Run a simulation first, then apply port-level coordinate transforms "
                        "and Kron reduction here."
                    ).classes("text-sm text-muted")

            with ui.card().classes("w-full bg-surface rounded-xl p-6 min-h-[320px]"):
                with ui.row().classes("items-center gap-2 mb-4"):
                    ui.icon("tune", size="sm").classes("text-primary")
                    ui.label("Post Processing Results").classes("text-lg font-bold text-fg")
                post_processing_results_container = ui.column().classes(
                    "w-full h-full flex items-center justify-center p-4"
                )
                with post_processing_results_container:
                    ui.icon("data_object", size="xl").classes("text-muted mb-4 opacity-50")
                    ui.label("Run Post Processing to view pipeline output traces.").classes(
                        "text-sm text-muted mt-2"
                    )

    sim_env()


def _save_simulation_results_dialog(
    circuit_record: CircuitRecord,
    freq_range: FrequencyRange,
    result: SimulationResult,
    *,
    setup_snapshot: dict[str, Any] | None = None,
    schema_source_hash: str | None = None,
    simulation_setup_hash: str | None = None,
):
    """Dialog for saving SimulationResult into DataRecords."""
    bundle_records = _build_result_bundle_data_records(dataset_id=0, result=result)
    bundle_trace_count = len(
        {
            (
                record.data_type,
                record.parameter,
            )
            for record in bundle_records
        }
    )

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg bg-surface"):
        ui.label("Save Simulation Results").classes("text-xl font-bold mb-4")
        ui.label(
            "This saves the cached result bundle "
            f"({bundle_trace_count} trace(s), including sidebands / QE / CM when available)."
        ).classes("text-sm text-muted mb-3")

        try:
            with get_unit_of_work() as uow:
                datasets = uow.datasets.list_all()
        except Exception:
            datasets = []

        mode_options = ["Create New"]
        if datasets:
            mode_options.append("Append to Existing")

        mode_toggle = ui.toggle(mode_options, value="Create New").classes("mb-4")

        default_name = f"{circuit_record.name} Sim {datetime.now().strftime('%m%d_%H%M')}"
        name_input = (
            ui.input("New Dataset Name", value=default_name)
            .classes("w-full mb-4 text-lg")
            .props("outlined")
        ).bind_visibility_from(mode_toggle, "value", value="Create New")

        dataset_options = {d.id: d.name for d in datasets}

        dataset_select: Any = (
            ui.select(options=dataset_options, label="Select Existing Dataset")
            .classes("w-full mb-4")
            .props("outlined options-dense")
            .bind_visibility_from(mode_toggle, "value", value="Append to Existing")
        )

        def _save_to_dataset(
            mode: str,
            *,
            new_dataset_name: str,
            selected_dataset_id: int | None,
        ) -> str:
            """Persist the manual-export result bundle and return target dataset name."""
            with get_unit_of_work() as uow:
                if mode == "Create New":
                    ds = DatasetRecord(
                        name=new_dataset_name,
                        source_meta={
                            "origin": "circuit_simulation",
                            "circuit_id": circuit_record.id,
                            "circuit_name": circuit_record.name,
                        },
                        parameters={
                            "start_ghz": freq_range.start_ghz,
                            "stop_ghz": freq_range.stop_ghz,
                            "points": freq_range.points,
                        },
                    )
                    uow.datasets.add(ds)
                    uow.flush()
                    ds_id = ds.id
                    if ds_id is None:
                        raise ValueError("Failed to allocate a dataset id.")
                    ds_name = new_dataset_name
                else:
                    if selected_dataset_id is None:
                        raise ValueError("Please select an existing dataset.")
                    ds_id = selected_dataset_id
                    ds_name = dataset_options[ds_id]

                export_setup_snapshot = setup_snapshot or {
                    "freq_range": {
                        "start_ghz": float(freq_range.start_ghz),
                        "stop_ghz": float(freq_range.stop_ghz),
                        "points": int(freq_range.points),
                    }
                }
                _persist_simulation_result_bundle(
                    uow=uow,
                    dataset_id=ds_id,
                    result=result,
                    role="manual_export",
                    source_meta={
                        "origin": "circuit_simulation",
                        "export_kind": "manual",
                        "circuit_id": circuit_record.id,
                        "circuit_name": circuit_record.name,
                    },
                    config_snapshot=export_setup_snapshot,
                    schema_source_hash=schema_source_hash,
                    simulation_setup_hash=simulation_setup_hash,
                )
                uow.commit()
                return ds_name

        async def save() -> None:
            mode = str(mode_toggle.value)
            name = name_input.value.strip()
            selected_dataset_id = (
                int(dataset_select.value) if isinstance(dataset_select.value, int) else None
            )

            if mode == "Create New" and not name:
                ui.notify("Dataset Name is required.", type="warning")
                return
            if mode != "Create New" and selected_dataset_id is None:
                ui.notify("Please select an existing dataset.", type="warning")
                return

            save_button.disable()
            cancel_button.disable()
            save_button.props(add="loading")
            await asyncio.sleep(0)

            try:
                ds_name = await run.io_bound(
                    _save_to_dataset,
                    mode,
                    new_dataset_name=name,
                    selected_dataset_id=selected_dataset_id,
                )
                ui.notify(
                    f"Saved {bundle_trace_count} trace(s) to: {ds_name}",
                    type="positive",
                )
                dialog.close()
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    ui.notify("A dataset with this name already exists.", type="negative")
                else:
                    ui.notify(f"Failed to save: {e}", type="negative")
            finally:
                save_button.props(remove="loading")
                save_button.enable()
                cancel_button.enable()

        with ui.row().classes("w-full justify-end mt-4 gap-2"):
            cancel_button = ui.button("Cancel", on_click=dialog.close).props("flat")
            save_button = ui.button("Save", on_click=save).props("color=primary")

    dialog.open()


def _save_post_processed_results_dialog(
    *,
    sweep: PortMatrixSweep,
    flow_spec: dict[str, Any],
    circuit_record: CircuitRecord | None,
    source_simulation_bundle_id: int | None,
    schema_source_hash: str | None,
    simulation_setup_hash: str | None,
) -> None:
    """Dialog for saving one post-processed Y sweep into a result bundle."""
    bundle_records = _build_post_processed_y_data_records(dataset_id=0, sweep=sweep)
    bundle_trace_count = len(
        {
            (
                record.data_type,
                record.parameter,
            )
            for record in bundle_records
        }
    )

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg bg-surface"):
        ui.label("Save Post-Processed Results").classes("text-xl font-bold mb-4")
        ui.label(
            "This saves the processed port-level Y bundle "
            f"({bundle_trace_count} trace(s), mode={SimulationResult.mode_token(sweep.mode)})."
        ).classes("text-sm text-muted mb-3")

        try:
            with get_unit_of_work() as uow:
                datasets = uow.datasets.list_all()
        except Exception:
            datasets = []

        mode_options = ["Create New"]
        if datasets:
            mode_options.append("Append to Existing")

        mode_toggle = ui.toggle(mode_options, value="Create New").classes("mb-4")

        circuit_name = str(circuit_record.name) if circuit_record is not None else "Simulation"
        default_name = f"{circuit_name} Post {datetime.now().strftime('%m%d_%H%M')}"
        name_input = (
            ui.input("New Dataset Name", value=default_name)
            .classes("w-full mb-4 text-lg")
            .props("outlined")
        ).bind_visibility_from(mode_toggle, "value", value="Create New")

        dataset_options = {d.id: d.name for d in datasets}

        dataset_select: Any = (
            ui.select(options=dataset_options, label="Select Existing Dataset")
            .classes("w-full mb-4")
            .props("outlined options-dense")
            .bind_visibility_from(mode_toggle, "value", value="Append to Existing")
        )

        def _save_to_dataset(
            mode: str,
            *,
            new_dataset_name: str,
            selected_dataset_id: int | None,
        ) -> str:
            with get_unit_of_work() as uow:
                if mode == "Create New":
                    dataset = DatasetRecord(
                        name=new_dataset_name,
                        source_meta={
                            "origin": "simulation_postprocess",
                            "source_simulation_bundle_id": source_simulation_bundle_id,
                            "circuit_id": (
                                int(circuit_record.id)
                                if circuit_record is not None and circuit_record.id is not None
                                else None
                            ),
                            "circuit_name": circuit_name,
                        },
                        parameters={
                            "start_ghz": float(sweep.frequencies_ghz[0]),
                            "stop_ghz": float(sweep.frequencies_ghz[-1]),
                            "points": len(sweep.frequencies_ghz),
                        },
                    )
                    uow.datasets.add(dataset)
                    uow.flush()
                    ds_id = dataset.id
                    if ds_id is None:
                        raise ValueError("Failed to allocate a dataset id.")
                    ds_name = str(dataset.name)
                else:
                    if selected_dataset_id is None:
                        raise ValueError("Please select an existing dataset.")
                    ds_id = int(selected_dataset_id)
                    ds_name = str(dataset_options[ds_id])

                persisted_records = _build_post_processed_y_data_records(
                    dataset_id=ds_id,
                    sweep=sweep,
                )
                for record in persisted_records:
                    uow.data_records.add(record)
                uow.flush()

                record_ids = [record.id for record in persisted_records if record.id is not None]
                if len(record_ids) != len(persisted_records):
                    raise ValueError("Failed to allocate one or more data record ids.")

                bundle = ResultBundleRecord(
                    dataset_id=ds_id,
                    bundle_type="simulation_postprocess",
                    role="derived_from_simulation",
                    status="completed",
                    schema_source_hash=schema_source_hash,
                    simulation_setup_hash=simulation_setup_hash,
                    source_meta={
                        "origin": "simulation_postprocess",
                        "source_simulation_bundle_id": source_simulation_bundle_id,
                        "source_kind": sweep.source_kind,
                        "mode_token": SimulationResult.mode_token(sweep.mode),
                        "circuit_id": (
                            int(circuit_record.id)
                            if circuit_record is not None and circuit_record.id is not None
                            else None
                        ),
                        "circuit_name": circuit_name,
                    },
                    config_snapshot=dict(flow_spec),
                    result_payload={
                        "kind": "port_level_postprocess",
                        "dimension": int(sweep.dimension),
                        "labels": list(sweep.labels),
                        "mode": [int(value) for value in sweep.mode],
                        "frequency_points": len(sweep.frequencies_ghz),
                    },
                    completed_at=datetime.utcnow(),
                )
                uow.result_bundles.add(bundle)
                uow.flush()
                if bundle.id is None:
                    raise ValueError("Failed to allocate a post-process bundle id.")
                uow.result_bundles.attach_data_records(
                    bundle_id=bundle.id,
                    data_record_ids=record_ids,
                )
                uow.commit()
                return ds_name

        async def save() -> None:
            mode = str(mode_toggle.value)
            name = str(name_input.value or "").strip()
            selected_dataset_id = (
                int(dataset_select.value) if isinstance(dataset_select.value, int) else None
            )
            if mode == "Create New" and not name:
                ui.notify("Dataset Name is required.", type="warning")
                return
            if mode != "Create New" and selected_dataset_id is None:
                ui.notify("Please select an existing dataset.", type="warning")
                return

            save_button.disable()
            cancel_button.disable()
            save_button.props(add="loading")
            await asyncio.sleep(0)

            try:
                ds_name = await run.io_bound(
                    _save_to_dataset,
                    mode,
                    new_dataset_name=name,
                    selected_dataset_id=selected_dataset_id,
                )
                ui.notify(
                    f"Saved {bundle_trace_count} post-processed trace(s) to: {ds_name}",
                    type="positive",
                )
                dialog.close()
            except Exception as exc:
                if "UNIQUE constraint failed" in str(exc):
                    ui.notify("A dataset with this name already exists.", type="negative")
                else:
                    ui.notify(f"Failed to save post-processed results: {exc}", type="negative")
            finally:
                save_button.props(remove="loading")
                save_button.enable()
                cancel_button.enable()

        with ui.row().classes("w-full justify-end mt-4 gap-2"):
            cancel_button = ui.button("Cancel", on_click=dialog.close).props("flat")
            save_button = ui.button("Save", on_click=save).props("color=primary")

    dialog.open()
