"""Main entry point for the SC Data Browser app."""

import os
import sys
from pathlib import Path

from nicegui import app as ui_app
from nicegui import ui

from app.pages import (  # noqa: F401
    characterization,
    dashboard,
    home,
    raw_data,
    schemdraw_live_preview,
    schema_editor,
    schemas,
    simulation,
)
from app.services.browser_tooling import shared_frontend_tooling_head_html

# Register static files for CSS
styles_dir = Path(__file__).parent / "styles"
ui_app.add_static_files("/styles", str(styles_dir))


def start():
    """Launch the NiceGUI application."""
    # NiceGUI reload mode expects execution as a module/script (__main__/__mp_main__).
    # Console-script entry points import this module as `app.main`, so re-exec once.
    if __name__ not in {"__main__", "__mp_main__"}:
        os.execv(sys.executable, [sys.executable, "-m", "app.main"])

    # Inject CSS globally via a head_html string
    # This guarantees the styles are loaded before content renders
    ui.add_head_html(
        (
            """
        <link href="/styles/theme.css" rel="stylesheet">
        <link href="/styles/components.css" rel="stylesheet">
        <style>
            /* NiceGUI Specific overrides to respect root tokens */
            body { background-color: rgb(var(--bg)); color: rgb(var(--fg)); }
        </style>
    """
            + shared_frontend_tooling_head_html()
        ),
        shared=True,
    )

    # Run the app
    # - dark=True: Default to dark mode
    # - show=True: Open browser automatically
    # - port=8080: Standard dev port
    ui.run(
        title="SC Tutorial App",
        port=int(os.getenv("SC_APP_PORT", "8080")),
        dark=True,
        show=False,  # Wait until everything loads cleanly, user can click or we can show later
        reload=True,
        storage_secret="SC_DATA_BROWSER_SECRET",
    )


if __name__ in {"__main__", "__mp_main__"}:
    start()
