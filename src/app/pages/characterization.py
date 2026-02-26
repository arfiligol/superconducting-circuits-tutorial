"""Analysis Dashboard page for SC Data Browser."""

from typing import Any

from nicegui import app, ui

from app.layout import app_shell
from app.services.analysis_registry import (
    ANALYSIS_REGISTRY,
    get_available_analyses,
    is_analysis_completed,
)
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.persistence import get_unit_of_work


@ui.page("/characterization")
def characterization_page():
    def render_analysis_card(
        dataset,
        analysis: dict[str, Any],
        available_analyses: list[dict[str, Any]],
        completed: bool = False,
    ):
        is_available = any(a["id"] == analysis["id"] for a in available_analyses)

        with ui.column().classes("app-card w-full max-w-sm flex flex-col p-6 gap-2"):
            with ui.row().classes("w-full items-center gap-2 mb-2"):
                ui.icon(analysis["icon"], size="sm").classes("text-primary")
                ui.label(analysis["label"]).classes("text-lg font-bold text-fg")

            ui.label(analysis["description"]).classes("text-sm text-muted mb-4 flex-grow")

            if not is_available:
                ui.label("🚫 Missing required records for this analysis.").classes(
                    "text-xs text-danger mt-auto font-semibold"
                )
                return

            if completed:
                with ui.row().classes("items-center gap-1 mb-2"):
                    ui.icon("check_circle", size="xs").classes("text-positive")
                    ui.label("Completed").classes("text-xs text-positive font-bold")
                button_text = "🔁 Re-run Fit"
            else:
                button_text = "▶ Run Fit"

            # Render configuration form
            form_inputs = {}
            for field in analysis.get("config_fields", []):
                if field["type"] == "select":
                    form_inputs[field["name"]] = (
                        ui.select(
                            options=field["options"],
                            value=field.get("default"),
                            label=field["label"],
                        )
                        .classes("w-full")
                        .props("dense outline")
                    )
                elif field["type"] == "number":
                    form_inputs[field["name"]] = (
                        ui.number(label=field["label"], value=field.get("default"))
                        .classes("w-full")
                        .props("dense outline")
                    )

            async def do_run():
                # Collect parameter values
                params = {k: v.value for k, v in form_inputs.items()}
                ds_name = dataset.name if dataset else "Cross-Dataset"

                try:
                    ui.notify(f"Starting {analysis['label']} on {ds_name}...", type="info")

                    if analysis["id"] == "admittance_extraction":
                        service = ResonanceExtractService()
                        service.extract_admittance(str(dataset.id))
                        ui.notify(
                            f"Admittance Extraction complete for {ds_name}.",
                            type="positive",
                            position="top",
                        )

                    elif analysis["id"] == "s21_resonance_fit":
                        service = ResonanceFitService()
                        # Default to S21 for this prototype;
                        # future improvements should read the specific parameter selected or found
                        service.perform_fit(
                            dataset_identifier=str(dataset.id),
                            parameter="S21",
                            model=params.get("model", "notch"),
                            resonators=int(params.get("resonators", 1) or 1),
                            f_min=params.get("f_min"),
                            f_max=params.get("f_max"),
                        )
                        ui.notify(
                            f"S21 Fit complete for {ds_name}.", type="positive", position="top"
                        )

                    elif analysis["id"] == "squid_fitting":
                        ui.notify(
                            "SQUID Fitting service logic stubbed.", type="warning", position="top"
                        )

                    elif analysis["id"] == "y11_fit":
                        ui.notify(
                            "Y11 Fitting service logic stubbed.", type="warning", position="top"
                        )

                    else:
                        ui.notify(f"Generic run triggered for {analysis['label']}.", type="info")

                except Exception as e:
                    ui.notify(f"Analysis failed: {e!s}", type="negative", position="top")

            ui.button(button_text, on_click=do_run).props("unelevated color=primary").classes(
                "w-full mt-4"
            )

    def content():
        ui.label("Characterization").classes("text-2xl font-bold text-fg mb-6")

        selected_dataset_ids = app.storage.user.get("selected_datasets", [])

        if not selected_dataset_ids:
            with ui.column().classes(
                "w-full p-12 items-center justify-center bg-transparent border-2 border-dashed border-border rounded-xl"
            ):
                ui.icon("science", size="xl").classes("text-muted mb-4 opacity-50")
                ui.label("No Datasets Selected").classes("text-xl text-fg font-bold")
                ui.label(
                    "Please select active datasets from the top header or the Raw Data page."
                ).classes("text-sm text-muted mt-2")
            return

        try:
            with get_unit_of_work() as uow:
                # 1. Build dictionary of available datasets from context
                ds_options = {}
                for ds_id in selected_dataset_ids:
                    ds = uow.datasets.get(ds_id)
                    if ds:
                        ds_options[ds_id] = ds.name

                if not ds_options:
                    ui.label("Error: Active datasets not found in database.").classes("text-danger")
                    return

                # 2. Reconcile current selection state
                current_ds_id = app.storage.user.get("analysis_current_dataset")
                if current_ds_id not in ds_options:
                    current_ds_id = list(ds_options.keys())[0]
                    app.storage.user["analysis_current_dataset"] = current_ds_id

                @ui.refreshable
                def render_single_dataset_analyses():
                    active_id = app.storage.user.get("analysis_current_dataset")
                    if not active_id or active_id not in ds_options:
                        return

                    ds = uow.datasets.get(active_id)
                    if not ds:
                        return

                    records = [
                        {
                            "data_type": r.data_type,
                            "parameter": r.parameter,
                            "representation": r.representation,
                        }
                        for r in uow.data_records.list_all()
                        if r.dataset_id == active_id
                    ]

                    available = get_available_analyses(records)
                    ds_params = uow.derived_params.list_by_dataset(active_id)

                    with ui.column().classes("w-full mb-8"):
                        with ui.row().classes("w-full items-center gap-4 mb-4"):
                            ui.label("Dataset:").classes("text-sm font-bold text-fg")

                            def on_change(e):
                                app.storage.user["analysis_current_dataset"] = e.value
                                render_single_dataset_analyses.refresh()

                            ui.select(
                                options=ds_options, value=active_id, on_change=on_change
                            ).props("dense outline dark standout").classes("w-64")

                        with ui.row().classes("w-full gap-6 flex-wrap lg:flex-nowrap"):
                            for analysis in ANALYSIS_REGISTRY:
                                if analysis["scope"] == "per_dataset":
                                    is_completed = is_analysis_completed(analysis, ds_params)
                                    render_analysis_card(ds, analysis, available, is_completed)

                # --- Layout rendering ---

                # Per-Dataset section
                ui.label("Per-Dataset Analyses").classes(
                    "text-xs font-bold text-muted tracking-widest uppercase mb-4"
                )
                render_single_dataset_analyses()

                # Cross-Dataset section
                if len(selected_dataset_ids) >= 2:
                    ui.separator().classes("my-8 bg-border")
                    ui.label("Cross-Dataset Analyses").classes(
                        "text-xs font-bold text-muted tracking-widest uppercase mb-4"
                    )
                    with ui.row().classes("w-full gap-6 flex-wrap lg:flex-nowrap"):
                        for analysis in ANALYSIS_REGISTRY:
                            if analysis["scope"] == "cross_dataset":
                                render_analysis_card(None, analysis, [analysis])

        except Exception as e:
            ui.label(f"Error loading analysis info: {e}").classes("text-danger")

    app_shell(content)()
