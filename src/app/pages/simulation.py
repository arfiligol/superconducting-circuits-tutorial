"""Simulation page - Circuit visualization and analysis."""

from __future__ import annotations

import ast
from datetime import datetime

import plotly.graph_objects as go
from nicegui import app, run, ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord, DataRecord, DatasetRecord
from core.simulation.application.circuit_visualizer import generate_circuit_svg
from core.simulation.application.run_simulation import run_simulation
from core.simulation.domain.circuit import CircuitDefinition, FrequencyRange, SimulationResult


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
                "w-full p-12 items-center justify-center border-2 border-dashed border-border rounded-xl"
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
            js_data = ast.literal_eval(active_record.definition_json)
            circuit_def = CircuitDefinition.model_validate(js_data)
            svg_content = generate_circuit_svg(circuit_def)
        except Exception as e:
            svg_content = f"<div class='text-danger p-4'>Error parsing selected schema: {e}</div>"

        # --- Two Columns ---
        with ui.row().classes("w-full gap-6"):
            # Left: Visualize and Params
            with ui.column().classes("w-full md:w-1/2 gap-4"):
                with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                    with ui.row().classes("items-center gap-2 mb-4"):
                        ui.icon("visibility", size="sm").classes("text-primary")
                        ui.label("Schematic").classes("text-lg font-bold text-fg")
                    ui.html(svg_content).classes(
                        "w-full min-h-[250px] flex items-center justify-center bg-white rounded-lg p-4"
                    )

                with ui.card().classes("w-full bg-surface rounded-xl p-6"):
                    with ui.row().classes("items-center gap-2 mb-4"):
                        ui.icon("settings", size="sm").classes("text-primary")
                        ui.label("Simulation Setup").classes("text-lg font-bold text-fg")

                    with ui.row().classes("w-full gap-4"):
                        start_input = ui.number("Start Freq (GHz)", value=1.0).classes("flex-grow")
                        stop_input = ui.number("Stop Freq (GHz)", value=10.0).classes("flex-grow")
                        points_input = ui.number("Points", value=1001, format="%.0f").classes(
                            "flex-grow"
                        )

                    async def run_sim():
                        try:
                            # Basic validation
                            if (
                                not start_input.value
                                or not stop_input.value
                                or not points_input.value
                            ):
                                ui.notify("Please fill all simulation parameters", type="warning")
                                return

                            freq_range = FrequencyRange(
                                start_ghz=start_input.value,
                                stop_ghz=stop_input.value,
                                points=int(points_input.value),
                            )

                            # Show loading state
                            sim_button.props("loading")
                            results_container.clear()
                            with results_container:
                                ui.spinner(size="3em").classes("text-primary")
                                ui.label("Running Simulation...").classes("text-muted mt-2")

                            try:
                                # Run Julia simulation in a process to prevent GIL blocking
                                result = await run.cpu_bound(
                                    run_simulation, circuit_def, freq_range
                                )
                            except ImportError as e:
                                results_container.clear()
                                with results_container:
                                    ui.label(str(e)).classes("text-danger")
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

                            fig.update_layout(
                                title="S11 Magnitude Response",
                                xaxis_title="Frequency (GHz)",
                                yaxis_title="Magnitude (linear)",
                                margin=dict(l=40, r=20, t=40, b=40),
                                showlegend=True,
                                hovermode="x unified",
                            )

                            def on_save_click():
                                _save_simulation_results_dialog(
                                    active_record, last_freq_range, last_sim_result
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
                            results_container.clear()
                            with results_container:
                                ui.label(f"Simulation Error: {e}").classes("text-danger")
                        finally:
                            sim_button.props(remove="loading")

                    sim_button = (
                        ui.button("Run Simulation", on_click=run_sim, icon="play_arrow")
                        .props("color=primary")
                        .classes("w-full mt-4")
                    )

            # Right: Results
            with (
                ui.column().classes("w-full md:w-[45%] h-full min-h-[400px]"),
                ui.card()
                .classes("w-full h-full bg-surface rounded-xl p-6")
                .style("min-height: 400px;"),
            ):
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
