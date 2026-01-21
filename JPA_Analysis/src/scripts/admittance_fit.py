from __future__ import annotations

import argparse
from collections.abc import Sequence
from enum import Enum
from pathlib import Path
from typing import NamedTuple, cast

import pandas as pd

from src.extraction import extract_modes_from_dataframe, normalize_mode_columns
from src.optimizer.fit_modes import (
    fit_squid_model,
    fit_squid_model_with_Ls,
    fit_squid_model_with_Ls_fixed_C,
)
from src.preprocess.loader import (
    dataset_to_dataframe,
    find_dataset,
    load_component_record,
)
from src.preprocess.schema import ParameterFamily, ParameterRepresentation
from src.types import AnalysisEntry, FitResultsByMode, ModeFitResult
from src.utils import PREPROCESSED_DATA_DIR
from src.visualization import plot_json_results, print_dataframe_table

# ---------------------------------------------------------------------------
# User configuration
# ---------------------------------------------------------------------------

# Component IDs stored under data/preprocessed/<component_id>.json
DEFAULT_COMPONENT_IDS: Sequence[str] = [
    "PF6FQ_Q0_Readout",
    "PF6FQ_Q0_XY_and_Readout",
    "PF6FQ_Q0_XY",
]

# Specify which extracted modes should be plotted/highlighted.
# Use None/empty to plot every available mode.
DEFAULT_MODES_TO_PLOT: Sequence[str] = ["Mode 1"]

# Default title for the plot window.
DEFAULT_PLOT_TITLE: str = "Q0 Mode Fits (by Admittance)"

# Default parameter bounds (None indicates no bound).
DEFAULT_FIT_BOUNDS: dict[str, tuple[float | None, float | None]] = {
    "Ls_nH": (0.0, None),
    "C_pF": (0.0, None),
}

# L_jun filter window (min, max) in nH. None means no limit.
DEFAULT_FIT_WINDOW: tuple[float | None, float | None] = (15, 30)


class FitModel(Enum):
    NO_LS = "no_ls"
    WITH_LS = "with_ls"
    FIXED_C = "fixed_c"


class AdmittanceFitArgs(NamedTuple):
    components: list[str]
    modes: list[str] | None
    title: str
    ls_min: float | None
    ls_max: float | None
    c_min: float | None
    c_max: float | None
    fixed_c: float | None
    fit_min: float | None
    fit_max: float | None
    matplotlib: bool


def parse_args() -> AdmittanceFitArgs:
    parser = argparse.ArgumentParser(
        description=("Batch analysis of admittance datasets stored under data/preprocessed/.")
    )
    _ = parser.add_argument(
        "components",
        nargs="*",
        help="Component IDs or JSON paths under data/preprocessed/ (defaults provided).",
    )
    _ = parser.add_argument(
        "--modes",
        nargs="+",
        help="Subset of modes to fit/plot (e.g., --modes 'Mode 1' 'Mode 2').",
    )
    _ = parser.add_argument(
        "--title",
        default=DEFAULT_PLOT_TITLE,
        help="Custom title for the plot window.",
    )
    _ = parser.add_argument("--ls-min", type=float, default=None, help="Lower bound for Ls (nH).")
    _ = parser.add_argument("--ls-max", type=float, default=None, help="Upper bound for Ls (nH).")
    _ = parser.add_argument("--c-min", type=float, default=None, help="Lower bound for C (pF).")
    _ = parser.add_argument("--c-max", type=float, default=None, help="Upper bound for C (pF).")
    _ = parser.add_argument(
        "--fixed-c",
        type=float,
        default=None,
        help="If provided, also run fitting with fixed Capacitance (pF). Required for 'fixed_c' model.",
    )
    _ = parser.add_argument(
        "--fit-min",
        type=float,
        default=None,
        help=f"Lower bound for fitting window (L_jun in nH). Default: {DEFAULT_FIT_WINDOW[0]}",
    )
    _ = parser.add_argument(
        "--fit-max",
        type=float,
        default=None,
        help=f"Upper bound for fitting window (L_jun in nH). Default: {DEFAULT_FIT_WINDOW[1]}",
    )
    _ = parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of the default Plotly view.",
    )
    args = cast(AdmittanceFitArgs, cast(object, parser.parse_args()))
    return AdmittanceFitArgs(
        components=args.components,
        modes=args.modes,
        title=args.title,
        ls_min=args.ls_min,
        ls_max=args.ls_max,
        c_min=args.c_min,
        c_max=args.c_max,
        fixed_c=args.fixed_c,
        fit_min=args.fit_min,
        fit_max=args.fit_max,
        matplotlib=args.matplotlib,
    )


def _build_bounds(
    args: AdmittanceFitArgs,
) -> dict[str, tuple[float | None, float | None]]:
    def resolve(
        key: str,
        override_min: float | None,
        override_max: float | None,
    ) -> tuple[float | None, float | None]:
        default_min, default_max = DEFAULT_FIT_BOUNDS[key]
        bound_min = override_min if override_min is not None else default_min
        bound_max = override_max if override_max is not None else default_max
        return (bound_min, bound_max)

    return {
        "Ls_nH": resolve("Ls_nH", args.ls_min, args.ls_max),
        "C_pF": resolve("C_pF", args.c_min, args.c_max),
    }


def resolve_component_path(candidate: str) -> Path | None:
    """Resolve a component identifier or explicit JSON path."""
    path = Path(candidate)
    if path.exists():
        return path

    fallback = PREPROCESSED_DATA_DIR / f"{candidate}.json"
    if fallback.exists():
        return fallback

    print(f"[Warning] Component record not found: {candidate}")
    return None


