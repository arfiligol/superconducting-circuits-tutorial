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
        /* Temporary loading of our custom CSS */
        .nicegui-content {
            max-width: 100% !important;
            width: 100% !important;
            padding: 0 !important;
        }
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
                    "text-xs text-muted font-bold tracking-wider mb-1 px-4"
                )

                def nav_btn(label: str, icon_name: str, route: str, disabled: bool = False):
                    with (
                        ui.button(
                            on_click=lambda r=route: ui.navigate.to(r) if not disabled else None
                        )
                        .classes("w-full px-4")
                        .props(f"flat no-caps dense {'disable' if disabled else ''}")
                    ):
                        with ui.row().classes("items-center no-wrap w-full"):
                            with ui.row().classes("w-8 justify-start"):
                                ui.icon(icon_name, size="sm")
                            ui.label(label).classes("text-sm")

                nav_btn("Home", "home", "/")
                nav_btn("Data Browser", "analytics", "/data-browser")

                ui.separator().classes("my-4 mx-4 bg-border")

                ui.label("TOOLS").classes("text-xs text-muted font-bold tracking-wider mb-1 px-4")
                nav_btn("Analysis", "functions", "", disabled=True)
                nav_btn("Simulation", "science", "", disabled=True)

        # Main Content Area
        with ui.column().classes("w-full p-4 md:p-8 gap-6"):
            content_builder(*args, **kwargs)

    return wrapper
