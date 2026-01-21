from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from src.extraction import extract_modes_from_dataframe, normalize_mode_columns
from src.optimizer import fit_resonant_modes_fixed_capacitance
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

DEFAULT_COMPONENT_IDS: Sequence[str] = [
    "LJPAL658_v1",
    "LJPAL658_v2",
    "LJPAL658_v3",
]
DEFAULT_MODES_TO_PLOT: Sequence[str] = ["Mode 1"]
DEFAULT_CAPACITANCE_PF: float = 0.885
DEFAULT_PLOT_TITLE: str = "SQUID JPA Mode Fits (Fixed C)"


def parse_args() -> tuple[Sequence[str], Sequence[str] | None, str, float, bool]:
    parser = argparse.ArgumentParser(
        description=(
            "Fit SQUID LC modes across multiple admittance CSV files while fixing "
            "the effective capacitance."
        )
    )
    _ = parser.add_argument(
        "components",
        nargs="*",
        help="Component IDs or JSON paths (defaults to known components).",
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
    _ = parser.add_argument(
        "--capacitance-pf",
        type=float,
        default=DEFAULT_CAPACITANCE_PF,
        help=f"Capacitance value (in pF) held fixed during fitting (default={DEFAULT_CAPACITANCE_PF}).",
    )
    _ = parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of the default Plotly view.",
    )
    args = parser.parse_args()

    file_list: Sequence[str] = args.components if args.components else DEFAULT_COMPONENT_IDS
    mode_list: Sequence[str] | None = args.modes if args.modes else DEFAULT_MODES_TO_PLOT
    return (
        file_list,
        mode_list,
        args.title,
        float(args.capacitance_pf),
        bool(args.matplotlib),
    )


def resolve_component_path(candidate: str) -> Path | None:
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
    capacitance_pf: float,
) -> None:
    if not fit_results:
        print(f"[Warning] {name}: no fit results to summarize.")
        return

    print(f"\n--- Mode fit summary for {name} (C fixed at {capacitance_pf:.4f} pF) ---")
    for mode_name in sorted(fit_results.keys()):
        if target_modes and mode_name not in target_modes:
            continue

        result: ModeFitResult = fit_results[mode_name]
        if result["status"] != "success":
            print(f"  > {mode_name}: failed ({result['reason']})")
            continue

        params = result["params"]
        metrics = result["metrics"]
        print(
            f"  > {mode_name}: "
            + f"Ls={params['Ls_nH']:.4f} nH (C fixed), "
            + f"RMSE={metrics['RMSE']:.4f}"
        )
    print()


def analyze_file(
    component_path: Path,
    modes_to_highlight: Sequence[str] | None,
    capacitance_pf: float,
) -> AnalysisEntry | None:
    print(f"\n=== Processing {component_path.stem} ===")
    df_modes = extract_modes(component_path)
    if df_modes is None or df_modes.empty:
        print(f"  > Extraction failed or returned empty results for {component_path.stem}")
        return None

    print_dataframe_table("Extracted Resonant Modes", df_modes)

    fit_results = fit_resonant_modes_fixed_capacitance(df_modes, capacitance_pf=capacitance_pf)
    print_fit_summary(component_path.stem, fit_results, modes_to_highlight, capacitance_pf)

    entry: AnalysisEntry = {"filename": component_path.stem, "fits": fit_results}
    return entry


def run() -> None:
    file_list, modes_to_plot, plot_title, capacitance_pf, use_matplotlib = parse_args()
    analysis_entries: list[AnalysisEntry] = []

    for identifier in file_list:
        component_path = resolve_component_path(identifier)
        if component_path is None:
            continue
        entry = analyze_file(component_path, modes_to_plot, capacitance_pf)
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
    run()
