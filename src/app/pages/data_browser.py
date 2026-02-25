"""Data Browser MVP page for SC Data Browser."""

from typing import Any

import plotly.graph_objects as go
from nicegui import ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work
from core.shared.visualization.figure_builders import (
    build_heatmap,
    build_line_chart,
    build_parameter_table,
)


def _get_badge_class(data_type: str) -> str:
    """Return styling class based on data type."""
    data_type = data_type.lower()
    if data_type.startswith("y_"):
        return "app-badge app-badge-y"
    if data_type.startswith("s_"):
        return "app-badge app-badge-s"
    if data_type.startswith("z_"):
        return "app-badge app-badge-z"
    return "app-badge app-badge-other"


def fetch_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fetch structured data for the UI."""
    try:
        with get_unit_of_work() as uow:
            datasets = uow.datasets.list_all()
            records = uow.data_records.list_all()

            # Map for quick lookup
            ds_map = {ds.id: ds.name for ds in datasets}

            # Formulate row data for AG Grid
            row_data = []
            for r in records:
                row_data.append(
                    {
                        "id": r.id,
                        "dataset_id": r.dataset_id,
                        "dataset_name": ds_map.get(r.dataset_id, "Unknown"),
                        "data_type": r.data_type,
                        "parameter": r.parameter,
                        "representation": r.representation,
                    }
                )

            dataset_options = [{"label": ds.name, "value": ds.id} for ds in datasets]
            return row_data, dataset_options
    except Exception as e:
        print(f"Error fetching data: {e}")
        return [], []


@ui.page("/data-browser")
def data_browser_page():
    # State
    all_records, dataset_options = fetch_data()
    selected_record_id: int | None = None

    # Declare container references before defining content so callbacks can use them
    plot_container: ui.column | None = None
    param_container: ui.column | None = None

    def render_plot():
        nonlocal plot_container, param_container
        if plot_container is None or param_container is None:
            return

        plot_container.clear()
        param_container.clear()

        if not selected_record_id:
            with plot_container:
                ui.label("Select a record to view visualization.").classes("text-muted")
            with param_container:
                ui.label("Waiting for data...").classes("text-muted")
            return

        try:
            with get_unit_of_work() as uow:
                record = uow.data_records.get(selected_record_id)
                if not record:
                    with plot_container:
                        ui.label("Record not found.").classes("text-danger")
                    return

                # 1. Render Chart
                if len(record.axes) == 2 and record.data_type == "s_params":
                    fig = build_heatmap(record, dark=ui.dark_mode().value)
                else:
                    fig = build_line_chart(record, dark=ui.dark_mode().value)

                with plot_container:
                    ui.plotly(fig).classes("w-full h-full").style("min-height: 400px;")

                # 2. Render Derived Parameters
                params = uow.derived_params.list_by_dataset(record.dataset_id)
                if params:
                    param_fig = build_parameter_table(params, dark=ui.dark_mode().value)
                    with param_container:
                        ui.plotly(param_fig).classes("w-full h-full").style("min-height: 200px;")
                else:
                    with param_container:
                        ui.label("No derived parameters for this dataset.").classes(
                            "text-muted p-4"
                        )

        except Exception as e:
            with plot_container:
                ui.label(f"Error rendering plot: {e}").classes("text-danger p-4")

    def content():
        nonlocal plot_container, param_container

        ui.label("Data Browser Explorer").classes("text-2xl font-bold text-fg mb-4")

        columns = [
            {"name": "id", "label": "ID", "field": "id", "sortable": True},
            {"name": "dataset", "label": "Dataset", "field": "dataset_name", "sortable": True},
            {"name": "type", "label": "Type", "field": "data_type", "sortable": True},
            {"name": "param", "label": "Param", "field": "parameter", "sortable": True},
            {"name": "repr", "label": "Repr", "field": "representation", "sortable": True},
        ]

        with ui.row().classes("w-full h-full gap-4 flex-wrap lg:flex-nowrap"):
            # Master: Table
            with ui.column().classes("app-card w-full lg:w-[45%] p-3 flex flex-col"):
                ui.label("Data Records").classes("app-section-title mb-2")
                ui.label("Select a record to preview data.").classes("text-xs text-muted mb-2")

                # table instance
                grid = (
                    ui.table(columns=columns, rows=all_records, row_key="id")
                    .classes("w-full flex-grow min-h-[500px] cursor-pointer")
                    .props("dense")
                )

                def handle_row_click(e):
                    nonlocal selected_record_id
                    selected_record_id = int(e.args[1]["id"])
                    render_plot()

                grid.on("rowClick", handle_row_click)

            # Detail: Charts and Params
            with ui.column().classes("w-full lg:w-[55%] flex flex-col gap-4"):
                # Chart card
                with ui.column().classes("app-card w-full p-3 flex flex-col"):
                    ui.label("Visualization").classes("app-section-title mb-2")
                    plot_container = ui.column().classes(
                        "app-plotly-container w-full flex-grow min-h-[400px] flex items-center justify-center"
                    )

                # Params card
                with ui.column().classes("app-card w-full p-3 flex flex-col"):
                    ui.label("Derived Parameters").classes("app-section-title mb-2")
                    param_container = ui.column().classes(
                        "app-plotly-container w-full flex-grow min-h-[200px] flex items-center justify-center"
                    )

                # Initial render
                render_plot()

    app_shell(content)()
