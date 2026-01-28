#!/usr/bin/env python3
"""CLI wrapper for SQUID model fitting."""

from typing import Annotated, Optional

import typer

from core.analysis.application.services.squid_fitting import (
    FitModel,
    analyze_file,
    resolve_component_path,
)
from core.analysis.infrastructure.visualization.plot_utils import plot_json_results

# ==========================================
#           USER CONFIGURATION
# ==========================================
# List of Component IDs or JSON paths to analyze if no CLI arguments are provided
DEFAULT_COMPONENTS = [
    "PF6FQ_Q0_Readout",
    "PF6FQ_Q0_XY",
]

# List of modes to fit/plot (e.g. ["Mode 1", "Mode 2"]). Set to None for all.
DEFAULT_MODES: list[str] | None = ["Mode 1"]

# Plot title
DEFAULT_TITLE = "Q0 Mode Fits (by Admittance)"

# Fitting Bounds (set to None for unbounded/default)
DEFAULT_LS_MIN: float | None = 0.0
DEFAULT_LS_MAX: float | None = None
DEFAULT_C_MIN: float | None = 0.0
DEFAULT_C_MAX: float | None = None

# Fixed Capacitance Value (pF). If set, forces 'fixed_c' model.
DEFAULT_FIXED_C_VALUE: float | None = None

# Fit Window (GHz)
DEFAULT_FIT_WINDOW_MIN: float = 15.0
DEFAULT_FIT_WINDOW_MAX: float = 30.0

# General Options
DEFAULT_USE_MATPLOTLIB = False
# ==========================================

DEFAULT_FIT_BOUNDS = {
    "Ls_nH": (0.0, None),
    "C_pF": (0.0, None),
}

app = typer.Typer(add_completion=False)


def build_bounds(
    ls_min: float | None,
    ls_max: float | None,
    c_min: float | None,
    c_max: float | None,
) -> dict[str, tuple[float | None, float | None]]:
    """Build parameter bounds dictionary from arguments."""

    def resolve(
        key: str, override_min: float | None, override_max: float | None
    ) -> tuple[float | None, float | None]:
        d_min, d_max = DEFAULT_FIT_BOUNDS[key]
        return (
            override_min if override_min is not None else d_min,
            override_max if override_max is not None else d_max,
        )

    return {
        "Ls_nH": resolve("Ls_nH", ls_min, ls_max),
        "C_pF": resolve("C_pF", c_min, c_max),
    }


@app.command()
def main(
    components: Annotated[
        Optional[list[str]],
        typer.Argument(help="Component IDs matching preprocessed JSONs."),
    ] = None,
    modes: Annotated[
        Optional[list[str]],
        typer.Option(help="Modes to fit/plot (e.g. 'Mode 1')."),
    ] = DEFAULT_MODES,
    title: Annotated[str, typer.Option(help="Plot title")] = DEFAULT_TITLE,
    ls_min: Annotated[Optional[float], typer.Option()] = DEFAULT_LS_MIN,
    ls_max: Annotated[Optional[float], typer.Option()] = DEFAULT_LS_MAX,
    c_min: Annotated[Optional[float], typer.Option()] = DEFAULT_C_MIN,
    c_max: Annotated[Optional[float], typer.Option()] = DEFAULT_C_MAX,
    fixed_c: Annotated[Optional[float], typer.Option()] = DEFAULT_FIXED_C_VALUE,
    fit_min: Annotated[float, typer.Option(help="Fit window min (GHz)")] = DEFAULT_FIT_WINDOW_MIN,
    fit_max: Annotated[float, typer.Option(help="Fit window max (GHz)")] = DEFAULT_FIT_WINDOW_MAX,
    matplotlib: Annotated[
        bool, typer.Option(help="Use Matplotlib backend")
    ] = DEFAULT_USE_MATPLOTLIB,
) -> None:
    """Batch analysis of admittance datasets."""
    # Use CLI args if provided, otherwise fall back to USER CONFIGURATION
    file_list = components if components else DEFAULT_COMPONENTS

    fit_model = FitModel.FIXED_C if fixed_c is not None else FitModel.WITH_LS

    entries = []
    for comp in file_list:
        path = resolve_component_path(comp)
        if not path:
            continue

        entry = analyze_file(
            path,
            modes,
            build_bounds(ls_min, ls_max, c_min, c_max),
            fit_model,
            fixed_c,
            (fit_min, fit_max),
        )
        if entry:
            entries.append(entry)

    if entries:
        plot_json_results(
            entries,
            target_modes=modes,
            title=title,
            use_matplotlib=matplotlib,
        )


if __name__ == "__main__":
    app()
