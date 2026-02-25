"""Central App Layout Shell for NiceGUI Data Browser."""

from nicegui import app, ui


def app_shell(content_builder):
    """
    App shell wrapper that provides the consistent header, drawer, and style.
    Can be used as a decorator or a function call.
    """
    # Load foundational CSS
    ui.add_css(
        """
        /* Temporary loading of our custom CSS using add_head_html is more robust 
           for dynamic reloading, but ui.add_css works for direct raw CSS strings. 
           We'll link the path using app.add_static_files */
    """,
        shared=True,
    )

    def wrapper(*args, **kwargs):
        # Global body setup (Dark mode handled globally in ui.run(dark=True))
        ui.query("body").classes("bg-bg text-fg")

        # App Header
        with ui.header(elevated=False).classes(
            "bg-surface text-fg border-b border-border h-16 flex items-center px-4"
        ):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props("flat").classes(
                "text-fg"
            )
            ui.label("🔬 SC Data Browser").classes("text-xl font-semibold ml-2 text-fg")
            ui.space()
            # Theme toggle placeholder - assuming dark mode default
            # NiceGUI dark mode toggle is native
            ui.button(icon="dark_mode", on_click=lambda: ui.dark_mode().toggle()).props(
                "flat round tooltip='Toggle Dark Mode'"
            ).classes("text-fg")

        # Navigation Drawer
        with (
            ui.left_drawer(elevated=False)
            .classes("bg-surface text-fg flex flex-col pt-4 gap-2")
            .props("width=220") as left_drawer
        ):
            with ui.column().classes("w-full px-1"):
                ui.label("NAVIGATION").classes(
                    "text-xs text-muted font-bold tracking-wider mb-1 px-2"
                )
                ui.button("Home", icon="home", on_click=lambda: ui.navigate.to("/")).classes(
                    "w-full justify-start"
                ).props("flat no-caps dense")
                ui.button(
                    "Data Browser",
                    icon="analytics",
                    on_click=lambda: ui.navigate.to("/data-browser"),
                ).classes("w-full justify-start").props("flat no-caps dense")

                ui.separator().classes("my-4 bg-border")

                ui.label("TOOLS").classes("text-xs text-muted font-bold tracking-wider mb-1 px-2")
                ui.button("Analysis", icon="functions").classes("w-full justify-start").props(
                    "flat no-caps dense disable"
                )
                ui.button("Simulation", icon="science").classes("w-full justify-start").props(
                    "flat no-caps dense disable"
                )

        # Main Content Area
        with ui.column().classes("w-full max-w-7xl mx-auto px-4 py-3 gap-4"):
            content_builder(*args, **kwargs)

    return wrapper
