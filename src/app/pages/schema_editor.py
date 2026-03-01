"""Schema Editor page for Schematic Netlist definitions."""

from __future__ import annotations

from nicegui import app, ui

from app.layout import app_shell
from app.services.browser_tooling import (
    build_schema_formatter_hotkey_js,
    build_schema_formatter_js,
    build_schematic_preview_action_js,
    build_schematic_preview_render_js,
)
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord
from core.simulation.application.circuit_visualizer import generate_circuit_svg
from core.simulation.domain.circuit import (
    format_circuit_definition,
    parse_circuit_definition_source,
)

_DEFAULT_CIRCUIT_STR = """{
    "schema_version": "0.1",
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
        "L_main": {"default": 10.0, "unit": "nH"},
        "C_main": {"default": 1.0, "unit": "pF"}
    },
    "ports": [
        {
            "id": "P1",
            "node": "n1",
            "ground": "gnd",
            "index": 1,
            "role": "signal",
            "side": "left"
        }
    ],
    "instances": [
        {
            "id": "R1",
            "kind": "resistor",
            "pins": ["n1", "gnd"],
            "value_ref": "R_port",
            "role": "termination"
        },
        {
            "id": "L1",
            "kind": "inductor",
            "pins": ["n1", "n2"],
            "value_ref": "L_main",
            "role": "signal"
        },
        {
            "id": "C1",
            "kind": "capacitor",
            "pins": ["n2", "gnd"],
            "value_ref": "C_main",
            "role": "shunt"
        }
    ],
    "layout": {
        "direction": "lr",
        "profile": "generic"
    }
}"""

_COMPONENT_REF_COLUMNS = [
    {"name": "kind", "label": "Component", "field": "kind", "align": "left"},
    {"name": "prefix", "label": "Name Prefix", "field": "prefix", "align": "left"},
    {"name": "units", "label": "Allowed Units", "field": "units", "align": "left"},
    {"name": "example", "label": "Example", "field": "example", "align": "left"},
    {"name": "notes", "label": "Notes", "field": "notes", "align": "left"},
]

_COMPONENT_REF_ROWS = [
    {
        "kind": "Port",
        "prefix": "ports[*]",
        "units": "-",
        "example": '{"id": "P1", "node": "n1", "ground": "gnd", "index": 1, ...}',
        "notes": "Declare ports in the top-level ports list; do not repeat them in instances.",
    },
    {
        "kind": "Resistor",
        "prefix": "kind=resistor",
        "units": "Ohm, kOhm, MOhm",
        "example": '{"id": "R1", "kind": "resistor", "pins": ["n1", "gnd"], ...}',
        "notes": "For stability, each port should usually have a shunt resistor (e.g., 50 Ohm).",
    },
    {
        "kind": "Inductor",
        "prefix": "kind=inductor",
        "units": "H, mH, uH, nH, pH",
        "example": '{"id": "L1", "kind": "inductor", "pins": ["n1", "n2"], ...}',
        "notes": "Two-pin linear inductor for signal or shunt branches.",
    },
    {
        "kind": "Capacitor",
        "prefix": "kind=capacitor",
        "units": "F, mF, uF, nF, pF, fF",
        "example": '{"id": "C1", "kind": "capacitor", "pins": ["n2", "gnd"], ...}',
        "notes": "Typical LC usage is pF for readability.",
    },
    {
        "kind": "Josephson Junction",
        "prefix": "kind=josephson_junction",
        "units": "H, mH, uH, nH, pH",
        "example": '{"id": "Lj1", "kind": "josephson_junction", "pins": ["n2", "gnd"], ...}',
        "notes": "Rendered as junction symbol in preview.",
    },
]


