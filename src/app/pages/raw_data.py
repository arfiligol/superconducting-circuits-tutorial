"""Raw data route wrapper delegating to the feature package."""

from __future__ import annotations

import importlib

from nicegui import ui

from app.layout import app_shell


def _feature_page():
    return importlib.import_module("app.features.raw_data.page")


def __getattr__(name: str):
    return getattr(_feature_page(), name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_feature_page())))


@ui.page("/raw-data")
def raw_data_page() -> None:
    app_shell(_feature_page().build_page)()
