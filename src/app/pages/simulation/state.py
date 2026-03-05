"""State factory helpers for Simulation page."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def default_result_view_state(
    *,
    family: str = "s",
    metric: str = "magnitude_linear",
    z0: float = 50.0,
    family_sources: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build one canonical result-view state payload."""
    state: dict[str, Any] = {
        "family": family,
        "metric": metric,
        "z0": z0,
        "traces": [],
    }
    if family_sources:
        state["family_sources"] = dict(family_sources)
    return state


def default_post_processing_input_state() -> dict[str, str]:
    """Build one canonical post-processing input selector state."""
    return {"input_y_source": "raw_y"}

