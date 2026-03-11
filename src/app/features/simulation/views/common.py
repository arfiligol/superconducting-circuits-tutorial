"""Shared view helpers for simulation feature modules."""

from __future__ import annotations

from typing import Any

from nicegui import app

_Z0_CONTROL_PROPS = "dense outlined"
_Z0_CONTROL_CLASSES = "w-32"


def _with_test_id(element: Any, test_id: str) -> Any:
    """Attach one stable test id to a NiceGUI element."""
    try:
        element.props(f"data-testid={test_id}")
    except Exception:
        props = getattr(element, "_props", None)
        if isinstance(props, dict):
            props["data-testid"] = test_id
    return element


def _user_storage_get(key: str, default: Any = None) -> Any:
    """Safely read one value from user storage with non-UI-context fallback."""
    try:
        return app.storage.user.get(key, default)
    except RuntimeError:
        return default


def _user_storage_set(key: str, value: Any) -> None:
    """Safely write one value into user storage when UI context is available."""
    try:
        app.storage.user[key] = value
    except RuntimeError:
        return
