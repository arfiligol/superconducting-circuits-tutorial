"""Data Browser MVP page for SC Data Browser."""

from typing import Any

from nicegui import app, ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work
from core.shared.visualization.figure_builders import (
    build_heatmap,
    build_line_chart,
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


def fetch_datasets() -> list[dict[str, Any]]:
    try:
        with get_unit_of_work() as uow:
            datasets = uow.datasets.list_all()
            return [{"id": ds.id, "name": ds.name} for ds in datasets]
    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return []


def fetch_records_for_dataset(dataset_id: int) -> list[dict[str, Any]]:
    try:
        with get_unit_of_work() as uow:
            records = uow.data_records.list_all()
            return [
                {
                    "id": r.id,
                    "dataset_id": r.dataset_id,
                    "data_type": r.data_type,
                    "parameter": r.parameter,
                    "representation": r.representation,
                }
                for r in records
                if r.dataset_id == dataset_id
            ]
    except Exception as e:
        print(f"Error fetching records: {e}")
        return []


@ui.page("/raw-data")
def raw_data_page():
    # State
    all_datasets = fetch_datasets()
    selected_dataset_id: int | None = None
    selected_record_id: int | None = None

    # Containers
    detail_container: ui.column | None = None
    plot_container: ui.column | None = None
    records_grid = None

    def handle_analyze_click():
        if selected_dataset_id:
            # Add to global context if not already there
            current_selection = app.storage.user.get("selected_datasets", [])
            if selected_dataset_id not in current_selection:
                current_selection.append(selected_dataset_id)
                app.storage.user["selected_datasets"] = current_selection

            ui.navigate.to("/characterization")

    def render_plot():
        if plot_container is None:
            return
        plot_container.clear()

        if not selected_record_id:
            with plot_container:
                ui.label("Select a record from the table to view visualization.").classes(
                    "text-muted p-4"
                )
            return

        try:
            with get_unit_of_work() as uow:
                record = uow.data_records.get(selected_record_id)
                if not record:
                    with plot_container:
                        ui.label("Record not found.").classes("text-danger")
                    return

                # Render Chart
                if len(record.axes) == 2 and record.data_type == "s_params":
                    fig = build_heatmap(record, dark=ui.dark_mode().value)
                else:
                    fig = build_line_chart(record, dark=ui.dark_mode().value)

                with plot_container:
                    ui.plotly(fig).classes("w-full h-full").style("min-height: 400px;")

        except Exception as e:
            with plot_container:
                ui.label(f"Error rendering plot: {e}").classes("text-danger p-4")

    def render_dataset_detail():
        if detail_container is None:
            return
        detail_container.clear()

        if not selected_dataset_id:
            with detail_container:
                ui.label("Select a dataset from the list to preview.").classes(
                    "text-muted italic text-center w-full mt-10"
                )
            return

        ds = next((d for d in all_datasets if d["id"] == selected_dataset_id), None)
        if not ds:
            return

        records = fetch_records_for_dataset(selected_dataset_id)

        with detail_container:
            with ui.row().classes("w-full justify-between items-center mb-4"):
                with ui.column().classes("gap-1"):
                    ui.label(ds["name"]).classes("text-xl font-bold text-fg")
                    ui.label(
                        f"{len(records)} records available." if records else "No records available."
                    ).classes("text-sm text-muted")

                ui.button(
                    "Analyze This Dataset", on_click=handle_analyze_click, icon="science"
                ).props("unelevated color=primary")

            # Records Table
            record_columns = [
                {
                    "name": "id",
                    "label": "ID",
                    "field": "id",
                    "sortable": True,
                    "align": "center",
                    "style": "width: 60px",
                },
                {
                    "name": "type",
                    "label": "Type",
                    "field": "data_type",
                    "sortable": True,
                    "align": "center",
                },
                {
                    "name": "param",
                    "label": "Param",
                    "field": "parameter",
                    "sortable": True,
                    "align": "center",
                },
                {
                    "name": "repr",
                    "label": "Repr",
                    "field": "representation",
                    "sortable": True,
                    "align": "center",
                },
            ]

            nonlocal records_grid
            records_grid = (
                ui.table(columns=record_columns, rows=records, row_key="id")
                .classes("w-full cursor-pointer mb-6")
                .props("dense")
            )

            def handle_record_click(e):
                nonlocal selected_record_id
                selected_record_id = int(e.args[1]["id"])
                render_plot()

            records_grid.on("rowClick", handle_record_click)

            # Plot Container
            ui.label("Visualization Preview").classes(
                "text-sm font-semibold text-muted tracking-wider mb-2 uppercase"
            )
            nonlocal plot_container
            plot_container = ui.column().classes(
                "w-full flex-grow app-plotly-container min-h-[400px] "
                "flex items-center justify-center"
            )
            render_plot()

    def content():
        nonlocal detail_container

        ui.label("Raw Data Browser").classes("text-2xl font-bold text-fg mb-4")

        with ui.row().classes("w-full h-full gap-6 flex-wrap lg:flex-nowrap items-stretch"):
            # Master: Dataset List
            with ui.column().classes("app-card w-full lg:w-[35%] p-4 flex flex-col"):
                ui.label("Datasets").classes("app-section-title mb-4")

                dataset_columns = [
                    {
                        "name": "name",
                        "label": "Name",
                        "field": "name",
                        "sortable": True,
                        "align": "left",
                    }
                ]

                ds_grid = (
                    ui.table(columns=dataset_columns, rows=all_datasets, row_key="id")
                    .classes("w-full flex-grow cursor-pointer")
                    .props("dense hide-header")
                )

                def handle_ds_click(e):
                    nonlocal selected_dataset_id, selected_record_id
                    selected_dataset_id = int(e.args[1]["id"])
                    selected_record_id = None  # Reset selected record on ds change
                    render_dataset_detail()

                ds_grid.on("rowClick", handle_ds_click)

            # Detail: Dataset Content (Records + Preview)
            with ui.column().classes("app-card w-full lg:w-[65%] p-6 flex flex-col"):
                detail_container = ui.column().classes("w-full flex-grow")
                render_dataset_detail()

    app_shell(content)()
