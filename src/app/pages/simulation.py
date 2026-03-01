"""Simulation page - Circuit visualization and analysis."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import plotly.graph_objects as go
from nicegui import app, run, ui

from app.layout import app_shell
from app.services.browser_tooling import (
    build_schematic_preview_action_js,
    build_schematic_preview_render_js,
)
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord, DataRecord, DatasetRecord
from core.shared.visualization import get_plotly_layout
from core.simulation.application.circuit_visualizer import generate_circuit_svg
from core.simulation.application.run_simulation import run_simulation
from core.simulation.domain.circuit import (
    CircuitDefinition,
    DriveSourceConfig,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
    format_circuit_definition,
    parse_circuit_definition_source,
)

_SIM_SETUP_STORAGE_KEY = "simulation_saved_setups_by_schema"
_SIM_SETUP_SELECTED_KEY = "simulation_selected_setup_id_by_schema"
_JOSEPHSON_EXAMPLE_PREFIX = "JosephsonCircuits Examples: "
_RESULT_FAMILY_OPTIONS = {
    "s": "S",
    "gain": "Gain",
    "impedance": "Impedance (Z)",
    "admittance": "Admittance (Y)",
    "qe": "Quantum Efficiency (QE)",
    "cm": "Commutation (CM)",
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
    "s": {"s": "S-Parameter"},
    "gain": {"s": "Power Gain from S"},
    "impedance": {"z": "Impedance"},
    "admittance": {"y": "Admittance"},
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
    if isinstance(raw_value, (list, tuple)):
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
        line_search_switch_tol=0.0,
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
        line_search_switch_tol=0.0,
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

    builtin_ids = {str(setup.get("id")) for setup in builtin_setups if setup.get("id")}
    user_setups = [s for s in existing_setups if str(s.get("id")) not in builtin_ids]
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
    raw_map = app.storage.user.get(_SIM_SETUP_SELECTED_KEY, {})
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
) -> go.Figure:
    """Build the selected simulation result figure from the cached result bundle."""
    freq_values = result.frequencies_ghz
    mode_suffix = _format_export_suffix(output_mode, input_mode)
    s_label = f"S{output_port}{input_port}{mode_suffix}"
    z_label = f"Z{output_port}{input_port}{mode_suffix}"
    y_label = f"Y{output_port}{input_port}{mode_suffix}"

    fig = go.Figure()
    line_style = dict(color="rgb(99, 102, 241)", width=2)
    x_axis_title = "Frequency (GHz)"
    y_axis_title = "Value"
    title = "Simulation Result"

    if view_family == "s":
        if metric == "magnitude_db":
            y_values = result.get_mode_s_parameter_db(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
            y_axis_title = "Magnitude (dB)"
            title = f"{s_label} Magnitude (dB)"
        elif metric == "phase_deg":
            y_values = result.get_mode_s_parameter_phase_deg(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
            y_axis_title = "Phase (deg)"
            title = f"{s_label} Phase"
        elif metric == "real":
            y_values = result.get_mode_s_parameter_real(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
            y_axis_title = "Real"
            title = f"{s_label} Real Part"
        elif metric == "imag":
            y_values = result.get_mode_s_parameter_imag(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
            y_axis_title = "Imaginary"
            title = f"{s_label} Imaginary Part"
        else:
            y_values = result.get_mode_s_parameter_magnitude(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
            y_axis_title = "Magnitude (linear)"
            title = f"{s_label} Magnitude"

        fig.add_trace(
            go.Scatter(
                x=freq_values,
                y=y_values,
                mode="lines",
                name=s_label,
                line=line_style,
            )
        )
    elif view_family == "gain":
        if metric == "gain_linear":
            y_values = result.get_mode_gain_linear(output_mode, output_port, input_mode, input_port)
            y_axis_title = "Gain (linear)"
            title = f"Gain from {s_label}"
        else:
            y_values = result.get_mode_gain_db(output_mode, output_port, input_mode, input_port)
            y_axis_title = "Gain (dB)"
            title = f"Gain (dB) from {s_label}"

        fig.add_trace(
            go.Scatter(
                x=freq_values,
                y=y_values,
                mode="lines",
                name=s_label,
                line=line_style,
            )
        )
    elif view_family == "impedance":
        try:
            z_values = result.get_mode_z_parameter_complex(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
        except KeyError:
            z_values = result.calculate_input_impedance_ohm(
                reference_impedance_ohm,
                port=output_port,
            )
        y_values = _complex_component_series(z_values, metric)
        unit_label = "Ohm"
        if metric == "real":
            title = f"{z_label} Real Part"
            y_axis_title = f"Real ({unit_label})"
        elif metric == "imag":
            title = f"{z_label} Imaginary Part"
            y_axis_title = f"Imaginary ({unit_label})"
        else:
            title = f"{z_label} Magnitude"
            y_axis_title = f"Magnitude ({unit_label})"

        fig.add_trace(
            go.Scatter(
                x=freq_values,
                y=y_values,
                mode="lines",
                name=z_label,
                line=line_style,
            )
        )
    elif view_family == "admittance":
        try:
            y_values_complex = result.get_mode_y_parameter_complex(
                output_mode,
                output_port,
                input_mode,
                input_port,
            )
        except KeyError:
            y_values_complex = result.calculate_input_admittance_s(
                reference_impedance_ohm,
                port=output_port,
            )
        y_values = _complex_component_series(y_values_complex, metric)
        unit_label = "S"
        if metric == "real":
            title = f"{y_label} Real Part"
            y_axis_title = f"Real ({unit_label})"
        elif metric == "imag":
            title = f"{y_label} Imaginary Part"
            y_axis_title = f"Imaginary ({unit_label})"
        else:
            title = f"{y_label} Magnitude"
            y_axis_title = f"Magnitude ({unit_label})"

        fig.add_trace(
            go.Scatter(
                x=freq_values,
                y=y_values,
                mode="lines",
                name=y_label,
                line=line_style,
            )
        )
    elif view_family == "qe":
        if trace == "qe_ideal":
            y_values = result.get_mode_qe_ideal(output_mode, output_port, input_mode, input_port)
            title = f"QE Ideal {output_port}{input_port}{mode_suffix}"
        else:
            y_values = result.get_mode_qe(output_mode, output_port, input_mode, input_port)
            title = f"QE {output_port}{input_port}{mode_suffix}"
        y_axis_title = "Quantum Efficiency"
        fig.add_trace(
            go.Scatter(
                x=freq_values,
                y=y_values,
                mode="lines",
                name=title,
                line=line_style,
            )
        )
    elif view_family == "cm":
        y_values = result.get_mode_cm(output_mode, output_port)
        title = f"CM{output_port}{_format_export_suffix(output_mode)}"
        y_axis_title = "Commutation"
        fig.add_trace(
            go.Scatter(
                x=freq_values,
                y=y_values,
                mode="lines",
                name=title,
                line=line_style,
            )
        )
    elif view_family == "complex":
        s_values = result.get_mode_s_parameter_complex(
            output_mode,
            output_port,
            input_mode,
            input_port,
        )
        if trace == "z":
            try:
                complex_values = result.get_mode_z_parameter_complex(
                    output_mode,
                    output_port,
                    input_mode,
                    input_port,
                )
            except KeyError:
                complex_values = result.calculate_input_impedance_ohm(
                    reference_impedance_ohm,
                    port=output_port,
                )
            trace_name = z_label
            title = f"{z_label} Complex Plane"
        elif trace == "y":
            try:
                complex_values = result.get_mode_y_parameter_complex(
                    output_mode,
                    output_port,
                    input_mode,
                    input_port,
                )
            except KeyError:
                complex_values = result.calculate_input_admittance_s(
                    reference_impedance_ohm,
                    port=output_port,
                )
            trace_name = y_label
            title = f"{y_label} Complex Plane"
        else:
            complex_values = s_values
            trace_name = s_label
            title = f"{s_label} Complex Plane"

        fig.add_trace(
            go.Scatter(
                x=[_finite_float_or_none(value.real) for value in complex_values],
                y=[_finite_float_or_none(value.imag) for value in complex_values],
                mode="lines+markers",
                name=trace_name,
                line=line_style,
                marker=dict(size=5),
                customdata=freq_values,
                hovertemplate=("Re=%{x}<br>Im=%{y}<br>f=%{customdata:.6f} GHz<extra></extra>"),
            )
        )
        x_axis_title = "Real"
        y_axis_title = "Imaginary"
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
        circuit_def, migrated_legacy = parse_circuit_definition_source(
            latest_record.definition_json,
            allow_legacy_migration=True,
        )
        if migrated_legacy:
            normalized = format_circuit_definition(circuit_def)
            with get_unit_of_work() as uow:
                db_record = uow.circuits.get(schema_id)
                if db_record is not None:
                    db_record.definition_json = normalized
                    uow.commit()
    except Exception as exc:
        raise ValueError(
            "SimulationInputError: active schema is invalid. "
            "Required fields: schema_version, name, parameters, ports, instances."
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


def _load_saved_setups_for_schema(schema_id: int) -> list[dict[str, Any]]:
    """Load saved simulation setups for one schema from user storage."""
    raw_store = app.storage.user.get(_SIM_SETUP_STORAGE_KEY, {})
    if not isinstance(raw_store, dict):
        return []

    setups = raw_store.get(str(schema_id), [])
    if not isinstance(setups, list):
        return []
    return [s for s in setups if isinstance(s, dict)]


def _save_saved_setups_for_schema(schema_id: int, setups: list[dict[str, Any]]) -> None:
    """Persist saved simulation setups for one schema into user storage."""
    raw_store = app.storage.user.get(_SIM_SETUP_STORAGE_KEY, {})
    store_dict = dict(raw_store) if isinstance(raw_store, dict) else {}
    store_dict[str(schema_id)] = setups
    app.storage.user[_SIM_SETUP_STORAGE_KEY] = store_dict


def _load_selected_setup_id(schema_id: int) -> str:
    """Load currently selected setup id for one schema from user storage."""
    raw_map = app.storage.user.get(_SIM_SETUP_SELECTED_KEY, {})
    if not isinstance(raw_map, dict):
        return ""

    selected = raw_map.get(str(schema_id), "")
    return selected if isinstance(selected, str) else ""


def _save_selected_setup_id(schema_id: int, setup_id: str) -> None:
    """Persist selected setup id for one schema into user storage."""
    raw_map = app.storage.user.get(_SIM_SETUP_SELECTED_KEY, {})
    selected_map = dict(raw_map) if isinstance(raw_map, dict) else {}
    selected_map[str(schema_id)] = setup_id
    app.storage.user[_SIM_SETUP_SELECTED_KEY] = selected_map


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
        active_circuit_id = app.storage.user.get("simulation_active_circuit")
        if active_circuit_id not in circuit_options:
            active_circuit_id = circuits[0].id
            app.storage.user["simulation_active_circuit"] = active_circuit_id

        # --- Top Selector ---
        with ui.row().classes("w-full items-center gap-4 mb-4 bg-surface p-4 rounded-xl"):
            ui.label("Active Schema:").classes("text-sm font-bold text-fg")

            def on_circuit_change(e):
                app.storage.user["simulation_active_circuit"] = e.value
                sim_env.refresh()

            ui.select(
                options=circuit_options, value=active_circuit_id, on_change=on_circuit_change
            ).props("dense outlined options-dense").classes("w-64")

        # Get active record
        active_record = next((c for c in circuits if c.id == active_circuit_id), circuits[0])
        try:
            active_record, circuit_def = _load_latest_circuit_definition(active_record.id)
            svg_content = generate_circuit_svg(circuit_def)
        except Exception as e:
            svg_content = f"<div class='text-danger p-4'>Error parsing selected schema: {e}</div>"

        latest_preview_svg = svg_content
        zoom_label = None

        def render_preview() -> None:
            if zoom_label is None:
                return
            ui.run_javascript(
                build_schematic_preview_render_js(
                    root_id=schematic_container.html_id,
                    label_id=zoom_label.html_id,
                    svg_content=latest_preview_svg,
                    schema_key=f"simulation:{active_record.id}",
                )
            )

        status_history: list[dict[str, str]] = []
        status_container = None

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

        # --- Single-column full-width flow ---
        with ui.column().classes("w-full gap-6"):
            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                with ui.row().classes("w-full items-center justify-between mb-4"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("visibility", size="sm").classes("text-primary")
                        ui.label("Live Preview").classes("text-lg font-bold text-fg")
                    with ui.row().classes("items-center gap-2"):
                        ui.button(
                            icon="remove",
                            on_click=lambda: ui.run_javascript(
                                build_schematic_preview_action_js(
                                    action="zoomOut", root_id=schematic_container.html_id
                                )
                            ),
                        ).props("flat dense round").classes("text-muted")
                        zoom_label = ui.label("100%").classes(
                            "text-xs text-muted min-w-[48px] text-center"
                        )
                        ui.button(
                            icon="add",
                            on_click=lambda: ui.run_javascript(
                                build_schematic_preview_action_js(
                                    action="zoomIn", root_id=schematic_container.html_id
                                )
                            ),
                        ).props("flat dense round").classes("text-muted")
                        ui.button(
                            "Reset",
                            on_click=lambda: ui.run_javascript(
                                build_schematic_preview_action_js(
                                    action="reset", root_id=schematic_container.html_id
                                )
                            ),
                        ).props("outline dense no-caps size=sm")
                schematic_container = ui.html().classes(
                    "w-full min-h-[320px] bg-white rounded-lg p-4 app-schematic-preview"
                )
                render_preview()

            with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                had_selected_setup_entry = _has_selected_setup_entry(active_record.id)
                saved_setups = _ensure_builtin_saved_setups(active_record.id, active_record.name)
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
                selected_setup_id = _load_selected_setup_id(active_record.id)
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
                _save_selected_setup_id(active_record.id, selected_setup_id)

                with ui.row().classes("w-full items-center justify-between mb-4"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("settings", size="sm").classes("text-primary")
                        ui.label("Simulation Setup").classes("text-lg font-bold text-fg")
                    with ui.row().classes("items-center gap-2"):
                        saved_setup_select = (
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

                source_forms: list[dict[str, object]] = []
                sources_container = ui.column().classes("w-full gap-3 mt-2")
                applying_saved_setup = False

                def normalize_source_mode_inputs() -> None:
                    source_count = len(source_forms)
                    if source_count < 1:
                        return

                    for idx, source_form in enumerate(source_forms):
                        mode_input = source_form["mode_input"]
                        try:
                            parsed_mode = _parse_source_mode_text(mode_input.value)
                        except ValueError:
                            continue
                        normalized_mode = _normalize_source_mode_components(
                            parsed_mode,
                            source_index=idx,
                            source_count=source_count,
                        )
                        normalized_text = _format_source_mode_text(normalized_mode)
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

                def remove_source_form(source_card: object) -> None:
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

                        setup_sources.append(
                            _build_source_payload(
                                pump_freq_ghz=float(source_pump_freq_input.value),
                                port=int(port_input.value),
                                current_amp=float(current_input.value),
                                mode=normalized_mode,
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
                            parsed_mode = _normalize_source_mode_components(
                                parsed_mode,
                                source_index=source_index - 1,
                                source_count=generated_mode_width,
                            )
                            add_source_form(
                                DriveSourceConfig(
                                    pump_freq_ghz=float(source["pump_freq_ghz"]),
                                    port=int(source["port"]),
                                    current_amp=float(source["current_amp"]),
                                    mode_components=parsed_mode,
                                )
                            )
                    finally:
                        applying_saved_setup = False

                def refresh_saved_setup_select(preferred_id: str | None = None) -> None:
                    nonlocal saved_setups, saved_setup_by_id
                    saved_setups = _ensure_builtin_saved_setups(
                        active_record.id,
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
                    _save_selected_setup_id(active_record.id, str(current))

                def on_saved_setup_change(e) -> None:
                    if applying_saved_setup:
                        return

                    setup_id = str(e.value or "")
                    _save_selected_setup_id(active_record.id, setup_id)
                    if not setup_id:
                        return

                    setup_record = saved_setup_by_id.get(setup_id)
                    if setup_record is None:
                        ui.notify("Saved setup not found.", type="warning")
                        return
                    apply_saved_setup(setup_record)
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
                            _save_saved_setups_for_schema(active_record.id, updated_setups)
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

                async def run_sim():
                    nonlocal latest_preview_svg
                    harmonic_grid_hits: list[tuple[int, int, float, int]] = []
                    try:
                        # Always fetch latest schema from DB at run-time.
                        latest_record, latest_circuit_def = _load_latest_circuit_definition(
                            active_record.id
                        )
                        # Keep preview synced with the exact schema being simulated.
                        latest_preview_svg = generate_circuit_svg(latest_circuit_def)
                        render_preview()

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

                        # Show loading state
                        sim_button.props("loading")
                        results_container.clear()
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
                        append_status("info", "Submitting job to Julia worker...")
                        with results_container:
                            ui.spinner(size="3em").classes("text-primary")
                            ui.label("Running Simulation...").classes("text-muted mt-2")

                        try:
                            # Run Julia simulation in a process to prevent GIL blocking
                            result = await run.cpu_bound(
                                run_simulation,
                                latest_circuit_def,
                                freq_range,
                                config,
                            )
                        except ImportError as e:
                            summary, detail = _summarize_simulation_error(e)
                            append_status("negative", summary)
                            results_container.clear()
                            with results_container:
                                ui.icon("error", size="lg").classes("text-danger mb-2")
                                ui.label(summary).classes("text-danger text-sm")
                                with ui.expansion("Technical Details").classes("w-full mt-3"):
                                    ui.label(detail).classes(
                                        "text-xs text-muted whitespace-pre-wrap break-all"
                                    )
                            sim_button.props(remove="loading")
                            return

                        # Save state for persistence
                        last_sim_result = result
                        last_freq_range = freq_range
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
                            )

                        results_container.clear()
                        with results_container:
                            view_family_to_label = {
                                family: label for family, label in _RESULT_FAMILY_OPTIONS.items()
                            }
                            view_label_to_family = {
                                label: family for family, label in _RESULT_FAMILY_OPTIONS.items()
                            }

                            with ui.row().classes(
                                "w-full items-center justify-between gap-3 mb-3 flex-wrap"
                            ):
                                ui.label(
                                    "All cached mode families come from one hbsolve run. "
                                    "Changing view, ports, or modes does not rerun the simulation."
                                ).classes("text-xs text-muted")
                                ui.button(
                                    "Save Results to Dataset",
                                    icon="save",
                                    on_click=on_save_click,
                                ).props("outline color=primary size=sm")
                            with ui.row().classes("w-full gap-3 items-end mb-3 flex-wrap"):
                                view_toggle = ui.toggle(
                                    list(view_label_to_family),
                                    value=view_family_to_label["s"],
                                ).props("unelevated no-caps")
                                metric_select = (
                                    ui.select(
                                        label="Metric",
                                        options=_result_metric_options_for_family("s"),
                                        value="magnitude_linear",
                                    )
                                    .props("dense outlined options-dense")
                                    .classes("w-52")
                                )
                                trace_select = (
                                    ui.select(
                                        label="Trace",
                                        options=_result_trace_options_for_family("s"),
                                        value="s",
                                    )
                                    .props("dense outlined options-dense")
                                    .classes("w-60")
                                )
                                mode_options = _result_mode_options(last_sim_result)
                                default_mode = next(iter(mode_options))
                                output_mode_select = (
                                    ui.select(
                                        label="Output Mode",
                                        options=mode_options,
                                        value=default_mode,
                                    )
                                    .props("dense outlined options-dense")
                                    .classes("w-48")
                                )
                                input_mode_select = (
                                    ui.select(
                                        label="Input Mode",
                                        options=mode_options,
                                        value=default_mode,
                                    )
                                    .props("dense outlined options-dense")
                                    .classes("w-48")
                                )
                                port_options = _result_port_options(last_sim_result)
                                default_port = next(iter(port_options))
                                output_port_select = (
                                    ui.select(
                                        label="Output Port",
                                        options=port_options,
                                        value=default_port,
                                    )
                                    .props("dense outlined")
                                    .classes("w-32")
                                )
                                input_port_select = (
                                    ui.select(
                                        label="Input Port",
                                        options=port_options,
                                        value=default_port,
                                    )
                                    .props("dense outlined")
                                    .classes("w-32")
                                )
                                reference_impedance_input = ui.number(
                                    "Z0 (Ohm)",
                                    value=50.0,
                                    format="%.6g",
                                ).classes("w-36")

                            helper_label = ui.label("").classes("w-full text-xs text-muted mb-2")
                            plot_host = ui.column().classes("w-full min-h-[400px]")

                            def render_result_view() -> None:
                                current_family = view_label_to_family.get(
                                    str(view_toggle.value or ""),
                                    "s",
                                )
                                metric_options = _result_metric_options_for_family(current_family)
                                trace_options = _result_trace_options_for_family(current_family)

                                metric_select.options = metric_options
                                if metric_select.value not in metric_options:
                                    metric_select.value = _first_option_key(metric_options)

                                trace_select.options = trace_options
                                if trace_select.value not in trace_options:
                                    trace_select.value = _first_option_key(trace_options)

                                selected_output_mode_token = str(
                                    output_mode_select.value or default_mode
                                )
                                selected_input_mode_token = str(
                                    input_mode_select.value or default_mode
                                )
                                selected_output_mode = SimulationResult.parse_mode_token(
                                    selected_output_mode_token
                                )
                                selected_input_mode = SimulationResult.parse_mode_token(
                                    selected_input_mode_token
                                )
                                selected_output_port = int(output_port_select.value or default_port)
                                selected_input_port = int(input_port_select.value or default_port)
                                selected_trace = str(trace_select.value)

                                output_mode_select.options = mode_options
                                input_mode_select.options = mode_options
                                input_port_select.options = port_options
                                output_port_select.options = port_options

                                lock_input_selectors = current_family == "cm"
                                if current_family == "cm":
                                    if selected_input_mode != selected_output_mode:
                                        selected_input_mode = selected_output_mode
                                        input_mode_select.value = SimulationResult.mode_token(
                                            selected_output_mode
                                        )
                                    if selected_input_port != selected_output_port:
                                        selected_input_port = selected_output_port
                                        input_port_select.value = selected_output_port

                                if current_family in {"impedance", "admittance"} or (
                                    current_family == "complex" and selected_trace in {"z", "y"}
                                ):
                                    lock_input_selectors = True
                                    if selected_input_port != selected_output_port:
                                        selected_input_port = selected_output_port
                                        input_port_select.value = selected_input_port
                                    if selected_input_mode != selected_output_mode:
                                        selected_input_mode = selected_output_mode
                                        input_mode_select.value = SimulationResult.mode_token(
                                            selected_output_mode
                                        )
                                if lock_input_selectors:
                                    input_port_select.disable()
                                    input_mode_select.disable()
                                else:
                                    input_port_select.enable()
                                    input_mode_select.enable()

                                z0_value = float(reference_impedance_input.value or 50.0)
                                if z0_value <= 0:
                                    z0_value = 50.0
                                    reference_impedance_input.value = z0_value

                                figure = _build_simulation_result_figure(
                                    result=last_sim_result,
                                    view_family=current_family,
                                    metric=str(metric_select.value),
                                    trace=selected_trace,
                                    output_mode=selected_output_mode,
                                    output_port=selected_output_port,
                                    input_mode=selected_input_mode,
                                    input_port=selected_input_port,
                                    reference_impedance_ohm=z0_value,
                                    dark_mode=app.storage.user.get("dark_mode", True),
                                )

                                if current_family in {"impedance", "admittance"}:
                                    family_prefix = "Z" if current_family == "impedance" else "Y"
                                    helper_label.text = (
                                        f"{current_family.title()} is using the native "
                                        f"{family_prefix}{selected_output_port}"
                                        f"{selected_input_port} "
                                        f"trace for mode {selected_output_mode}."
                                    )
                                elif current_family == "qe":
                                    helper_label.text = (
                                        "QE uses the cached linearized hbsolve bundle. "
                                        "Select non-zero modes to inspect idler/sideband QE."
                                    )
                                elif current_family == "cm":
                                    helper_label.text = (
                                        "CM is indexed by output mode and output port only. "
                                        "Input selectors are fixed to match."
                                    )
                                elif current_family == "complex":
                                    if selected_trace == "s":
                                        helper_label.text = (
                                            "Complex plane is showing the selected cached "
                                            f"S{selected_output_port}{selected_input_port} trace."
                                        )
                                    else:
                                        helper_label.text = (
                                            "Complex plane is showing the selected cached "
                                            f"{selected_trace.upper()}{selected_output_port}"
                                            f"{selected_input_port} trace."
                                        )
                                else:
                                    helper_label.text = (
                                        "Select non-zero modes to inspect idler/sideband "
                                        "traces without rerunning the solver."
                                    )

                                plot_host.clear()
                                with plot_host:
                                    ui.plotly(figure).classes("w-full h-full min-h-[400px]")

                            view_toggle.on_value_change(lambda _e: render_result_view())
                            metric_select.on_value_change(lambda _e: render_result_view())
                            trace_select.on_value_change(lambda _e: render_result_view())
                            output_mode_select.on_value_change(lambda _e: render_result_view())
                            input_mode_select.on_value_change(lambda _e: render_result_view())
                            output_port_select.on_value_change(lambda _e: render_result_view())
                            input_port_select.on_value_change(lambda _e: render_result_view())
                            reference_impedance_input.on_value_change(
                                lambda _e: render_result_view()
                            )
                            render_result_view()

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
                        results_container.clear()
                        with results_container:
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

                results_container = ui.column().classes(
                    "w-full h-full flex items-center justify-center p-4"
                )
                with results_container:
                    ui.icon("show_chart", size="xl").classes("text-muted mb-4 opacity-50")
                    ui.label("Run a simulation to view S-parameters here.").classes(
                        "text-sm text-muted mt-2"
                    )

    sim_env()


def _save_simulation_results_dialog(
    circuit_record: CircuitRecord, freq_range: FrequencyRange, result: SimulationResult
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

        dataset_select = (
            ui.select(options=dataset_options, label="Select Existing Dataset")
            .classes("w-full mb-4")
            .props("outlined options-dense")
            .bind_visibility_from(mode_toggle, "value", value="Append to Existing")
        )

        def save():
            mode = mode_toggle.value
            try:
                with get_unit_of_work() as uow:
                    if mode == "Create New":
                        name = name_input.value.strip()
                        if not name:
                            ui.notify("Dataset Name is required.", type="warning")
                            return
                        # Create DatasetRecord
                        ds = DatasetRecord(
                            name=name,
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
                        uow.commit()  # Commit to get Dataset ID
                        ds_id = ds.id
                        ds_name = name
                    else:
                        if not dataset_select.value:
                            ui.notify("Please select an existing dataset.", type="warning")
                            return
                        ds_id = dataset_select.value
                        ds_name = dataset_options[ds_id]

                    data_records = _build_result_bundle_data_records(ds_id, result)
                    for data_record in data_records:
                        uow.data_records.add(data_record)
                    uow.commit()  # Commit all data records

                ui.notify(
                    (f"Saved {bundle_trace_count} trace(s) to: {ds_name}"),
                    type="positive",
                )
                dialog.close()
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    ui.notify("A dataset with this name already exists.", type="negative")
                else:
                    ui.notify(f"Failed to save: {e}", type="negative")

        with ui.row().classes("w-full justify-end mt-4 gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("color=primary")

    dialog.open()
