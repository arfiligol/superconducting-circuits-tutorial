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

        # Refreshable content area — re-renders when Active Datasets change
        @ui.refreshable
        def content_area():
            content_builder(*args, **kwargs)

        # App Header
        with ui.header(elevated=False).classes(
            "bg-surface text-fg border-b border-border h-16 flex items-center px-4"
        ):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props("flat").classes(
                "text-fg"
            )
            ui.label("🔬 SC Tutorial App").classes("text-xl font-semibold ml-2 text-fg truncate")

            # Dataset Context Selector
            from core.shared.persistence import get_unit_of_work

            def fetch_dataset_options():
                try:
                    with get_unit_of_work() as uow:
                        datasets = uow.datasets.list_all()
                        return {ds.id: ds.name for ds in datasets}
                except Exception:
                    return {}

            def on_dataset_change(_):
                content_area.refresh()

            with ui.row().classes("flex-grow mx-4 items-center justify-center max-w-2xl"):
                ui.select(
                    options=fetch_dataset_options(),
                    multiple=True,
                    with_input=True,
                    clearable=True,
                    label="Active Datasets",
                    on_change=on_dataset_change,
                ).classes("w-full").bind_value(app.storage.user, "selected_datasets").props(
                    "use-chips dense dark standout"
                )

            ui.space()

            # Dark mode state management — syncs with global app storage & client-side Plotly
            if "dark_mode" not in app.storage.user or app.storage.user["dark_mode"] is None:
                app.storage.user["dark_mode"] = True

            dark = ui.dark_mode().bind_value(app.storage.user, "dark_mode")
            ui.button(on_click=dark.toggle).props("flat round tooltip='Toggle Dark Mode'").classes(
                "text-fg"
            ).bind_icon_from(dark, "value", lambda v: "light_mode" if v else "dark_mode")

        # --- Client-side Plotly theme sync via MutationObserver ---
        # Watches Quasar's body.body--dark class and calls Plotly.relayout()
        # on every chart. Zero server round-trips, zero state loss.
        ui.add_head_html(
            """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
          // Use flattened keys for Plotly.relayout to gracefully merge properties
          // rather than completely overwriting the server-generated layout (which wipes titles/legends).
          const DARK_LAYOUT = {
            'paper_bgcolor': 'rgb(30, 41, 59)',
            'plot_bgcolor': 'rgb(15, 23, 42)',
            'font.color': 'rgb(226, 232, 240)',
            'font.family': 'Inter, Arial, sans-serif',
            'xaxis.gridcolor': 'rgb(51, 65, 85)',
            'xaxis.zerolinecolor': 'rgb(51, 65, 85)',
            'yaxis.gridcolor': 'rgb(51, 65, 85)',
            'yaxis.zerolinecolor': 'rgb(51, 65, 85)'
          };
          const LIGHT_LAYOUT = {
            'paper_bgcolor': 'rgb(255, 255, 255)',
            'plot_bgcolor': 'rgb(248, 250, 252)',
            'font.color': 'rgb(15, 23, 42)',
            'font.family': 'Inter, Arial, sans-serif',
            'xaxis.gridcolor': 'rgb(226, 232, 240)',
            'xaxis.zerolinecolor': 'rgb(226, 232, 240)',
            'yaxis.gridcolor': 'rgb(226, 232, 240)',
            'yaxis.zerolinecolor': 'rgb(226, 232, 240)'
          };

          function relayoutAll() {
            requestAnimationFrame(function() {
              const isDark = document.body.classList.contains('body--dark');
              const layoutUpdate = isDark ? DARK_LAYOUT : LIGHT_LAYOUT;
              document.querySelectorAll('.js-plotly-plot').forEach(function(el) {
                if (typeof Plotly !== 'undefined') {
                  Plotly.relayout(el, layoutUpdate);
                }
              });
            });
          }

          // Watch for Quasar dark-mode class toggle on <body>
          const observer = new MutationObserver(function(mutations) {
            for (const m of mutations) {
              if (m.attributeName === 'class') { relayoutAll(); return; }
            }
          });
          observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
        });
        </script>
        """,
            shared=True,
        )

        # Navigation Drawer
        with (
            ui.left_drawer(elevated=False)
            .classes("bg-surface text-fg flex flex-col pt-4 gap-2")
            .props("width=220") as left_drawer,
            ui.column().classes("w-full px-1"),
        ):

            def nav_btn(label: str, icon_name: str, route: str, disabled: bool = False):
                with (
                    ui.button(on_click=lambda r=route: ui.navigate.to(r) if not disabled else None)
                    .classes("w-full px-4")
                    .props(f"flat no-caps dense {'disable' if disabled else ''}")
                ):
                    with ui.row().classes("items-center no-wrap w-full"):
                        with ui.row().classes("w-8 justify-start"):
                            ui.icon(icon_name, size="sm")
                        ui.label(label).classes("text-sm")

            ui.label("DASHBOARD").classes("text-xs text-muted font-bold tracking-wider mb-1 px-4")
            nav_btn("Home", "home", "/")

            ui.separator().classes("my-4 mx-4 bg-border")

            ui.label("DATA").classes("text-xs text-muted font-bold tracking-wider mb-1 px-4")
            nav_btn("Raw Data", "folder_zip", "/raw-data")
            nav_btn("Analysis", "functions", "/analysis")
            nav_btn("Derived Results", "list_alt", "/results")

            ui.separator().classes("my-4 mx-4 bg-border")

            ui.label("TOOLS").classes("text-xs text-muted font-bold tracking-wider mb-1 px-4")
            nav_btn("Simulation", "science", "/simulation", disabled=True)

        # Main Content Area
        with ui.column().classes("w-full p-4 md:p-8 gap-6"):
            content_area()

    return wrapper
