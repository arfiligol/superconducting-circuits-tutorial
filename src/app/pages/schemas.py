"""Schema management page - List and manage circuit schemas."""

from __future__ import annotations

from nicegui import ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work


@ui.page("/schemas")
def schemas_page():
    def content():
        with ui.row().classes("w-full justify-between items-center mb-6"):
            with ui.column().classes("gap-1"):
                ui.label("Circuit Schemas").classes("text-2xl font-bold text-fg")
                ui.label("Manage your superconducting circuit designs").classes(
                    "text-sm text-muted"
                )

            ui.button(
                "New Circuit", icon="add", on_click=lambda: ui.navigate.to("/schemas/new")
            ).props("color=primary")

        @ui.refreshable
        def render_list():
            try:
                with get_unit_of_work() as uow:
                    circuits = uow.circuits.list_all()
            except Exception as e:
                ui.label(f"Database Error: {e}").classes("text-danger")
                return

            if not circuits:
                with ui.column().classes(
                    "w-full p-12 items-center justify-center border-2 border-dashed border-border rounded-xl"
                ):
                    ui.icon("account_tree", size="xl").classes("text-muted mb-4 opacity-50")
                    ui.label("No Circuit Schemas Found").classes("text-xl text-fg font-bold")
                    ui.label("Create a new circuit schema to get started.").classes(
                        "text-sm text-muted mt-2"
                    )
                return

            with ui.row().classes("w-full flex-wrap gap-4"):
                for circuit in circuits:
                    with ui.card().classes(
                        "w-full md:w-[calc(50%-1rem)] xl:w-[calc(33%-1rem)] bg-surface p-4"
                    ):
                        with ui.row().classes("w-full justify-between items-start mb-2"):
                            ui.label(circuit.name).classes("font-bold text-lg text-fg truncate")

                            def delete_handler(c=circuit):
                                with get_unit_of_work() as uow:
                                    uow.circuits.delete(c.id)
                                    uow.commit()
                                ui.notify(f"Deleted {c.name}", type="info")
                                render_list.refresh()

                            with ui.row().classes("gap-2"):
                                ui.button(
                                    icon="edit",
                                    on_click=lambda c=circuit: ui.navigate.to(f"/schemas/{c.id}"),
                                ).props("flat round size=sm color=primary tooltip='Edit Schema'")
                                ui.button(icon="delete", on_click=delete_handler).props(
                                    "flat round size=sm color=negative tooltip='Delete Schema'"
                                )

                        ui.label(
                            f"Created: {circuit.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                        ).classes("text-xs text-muted")

        render_list()

    app_shell(content)()
