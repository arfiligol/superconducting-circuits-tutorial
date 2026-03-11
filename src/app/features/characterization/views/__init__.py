"""Characterization view helpers."""

from __future__ import annotations

from typing import Any


def _with_test_id(element: Any, test_id: str) -> Any:
    """Attach one stable test id to a NiceGUI element."""
    try:
        element.props(f"data-testid={test_id}")
    except Exception:
        props = getattr(element, "_props", None)
        if isinstance(props, dict):
            props["data-testid"] = test_id
    return element


def _result_view_controls_row_classes() -> str:
    """Shared responsive row classes for Result View controls."""
    return "w-full items-end gap-3 mt-3 mb-3 flex-wrap lg:flex-nowrap"


__all__ = [
    "_result_view_controls_row_classes",
    "_with_test_id",
]
