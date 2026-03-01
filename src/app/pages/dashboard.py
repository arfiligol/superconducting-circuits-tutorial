"""Dashboard page to view vital tagged metrics across datasets."""

from nicegui import app, ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import DerivedParameter, ParameterDesignation


@ui.page("/dashboard")
def dashboard_page():
    def content():
        ui.label("Dashboard").classes("text-2xl font-bold text-fg mb-6")

        selected_dataset_ids = app.storage.user.get("selected_datasets", [])

        if not selected_dataset_ids:
            with ui.column().classes(
                "w-full p-12 items-center justify-center border-2 border-dashed border-border rounded-xl"
            ):
                ui.icon("dashboard", size="xl").classes("text-muted mb-4 opacity-50")
                ui.label("No Datasets Selected").classes("text-xl text-fg font-bold")
                ui.label("Select active datasets from the Raw Data page.").classes(
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

                # --- Layout: Header + Dataset Selector ---
                with ui.row().classes("w-full items-center gap-4 mb-4"):
                    ui.label("Dataset:").classes("text-sm font-bold text-fg")

                    # We can use the same state variable or a new one
                    current_ds_id = app.storage.user.get("dashboard_current_dataset")
                    if current_ds_id not in ds_options:
                        current_ds_id = list(ds_options.keys())[0]
                        app.storage.user["dashboard_current_dataset"] = current_ds_id

                    def on_change(e):
                        app.storage.user["dashboard_current_dataset"] = e.value
                        render_dashboard.refresh()

                    ui.select(options=ds_options, value=current_ds_id, on_change=on_change).props(
                        "dense outlined options-dense"
                    ).classes("w-64")

                # --- Layout: Main Body ---
                @ui.refreshable
                def render_dashboard():
                    active_id = app.storage.user.get("dashboard_current_dataset")
                    if not active_id or active_id not in ds_options:
                        return

                    designations = (
                        uow._session.query(ParameterDesignation)
                        .filter_by(dataset_id=active_id)
                        .all()
                    )

                    if not designations:
                        with ui.column().classes(
                            "w-full p-8 mt-4 items-center justify-center bg-bg rounded-xl border border-border"
                        ):
                            ui.icon("sell", size="lg").classes("text-muted opacity-40 mb-2")
                            ui.label("No Metrics Tagged").classes("text-lg font-bold text-muted")
                            ui.label(
                                "Use the Identify Mode tool in the Characterization page to tag key parameters."
                            ).classes("text-sm text-muted")
                        return

                    ui.label("Tagged Core Metrics").classes(
                        "text-xs font-bold text-muted tracking-widest uppercase mb-4 mt-6"
                    )
                    with ui.row().classes("w-full gap-4 flex-wrap"):
                        for desig in designations:
                            resolved_param = (
                                uow._session.query(DerivedParameter)
                                .filter_by(
                                    dataset_id=active_id,
                                    method=desig.source_analysis_type,
                                    name=desig.source_parameter_name,
                                )
                                .first()
                            )

                            # If exact match fails, it might be a bias-swept parameter,
                            # so try finding the value for the first bias slice (_b0)
                            if not resolved_param:
                                resolved_param = (
                                    uow._session.query(DerivedParameter)
                                    .filter_by(
                                        dataset_id=active_id,
                                        method=desig.source_analysis_type,
                                        name=f"{desig.source_parameter_name}_b0",
                                    )
                                    .first()
                                )

                            # If still not found, try a LIKE query as a final fallback
                            if not resolved_param:
                                resolved_param = (
                                    uow._session.query(DerivedParameter)
                                    .filter(
                                        DerivedParameter.dataset_id == active_id,
                                        DerivedParameter.method == desig.source_analysis_type,
                                        DerivedParameter.name.like(
                                            f"{desig.source_parameter_name}%"
                                        ),
                                    )
                                    .first()
                                )

                            with ui.column().classes(
                                "app-card p-6 min-w-[240px] flex-grow flex-shrink bg-surface border border-border rounded-xl hover:border-primary transition-colors"
                            ):
                                with ui.row().classes("w-full items-center justify-between mb-2"):
                                    ui.label(desig.designated_name).classes(
                                        "text-lg text-primary font-bold"
                                    )
                                    ui.icon("sell", size="sm").classes("text-primary opacity-80")

                                if resolved_param:
                                    val = (
                                        f"{resolved_param.value:.4g}"
                                        if isinstance(resolved_param.value, float)
                                        else str(resolved_param.value)
                                    )
                                    unit = resolved_param.unit or ""
                                    with ui.row().classes("items-baseline gap-1"):
                                        ui.label(val).classes("text-3xl font-bold text-fg")
                                        if unit:
                                            ui.label(unit).classes("text-base text-muted")
                                    ui.label(f"Source: {desig.source_analysis_type}").classes(
                                        "text-xs text-muted mt-4 uppercase tracking-wider"
                                    )
                                else:
                                    ui.label("Value not found").classes(
                                        "text-sm text-warning italic mt-1"
                                    )
                                    ui.label(f"Expected: {desig.source_parameter_name}").classes(
                                        "text-xs text-muted"
                                    )

                render_dashboard()

        except Exception as e:
            ui.label(f"Error loading dashboard: {e}").classes("text-danger")

    app_shell(content)()
