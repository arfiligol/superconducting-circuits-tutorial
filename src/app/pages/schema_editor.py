"""Schema Editor page - Live preview for Circuit definitions."""

from __future__ import annotations

import ast

from nicegui import ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord
from core.simulation.application.circuit_visualizer import generate_circuit_svg
from core.simulation.domain.circuit import CircuitDefinition

_DEFAULT_CIRCUIT_STR = """{
    "name": "LC Resonator",
    "components": [
        {"name": "L1", "value": 10.0, "unit": "nH"},
        {"name": "C1", "value": 1.0, "unit": "pF"},
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("L1", "1", "2", "L1"),
        ("C1", "2", "0", "C1")
    ]
}"""


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

        with ui.row().classes("w-full gap-6"):
            # Left Column: Circuit Definition Input
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
                            js_data = ast.literal_eval(json_input.value)
                            circuit_def = CircuitDefinition.model_validate(js_data)
                            name = circuit_def.name
                        except Exception as e:
                            ui.notify(f"Invalid Circuit Definition syntax: {e}", type="negative")
                            return

                        if not name:
                            ui.notify("Name cannot be empty in the dictionary.", type="negative")
                            return

                        try:
                            with get_unit_of_work() as uow:
                                if circuit_record:
                                    db_circuit = uow.circuits.get(circuit_record.id)
                                    db_circuit.name = name
                                    db_circuit.definition_json = json_input.value
                                    uow.commit()
                                    ui.notify("Schema updated.", type="positive")
                                else:
                                    new_circuit = CircuitRecord(
                                        name=name, definition_json=json_input.value
                                    )
                                    uow.circuits.add(new_circuit)
                                    uow.commit()
                                    ui.notify("New schema created.", type="positive")
                                    ui.navigate.to(f"/schemas/{new_circuit.id}")
                        except Exception as e:
                            ui.notify(f"Database Error: {e}", type="negative")

                    ui.button("Save Schema", icon="save", on_click=save_schema).props(
                        "color=primary size=sm"
                    )

                error_label = ui.label("").classes("text-danger text-sm hidden mb-2")

                def_val = circuit_record.definition_json if circuit_record else _DEFAULT_CIRCUIT_STR
                json_input = (
                    ui.textarea(
                        "Netlist Dictionary",
                        value=def_val,
                    )
                    .classes("w-full font-mono text-sm")
                    .props("rows=15 standout dark")
                )

            # Right Column: Live Schematic Visualization
            with (
                ui.column().classes("w-full md:w-[45%]"),
                ui.card().classes("w-full h-full bg-surface rounded-xl p-6 min-h-[400px]"),
            ):
                with ui.row().classes("items-center gap-2 mb-4"):
                    ui.icon("visibility", size="sm").classes("text-primary")
                    ui.label("Live Preview").classes("text-lg font-bold text-fg")

                ui.label("The schematic updates automatically as you type.").classes(
                    "text-xs text-muted mb-4"
                )

                svg_container = ui.html().classes(
                    "w-full flex-grow flex items-center justify-center bg-white rounded-lg p-4"
                )

        # Function to update schematic based on input
        def update_schematic(e=None):
            try:
                js_data = ast.literal_eval(json_input.value)
                circuit = CircuitDefinition.model_validate(js_data)

                # Generate SVG
                svg_content = generate_circuit_svg(circuit)

                # Update UI
                svg_container.content = svg_content
                error_label.classes(add="hidden", remove="block")

                # Sync title
                if circuit.name:
                    title_label.text = (
                        f"Edit Schema: {circuit.name}"
                        if circuit_record
                        else f"New Schema: {circuit.name}"
                    )

            except Exception as e:
                error_label.text = f"Error Parsing Definition: {e!s}"
                error_label.classes(add="block", remove="hidden")
                svg_container.content = (
                    "<div class='text-gray-400'>Invalid Circuit Definition</div>"
                )

        # Update it once on load
        update_schematic()

        # Trigger on change
        json_input.on_value_change(update_schematic)

    app_shell(content)()
