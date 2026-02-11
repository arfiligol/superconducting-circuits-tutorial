#!/usr/bin/env python3
"""CLI wrapper for SQUID model fitting."""

from typing import Annotated

import typer

from core.analysis.application.services.fit_result_persistence import persist_lc_squid_fit_outputs
from core.analysis.application.services.squid_fitting import (
    FitModel,
    analyze_file,
    resolve_dataset,
)
from core.analysis.infrastructure.visualization.plot_utils import plot_json_results
from core.shared.persistence.models import DeviceType

# ==========================================
#           USER CONFIGURATION
# ==========================================
# List of modes to fit/plot (e.g. ["Mode 1", "Mode 2"]). Set to None for all.
DEFAULT_MODES: list[str] | None = ["Mode 1"]

# Plot title
DEFAULT_TITLE = "Q0 Mode Fits (by Admittance)"

# Fitting Bounds (set to None for unbounded/default)
DEFAULT_LS_MIN: float | None = 0.0
DEFAULT_LS_MAX: float | None = None
DEFAULT_C_MIN: float | None = 0.0
DEFAULT_C_MAX: float | None = None

# Fit Window (GHz)
DEFAULT_FIT_WINDOW_MIN: float = 15.0
DEFAULT_FIT_WINDOW_MAX: float = 30.0

# General Options

# ==========================================

DEFAULT_FIT_BOUNDS = {
    "Ls_nH": (0.0, None),
    "C_pF": (0.0, None),
}

app = typer.Typer(help="Fit Analysis Commands", add_completion=False)


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


@app.command("lc-squid")
def lc_squid_fit(
    datasets: Annotated[
        list[str] | None,
        typer.Argument(help="Dataset names or IDs."),
    ] = None,
    modes: Annotated[
        list[str] | None,
        typer.Option(help="Modes to fit/plot (e.g. '1'). Can be used multiple times."),
    ] = DEFAULT_MODES,
    title: Annotated[str, typer.Option(help="Plot title")] = DEFAULT_TITLE,
    ls_min: Annotated[float | None, typer.Option()] = DEFAULT_LS_MIN,
    ls_max: Annotated[float | None, typer.Option()] = DEFAULT_LS_MAX,
    c_min: Annotated[float | None, typer.Option()] = DEFAULT_C_MIN,
    c_max: Annotated[float | None, typer.Option()] = DEFAULT_C_MAX,
    fixed_c: Annotated[
        float | None,
        typer.Option(help="Fixed Capacitance Value (pF). Forces 'fixed_c' model."),
    ] = None,
    no_ls: Annotated[
        bool,
        typer.Option("--no-ls", help="Disable Series Inductance (Ls) fitting."),
    ] = False,
    fit_min: Annotated[float, typer.Option(help="Fit window min (GHz)")] = DEFAULT_FIT_WINDOW_MIN,
    fit_max: Annotated[float, typer.Option(help="Fit window max (GHz)")] = DEFAULT_FIT_WINDOW_MAX,
    save_to_db: Annotated[
        bool,
        typer.Option(
            "--save-to-db/--no-save-to-db",
            help="Persist fit outputs into DataRecord/DerivedParameter tables.",
        ),
    ] = False,
    device_type: Annotated[
        DeviceType,
        typer.Option(
            "--device-type",
            case_sensitive=False,
            help="Device type used when saving DerivedParameter rows.",
        ),
    ] = DeviceType.OTHER,
    replace_existing: Annotated[
        bool,
        typer.Option(
            "--replace-existing/--append",
            help="Replace existing lc_squid_fit outputs in DB for each dataset.",
        ),
    ] = True,
) -> None:
    """
    Fit SQUID LC parameters (Ls, C) from admittance data.

    Models:
    - Default: Fits with Series Inductance (Ls).
    - --no-ls: Fits WITHOUT Series Inductance (ideal LC).
    - --fixed-c <VAL>: Fits Ls with Fixed Capacitance.
    """
    if not datasets:
        typer.echo("Error: No datasets specified.")
        typer.echo("Usage: sc analysis fit lc-squid [OPTIONS] [DATASETS]...")
        typer.echo("Example: uv run sc analysis fit lc-squid 1 2 --no-ls")
        raise typer.Exit(code=1)

    # Determine Fit Model
    if fixed_c is not None:
        if no_ls:
            typer.echo("Warning: --no-ls ignored when --fixed-c is set.")
        fit_model = FitModel.FIXED_C
    elif no_ls:
        fit_model = FitModel.NO_LS
    else:
        fit_model = FitModel.WITH_LS  # Default

    # Normalize modes input (handle "1" -> "Mode 1")
    if modes:
        normalized_modes = []
        for m in modes:
            if m.isdigit():
                normalized_modes.append(f"Mode {m}")
            else:
                normalized_modes.append(m)
        modes = normalized_modes

    entries = []
    for comp in datasets:
        dataset = resolve_dataset(comp)
        if not dataset:
            continue

        entry = analyze_file(
            dataset,
            modes,
            build_bounds(ls_min, ls_max, c_min, c_max),
            fit_model,
            fixed_c,
            (fit_min, fit_max),
        )
        if entry:
            entries.append(entry)
            if save_to_db:
                if dataset.id is None:
                    typer.echo(f"Skip save: dataset '{dataset.name}' has no database ID.")
                else:
                    summary = persist_lc_squid_fit_outputs(
                        dataset_id=int(dataset.id),
                        entry=entry,
                        device_type=device_type,
                        replace_existing=replace_existing,
                    )
                    typer.echo(
                        "Saved fit outputs for "
                        f"'{dataset.name}': "
                        f"{summary.data_records} data records, "
                        f"{summary.derived_parameters} derived parameters."
                    )

    if entries:
        plot_json_results(
            entries,
            target_modes=modes,
            title=title,
        )


if __name__ == "__main__":
    app()