def extract_modes(component_path: Path) -> pd.DataFrame | None:
    record = load_component_record(component_path)
    dataset = find_dataset(
        record,
        family=ParameterFamily.y_parameters,
        parameter="Y11",
        representation=ParameterRepresentation.imaginary,
    )
    df_raw = dataset_to_dataframe(dataset, value_label="im(Y) []")
    df_modes = extract_modes_from_dataframe(df_raw)
    if df_modes is None:
        return None
    df_modes = normalize_mode_columns(df_modes)
    return df_modes


def print_fit_summary(
    name: str,
    fit_results: FitResultsByMode,
    target_modes: Sequence[str] | None,
    show_ls: bool = True,
) -> None:
    if not fit_results:
        print(f"[Warning] {name}: no fit results to summarize.")
        return

    # Use the name provided in the argument as the header
    print(f"\n--- {name} ---")
    for mode_name in sorted(fit_results.keys()):
        if target_modes and mode_name not in target_modes:
            continue

        result: ModeFitResult = fit_results[mode_name]
        if result["status"] != "success":
            print(f"  > {mode_name}: failed ({result['reason']})")
            continue

        params = result["params"]
        metrics = result["metrics"]

        parts = []
        if show_ls:
            parts.append(f"Ls={params['Ls_nH']:.4f} nH")

        parts.append(f"C={params['C_eff_pF']:.4f} pF")
        parts.append(f"RMSE={metrics['RMSE']:.4f}")

        print(f"  > {mode_name}: " + ", ".join(parts))
    print()


def analyze_file(
    component_path: Path,
    modes_to_highlight: Sequence[str] | None,
    parameter_bounds: dict[str, tuple[float | None, float | None]],
    fit_model: FitModel,
    fixed_c: float | None,
    fit_window: tuple[float | None, float | None],
) -> AnalysisEntry | None:
    print(f"\n=== Processing {component_path.stem} ===")
    df_modes = extract_modes(component_path)
    if df_modes is None or df_modes.empty:
        print(f"  > Extraction failed or returned empty results for {component_path.stem}")
        return None

    print_dataframe_table("Extracted Resonant Modes", df_modes)

    print_dataframe_table("Extracted Resonant Modes", df_modes)

    fit_results: FitResultsByMode
    fit_name: str
    show_ls_in_summary: bool = True

    if fit_model == FitModel.NO_LS:
        fit_results = fit_squid_model(
            df_modes, parameter_bounds=parameter_bounds, fit_window=fit_window
        )
        fit_name = "squid-model-fit (No Ls)"
        show_ls_in_summary = False
    elif fit_model == FitModel.WITH_LS:
        fit_results = fit_squid_model_with_Ls(
            df_modes, parameter_bounds=parameter_bounds, fit_window=fit_window
        )
        fit_name = "squid-model-with-Ls-fit (Standard)"
    elif fit_model == FitModel.FIXED_C:
        if fixed_c is None:
            print(
                f"[Error] Fixed capacitance (fixed_c) must be provided for {FitModel.FIXED_C} model."
            )
            return None
        fit_results = fit_squid_model_with_Ls_fixed_C(
            df_modes,
            capacitance_pf=fixed_c,
            parameter_bounds=parameter_bounds,
            fit_window=fit_window,
        )
        fit_name = f"squid-model-with-Ls-fixed-C-fit (C={fixed_c} pF)"
    else:
        raise ValueError(f"Unknown fit model: {fit_model}")

    print_fit_summary(fit_name, fit_results, modes_to_highlight, show_ls=show_ls_in_summary)

    entry: AnalysisEntry = {"filename": component_path.stem, "fits": fit_results}
    return entry


def run_no_ls() -> None:
    """Entry point for No-Ls fitting."""
    main(FitModel.NO_LS)


def run_with_ls() -> None:
    """Entry point for Standard (With-Ls) fitting."""
    main(FitModel.WITH_LS)


def run_with_ls_fixed_c() -> None:
    """Entry point for Fixed-C fitting."""
    main(FitModel.FIXED_C)


def main(fit_model: FitModel = FitModel.WITH_LS) -> None:
    args = parse_args()

    file_list: Sequence[str] = args.components if args.components else DEFAULT_COMPONENT_IDS
    modes_to_plot: Sequence[str] | None = args.modes if args.modes else DEFAULT_MODES_TO_PLOT
    parameter_bounds = _build_bounds(args)
    plot_title = args.title
    use_matplotlib = args.matplotlib
    analysis_entries: list[AnalysisEntry] = []

    # Resolve fit window using defaults if arguments are missing
    fit_min = args.fit_min if args.fit_min is not None else DEFAULT_FIT_WINDOW[0]
    fit_max = args.fit_max if args.fit_max is not None else DEFAULT_FIT_WINDOW[1]

    # Validate fixed_c if the model requires it
    if fit_model == FitModel.FIXED_C and args.fixed_c is None:
        print(
            f"[Error] The '{fit_model.value}' model requires a fixed capacitance (--fixed-c) to be provided."
        )
        return

    for identifier in file_list:
        component_path = resolve_component_path(identifier)
        if component_path is None:
            continue
        entry = analyze_file(
            component_path,
            modes_to_plot,
            parameter_bounds,
            fit_model,
            args.fixed_c,
            (fit_min, fit_max),
        )
        if entry:
            analysis_entries.append(entry)

    if not analysis_entries:
        print("[Error] No datasets were processed successfully.")
        return

    plot_modes: list[str] | None = list(modes_to_plot) if modes_to_plot else None
    plot_json_results(
        analysis_entries,
        target_modes=plot_modes,
        title=plot_title,
        use_matplotlib=use_matplotlib,
    )


if __name__ == "__main__":
    main(FitModel.WITH_LS)
