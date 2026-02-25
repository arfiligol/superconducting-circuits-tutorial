"""Main entry point for the SC Data Browser app."""

from pathlib import Path

from nicegui import app, ui

# Register static files for CSS
styles_dir = Path(__file__).parent / "styles"
app.add_static_files("/styles", str(styles_dir))

# Import pages to register route decorators
import app.pages.data_browser  # noqa: F401
import app.pages.home  # noqa: F401


def start():
    """Launch the NiceGUI application."""

    # Inject CSS globally via a head_html string
    # This guarantees the styles are loaded before content renders
    ui.add_head_html(
        """
        <link href="/styles/theme.css" rel="stylesheet">
        <link href="/styles/components.css" rel="stylesheet">
        <style>
            /* NiceGUI Specific overrides to respect root tokens */
            body { background-color: rgb(var(--bg)); color: rgb(var(--fg)); }
        </style>
    """,
        shared=True,
    )

    # Run the app
    # - dark=True: Default to dark mode
    # - show=True: Open browser automatically
    # - port=8080: Standard dev port
    ui.run(
        title="SC Data Browser",
        port=8080,
        dark=True,
        show=False,  # Wait until everything loads cleanly, user can click or we can show later
        reload=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    start()