@ui.page("/schemas/{schema_id}")
def schema_editor_page(schema_id: str):
    def content():
        # Fetch existing if not "new"
        circuit_record = None
        if schema_id != "new":
            try:
                with get_unit_of_work() as uow:
                    circuit_record = uow.circuits.get(int(schema_id))
            except Exception as e:
                ui.label(f"Error loading circuit: {e}").classes("text-danger")
                return

            if not circuit_record:
                ui.label("Circuit not found").classes("text-danger")
                return

        with ui.row().classes("w-full items-center gap-4 mb-6"):
            ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to("/schemas")).props(
                "flat round"
            ).classes("text-muted")
            title_label = ui.label(
                f"Edit Schema: {circuit_record.name}" if circuit_record else "New Circuit Schema"
            ).classes("text-2xl font-bold text-fg")

        latest_svg = ""
        zoom_label = None

        def update_preview_content() -> None:
            if zoom_label is None:
                return
            ui.run_javascript(
                build_schematic_preview_render_js(
                    root_id=svg_container.html_id,
                    label_id=zoom_label.html_id,
                    svg_content=latest_svg,
                    schema_key=f"schema-editor:{schema_id}",
                )
            )

        def show_invalid_preview() -> None:
            if zoom_label is None:
                return
            ui.run_javascript(
                build_schematic_preview_render_js(
                    root_id=svg_container.html_id,
                    label_id=zoom_label.html_id,
                    svg_content="",
                    schema_key=f"schema-editor:{schema_id}",
                    empty_html=(
                        "<div class='text-gray-400 text-sm'>Invalid Circuit Definition</div>"
                    ),
                )
            )

        with ui.row().classes("w-full gap-6"):
            with (
                ui.column().classes("w-full md:w-1/2"),
                ui.card().classes("w-full bg-surface rounded-xl p-6 min-h-[400px]"),
            ):
                with ui.row().classes("items-center w-full justify-between mb-4"):
                    with ui.row().classes("gap-2 items-center"):
                        ui.icon("science", size="sm").classes("text-primary")
                        ui.label("Circuit Definition").classes("text-lg font-bold text-fg")

                    def save_schema():
                        try:
                            circuit_def, _ = parse_circuit_definition_source(json_input.value)
                            name = circuit_def.name
                        except Exception as e:
                            ui.notify(
                                "Invalid Circuit Definition. Required fields: "
                                "schema_version, name, parameters, ports, instances. "
                                f"Details: {e}",
                                type="negative",
                            )
                            return

                        if not name:
                            ui.notify("Name cannot be empty in the dictionary.", type="negative")
                            return

                        try:
                            with get_unit_of_work() as uow:
                                if circuit_record:
                                    db_circuit = uow.circuits.get(circuit_record.id)
                                    db_circuit.name = name
                                    formatted_definition = format_circuit_definition(circuit_def)
                                    db_circuit.definition_json = formatted_definition
                                    uow.commit()
                                    json_input.value = formatted_definition
                                    ui.notify("Schema updated.", type="positive")
                                else:
                                    formatted_definition = format_circuit_definition(circuit_def)
                                    new_circuit = CircuitRecord(
                                        name=name, definition_json=formatted_definition
                                    )
                                    uow.circuits.add(new_circuit)
                                    uow.commit()
                                    json_input.value = formatted_definition
                                    ui.notify("New schema created.", type="positive")
                                    ui.navigate.to(f"/schemas/{new_circuit.id}")
                        except Exception as e:
                            ui.notify(f"Database Error: {e}", type="negative")

                    async def format_schema() -> None:
                        format_status.classes(add="hidden", remove="block")
                        format_status.text = "Formatting..."

                        browser_result = await ui.run_javascript(
                            build_schema_formatter_js(json_input.value)
                        )

                        formatted_text: str | None = None
                        if isinstance(browser_result, dict) and browser_result.get("ok"):
                            text = browser_result.get("text")
                            if isinstance(text, str):
                                formatted_text = text

                        if formatted_text is None:
                            try:
                                circuit_def, _ = parse_circuit_definition_source(json_input.value)
                                formatted_text = format_circuit_definition(circuit_def)
                            except Exception as exc:
                                error_detail = (
                                    browser_result.get("error")
                                    if isinstance(browser_result, dict)
                                    else None
                                )
                                message = error_detail or str(exc)
                                format_status.text = f"Format failed: {message}"
                                format_status.classes(add="block", remove="hidden")
                                ui.notify(f"Format failed: {message}", type="negative")
                                return

                        if formatted_text != json_input.value:
                            json_input.set_value(formatted_text)
                        format_status.text = "Formatted with browser formatter."
                        format_status.classes(add="block", remove="hidden")
                        ui.notify("Schema formatted.", type="positive")

                    format_button = ui.button(
                        "Format",
                        icon="auto_fix_high",
                        on_click=format_schema,
                    ).props("outline size=sm")
                    ui.button("Save Schema", icon="save", on_click=save_schema).props(
                        "color=primary size=sm"
                    )

                error_label = ui.label("").classes("text-danger text-sm hidden mb-2")
                format_status = ui.label("").classes("text-xs text-muted hidden mb-2")

                if circuit_record:
                    try:
                        normalized, migrated_legacy = parse_circuit_definition_source(
                            circuit_record.definition_json,
                            allow_legacy_migration=True,
                        )
                        def_val = format_circuit_definition(normalized)
                        if migrated_legacy:
                            with get_unit_of_work() as uow:
                                db_circuit = uow.circuits.get(circuit_record.id)
                                if db_circuit is not None:
                                    db_circuit.definition_json = def_val
                                    uow.commit()
                    except Exception:
                        def_val = circuit_record.definition_json
                else:
                    def_val = _DEFAULT_CIRCUIT_STR
                ui.label("Schematic Netlist").classes("text-sm text-muted mb-2")
                editor_theme = (
                    "vscodeDark" if app.storage.user.get("dark_mode", True) else "vscodeLight"
                )
                json_input = ui.codemirror(
                    value=def_val,
                    language="Python",
                    theme=editor_theme,
                    indent=" " * 4,
                ).classes("w-full app-netlist-editor")
                ui.label("Tip: Use Tab / Shift+Tab for indentation.").classes(
                    "text-xs text-muted mt-2"
                )
                ui.label("Shortcut: Ctrl/Cmd + Shift + F").classes("text-xs text-muted mt-1")

            with (
                ui.column().classes("w-full md:w-[45%]"),
                ui.card().classes("w-full h-full bg-surface rounded-xl p-6 min-h-[400px]"),
            ):
                with ui.row().classes("w-full items-center justify-between mb-4"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("visibility", size="sm").classes("text-primary")
                        ui.label("Live Preview").classes("text-lg font-bold text-fg")
                    with ui.row().classes("items-center gap-2"):
                        ui.button(
                            icon="remove",
                            on_click=lambda: ui.run_javascript(
                                build_schematic_preview_action_js(
                                    action="zoomOut", root_id=svg_container.html_id
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
                                    action="zoomIn", root_id=svg_container.html_id
                                )
                            ),
                        ).props("flat dense round").classes("text-muted")
                        ui.button(
                            "Reset",
                            on_click=lambda: ui.run_javascript(
                                build_schematic_preview_action_js(
                                    action="reset", root_id=svg_container.html_id
                                )
                            ),
                        ).props("outline dense no-caps size=sm")

                ui.label("The schematic updates automatically as you type.").classes(
                    "text-xs text-muted mb-4"
                )

                svg_container = ui.html().classes(
                    "w-full flex-grow bg-white rounded-lg p-4 app-schematic-preview"
                )

        with ui.card().classes("w-full bg-surface rounded-xl p-6 mt-2"):
            with ui.row().classes("items-center gap-2 mb-3"):
                ui.icon("table_chart", size="sm").classes("text-primary")
                ui.label("Component & Unit Reference").classes("text-lg font-bold text-fg")
            ui.table(
                columns=_COMPONENT_REF_COLUMNS,
                rows=_COMPONENT_REF_ROWS,
                row_key="kind",
            ).props("dense wrap-cells").classes("w-full")
            ui.label(
                "Define `parameters`, declare `ports`, and reference parameter keys from "
                "`instances[*].value_ref`. Preferred ground token: gnd."
            ).classes("text-xs text-muted mt-3")

        # Function to update schematic based on input
        def update_schematic(e=None):
            nonlocal latest_svg
            try:
                circuit, _ = parse_circuit_definition_source(json_input.value)

                # Generate SVG
                latest_svg = generate_circuit_svg(circuit)

                # Update UI
                update_preview_content()
                error_label.classes(add="hidden", remove="block")

                # Sync title
                if circuit.name:
                    title_label.text = (
                        f"Edit Schema: {circuit.name}"
                        if circuit_record
                        else f"New Schema: {circuit.name}"
                    )

            except Exception as e:
                error_label.text = (
                    "Error Parsing Definition (required: schema_version + name + parameters + "
                    f"ports + instances): {e!s}"
                )
                error_label.classes(add="block", remove="hidden")
                latest_svg = ""
                show_invalid_preview()

        # Update it once on load
        update_schematic()
        ui.run_javascript(
            build_schema_formatter_hotkey_js(
                button_id=format_button.html_id,
                scope_id=json_input.html_id,
            )
        )

        # Trigger on change
        json_input.on_value_change(update_schematic)

    app_shell(content)()
