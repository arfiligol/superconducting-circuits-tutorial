#!/usr/bin/env python3
"""Service for SQUID model fitting workflows."""

from collections.abc import Sequence
from enum import Enum
from pathlib import Path

import pandas as pd

from core.analysis.application.analysis.extraction.admittance import extract_modes_from_dataframe
from core.analysis.application.analysis.extraction.cleaning import normalize_mode_columns
from core.analysis.application.analysis.fitting.modes import (
    fit_squid_model,
    fit_squid_model_with_Ls,
    fit_squid_model_with_Ls_fixed_C,
)
from core.analysis.domain.schemas.components import ParameterFamily, ParameterRepresentation
from core.analysis.domain.schemas.fitting import AnalysisEntry
from core.analysis.domain.services.data_conversion import convert_dataset_to_dataframe
from core.analysis.infrastructure.paths import PREPROCESSED_DATA_DIR
from core.analysis.infrastructure.repositories.component_repository import load_component_record
from core.analysis.infrastructure.visualization.dataframe_display import print_dataframe_table


class FitModel(Enum):
    """Fit model types for SQUID analysis."""

    NO_LS = "no_ls"
    WITH_LS = "with_ls"
    FIXED_C = "fixed_c"


def resolve_component_path(candidate: str) -> Path | None:
    """Resolve a component ID or path to an actual JSON file path."""
    path = Path(candidate)
    if path.exists():
        return path
    fallback = PREPROCESSED_DATA_DIR / f"{candidate}.json"
    if fallback.exists():
        return fallback
    print(f"[Warning] Component record not found: {candidate}")
    return None


def find_dataset(record, family, parameter, representation):
    """Find a dataset in a component record matching specific criteria."""
    p_upper = parameter.upper()
    for ds in record.datasets:
        if (
            ds.family == family
            and ds.representation == representation
            and ds.parameter.upper() == p_upper
        ):
            return ds
    return None


def extract_modes(component_path: Path) -> pd.DataFrame | None:
    """Load component data and extract resonant modes."""
    record = load_component_record(component_path)
    dataset = find_dataset(
        record,
        family=ParameterFamily.y_parameters,
        parameter="Y11",
        representation=ParameterRepresentation.imaginary,
    )
    if not dataset:
        print(f"[Error] Y11 imaginary dataset not found in {component_path}")
        return None

    df_raw = convert_dataset_to_dataframe(dataset, value_label="im(Y) []")
    df_modes = extract_modes_from_dataframe(df_raw)
    if df_modes is None:
        return None
    df_modes = normalize_mode_columns(df_modes)
    return df_modes


def analyze_file(
    component_path: Path,
    modes_to_highlight: Sequence[str] | None,
    parameter_bounds: dict[str, tuple[float | None, float | None]],
    fit_model: FitModel,
    fixed_c: float | None,
    fit_window: tuple[float | None, float | None],
) -> AnalysisEntry | None:
    """Execute the full SQUID fitting workflow for a single component file."""
    print(f"\n=== Processing {component_path.stem} ===")
    df_modes = extract_modes(component_path)
    if df_modes is None or df_modes.empty:
        print(f"  > Extraction failed for {component_path.stem}")
        return None

    print_dataframe_table("Extracted Resonant Modes", df_modes)

    if fit_model == FitModel.NO_LS:
        fit_results = fit_squid_model(df_modes, parameter_bounds, fit_window)
    elif fit_model == FitModel.WITH_LS:
        fit_results = fit_squid_model_with_Ls(df_modes, parameter_bounds, fit_window)
    elif fit_model == FitModel.FIXED_C:
        if fixed_c is None:
            print("[Error] fixed_c required for fixed-c model")
            return None
        fit_results = fit_squid_model_with_Ls_fixed_C(
            df_modes, fixed_c, parameter_bounds, fit_window
        )
    else:
        raise ValueError("Unknown fit model")

    return AnalysisEntry(filename=component_path.stem, fits=fit_results)
