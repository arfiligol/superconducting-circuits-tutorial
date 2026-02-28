"""Simulation page - Circuit visualization and analysis."""

from __future__ import annotations

import ast
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
)

_SIM_SETUP_STORAGE_KEY = "simulation_saved_setups_by_schema"
_SIM_SETUP_SELECTED_KEY = "simulation_selected_setup_id_by_schema"


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
        js_data = ast.literal_eval(latest_record.definition_json)
        circuit_def = CircuitDefinition.model_validate(js_data)
    except Exception as exc:
        raise ValueError(
            "SimulationInputError: active schema is invalid. "
            "Required fields: name, parameters, topology."
        ) from exc

    return latest_record, circuit_def


def _extract_available_port_indices(circuit: CircuitDefinition) -> set[int]:
    """Collect schema-declared port indices from topology entries."""
    ports: set[int] = set()
    for comp_name, _, _, value_ref in circuit.topology:
        if not comp_name.lower().startswith("p"):
            continue
        try:
            port_index = int(value_ref)
        except (TypeError, ValueError):
            digits = "".join(ch for ch in comp_name if ch.isdigit())
            if not digits:
                continue
            port_index = int(digits)
        if port_index >= 1:
            ports.add(port_index)
    return ports


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
            ).props("dense outline dark standout").classes("w-64")

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
                saved_setups = _load_saved_setups_for_schema(active_record.id)
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
                if selected_setup_id not in saved_setup_options:
                    selected_setup_id = ""

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

                def refresh_source_forms() -> None:
                    has_multiple_sources = len(source_forms) > 1
                    for idx, source_form in enumerate(source_forms, start=1):
                        title = source_form["title"]
                        remove_button = source_form["remove_button"]
                        title.text = f"Source {idx}"
                        remove_button.enabled = has_multiple_sources

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
                    source_defaults = initial or DriveSourceConfig()
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

                    source_forms.append(
                        {
                            "card": source_card,
                            "title": title_label,
                            "remove_button": remove_button,
                            "source_pump_freq_input": source_pump_freq_input,
                            "port_input": port_input,
                            "current_input": current_input,
                        }
                    )
                    refresh_source_forms()

                with ui.row().classes("w-full items-center justify-between mt-3"):
                    ui.label("Sources").classes("text-sm font-bold text-fg")
                    ui.button("Add Source", icon="add", on_click=add_source_form).props(
                        "outline color=primary size=sm"
                    )

                add_source_form(DriveSourceConfig(pump_freq_ghz=5.0, port=1, current_amp=0.0))

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

                        if (
                            source_pump_freq_input.value is None
                            or port_input.value is None
                            or current_input.value is None
                        ):
                            ui.notify(f"Source {idx} has missing parameters.", type="warning")
                            return None

                        setup_sources.append(
                            {
                                "pump_freq_ghz": float(source_pump_freq_input.value),
                                "port": int(port_input.value),
                                "current_amp": float(current_input.value),
                            }
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

                        for source in valid_sources:
                            add_source_form(
                                DriveSourceConfig(
                                    pump_freq_ghz=float(source["pump_freq_ghz"]),
                                    port=int(source["port"]),
                                    current_amp=float(source["current_amp"]),
                                )
                            )
                    finally:
                        applying_saved_setup = False

                def refresh_saved_setup_select(preferred_id: str | None = None) -> None:
                    nonlocal saved_setups, saved_setup_by_id
                    saved_setups = _load_saved_setups_for_schema(active_record.id)
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

                            sources.append(
                                DriveSourceConfig(
                                    pump_freq_ghz=float(source_pump_freq_input.value),
                                    port=int(port_input.value),
                                    current_amp=float(current_input.value),
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
                            append_status(
                                "info",
                                (
                                    f"S{source_idx}: fp={source.pump_freq_ghz:.5f} GHz, "
                                    f"port={source.port}, Ip={source.current_amp:.3e} A."
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

                        # Plot Results
                        fig = go.Figure()

                        fig.add_trace(
                            go.Scatter(
                                x=result.frequencies_ghz,
                                y=result.s11_magnitude,
                                mode="lines",
                                name="|S11|",
                                line=dict(color="rgb(99, 102, 241)", width=2),
                            )
                        )

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

                        theme_layout = get_plotly_layout(
                            dark=app.storage.user.get("dark_mode", True)
                        )
                        fig.update_layout(
                            title="S11 Magnitude Response",
                            xaxis_title="Frequency (GHz)",
                            yaxis_title="Magnitude (linear)",
                            margin=dict(l=40, r=20, t=40, b=40),
                            showlegend=True,
                            hovermode="x unified",
                            **theme_layout,
                        )

                        def on_save_click():
                            _save_simulation_results_dialog(
                                latest_record,
                                last_freq_range,
                                last_sim_result,
                            )

                        results_container.clear()
                        with results_container:
                            with ui.row().classes("w-full justify-end mb-2"):
                                ui.button(
                                    "Save Results to Dataset",
                                    icon="save",
                                    on_click=on_save_click,
                                ).props("outline color=primary size=sm")
                            ui.plotly(fig).classes("w-full h-full min-h-[400px]")

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
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg bg-surface"):
        ui.label("Save Simulation Results").classes("text-xl font-bold mb-4")

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
            .props("standout dark")
        ).bind_visibility_from(mode_toggle, "value", value="Create New")

        dataset_options = {d.id: d.name for d in datasets}

        dataset_select = (
            ui.select(options=dataset_options, label="Select Existing Dataset")
            .classes("w-full mb-4")
            .props("standout dark")
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

                    # Create DataRecords for real and imaginary parts of S11
                    dr_real = DataRecord(
                        dataset_id=ds_id,
                        data_type="s_params",
                        parameter="S11",
                        representation="real",
                        axes=[
                            {"name": "frequency", "unit": "GHz", "values": result.frequencies_ghz}
                        ],
                        values=result.s11_real,
                    )
                    dr_imag = DataRecord(
                        dataset_id=ds_id,
                        data_type="s_params",
                        parameter="S11",
                        representation="imaginary",
                        axes=[
                            {"name": "frequency", "unit": "GHz", "values": result.frequencies_ghz}
                        ],
                        values=result.s11_imag,
                    )
                    uow.data_records.add(dr_real)
                    uow.data_records.add(dr_imag)
                    uow.commit()  # Commit all data records

                ui.notify(f"Saved results to: {ds_name}", type="positive")
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
