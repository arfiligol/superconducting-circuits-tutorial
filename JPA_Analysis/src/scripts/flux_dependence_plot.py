from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, cast

import numpy as np
import pandas as pd

from src.preprocess.loader import find_dataset, load_component_record
from src.preprocess.schema import ParameterDataset, ParameterFamily, ParameterRepresentation
from src.utils import PREPROCESSED_DATA_DIR
from src.visualization import print_dataframe_table, render_flux_heatmap, render_flux_slice
from src.visualization.flux_plots import FluxView

DEFAULT_COMPONENT_IDS: Sequence[str] = [
    "LJPAL6572_B44D1",
]
DEFAULT_DEVICE: str | None = None
DEFAULT_VIEW: str = "all"
DEFAULT_PHASE_UNIT: str = "rad"
DEFAULT_WRAP_PHASE: bool = False
DEFAULT_SLICE_FREQUENCIES: Sequence[float] = (4.5, 6.5, 7.5)
DEFAULT_SLICE_BIASES: Sequence[float] = (-1.5, 0.0, 1.5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize flux dependence sweeps from preprocessed records."
    )
    parser.add_argument(
        "components",
        nargs="*",
        help="Component IDs or JSON paths (defaults to known components).",
    )
    parser.add_argument(
        "--parameter",
        default="S11",
        help="Parameter name (e.g., S11) for the amplitude/phase datasets (default: S11).",
    )
    parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of Plotly.",
    )
    parser.add_argument(
        "--device",
        default=DEFAULT_DEVICE,
        help="Device identifier used in plot titles (defaults to component ID).",
    )
    parser.add_argument(
        "--view",
        choices=["amplitude", "phase", "combined", "all"],
        default=DEFAULT_VIEW,
        help=f"Which flux plot(s) to render (default: {DEFAULT_VIEW}).",
    )
    parser.add_argument(
        "--phase-unit",
        choices=["deg", "rad"],
        default=DEFAULT_PHASE_UNIT,
        help=f"Display unit for phase heatmaps (default: {DEFAULT_PHASE_UNIT}).",
    )
    parser.add_argument(
        "--wrap-phase",
        action="store_true",
        default=DEFAULT_WRAP_PHASE,
        help="Wrap phase values into +/- 180° or +/- pi range before plotting.",
    )
    parser.add_argument(
        "--slice-frequency",
        type=float,
        action="append",
        help="Extract a frequency slice (GHz) and plot amplitude/phase vs bias. Repeat flag for multiple slices.",
    )
    parser.add_argument(
        "--slice-bias",
        type=float,
        action="append",
        help="Extract a bias slice (mA) and plot amplitude/phase vs frequency. Repeat flag for multiple slices.",
    )
    return parser.parse_args()


def resolve_component_path(candidate: str) -> Path | None:
    path = Path(candidate)
    if path.exists():
        return path

    fallback = PREPROCESSED_DATA_DIR / f"{candidate}.json"
    if fallback.exists():
        return fallback

    print(f"[Warning] Component record not found: {candidate}")
    return None


def dataset_to_pivot(dataset: ParameterDataset) -> pd.DataFrame:
    if len(dataset.axes) != 2:
        raise ValueError("Flux dependence datasets must have exactly two axes (frequency, bias).")
    freq_axis, bias_axis = dataset.axes
    freq_index = pd.Index(
        [float(value) for value in freq_axis.values], name=f"{freq_axis.name} [{freq_axis.unit}]"
    )
    bias_columns = pd.Index(
        [float(value) for value in bias_axis.values], name=f"{bias_axis.name} [{bias_axis.unit}]"
    )
    matrix = np.asarray(dataset.values, dtype=float)
    return pd.DataFrame(matrix, index=freq_index, columns=bias_columns)


def load_flux_pivots(
    component_path: Path,
    parameter: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str], dict[str, str]]:
    record = load_component_record(component_path)
    amp_dataset = find_dataset(
        record,
        family=ParameterFamily.s_parameters,
        parameter=parameter,
        representation=ParameterRepresentation.amplitude,
    )
    phase_dataset = find_dataset(
        record,
        family=ParameterFamily.s_parameters,
        parameter=parameter,
        representation=ParameterRepresentation.phase,
    )
    amp_pivot = dataset_to_pivot(amp_dataset)
    phase_pivot = dataset_to_pivot(phase_dataset)
    return amp_pivot, phase_pivot, amp_dataset.metadata, phase_dataset.metadata


def build_sample_statistics(
    pivot_amp: pd.DataFrame,
    pivot_phase_deg: pd.DataFrame,
    amp_unit: str | None,
) -> pd.DataFrame:
    freq_vals = np.repeat(pivot_amp.index.to_numpy(dtype=float), pivot_amp.shape[1])
    bias_vals = np.tile(pivot_amp.columns.to_numpy(dtype=float), pivot_amp.shape[0])
    amp_vals = pivot_amp.to_numpy(dtype=float).reshape(-1)
    phase_vals = pivot_phase_deg.to_numpy(dtype=float).reshape(-1)
    amp_label = f"Amplitude [{amp_unit}]" if amp_unit else "Amplitude"
    df = pd.DataFrame(
        {
            "Frequency_GHz": freq_vals,
            "Bias_mA": bias_vals,
            amp_label: amp_vals,
            "Phase_deg": phase_vals,
        }
    )
    return df.describe()


def convert_phase_to_degrees(pivot_phase: pd.DataFrame, stored_unit: str | None) -> pd.DataFrame:
    values = pivot_phase.to_numpy(dtype=float)
    if stored_unit and stored_unit.lower().startswith("rad"):
        converted = np.rad2deg(values)
    else:
        converted = values
    return pd.DataFrame(converted, index=pivot_phase.index, columns=pivot_phase.columns)


def unwrap_phase_deg(phase_deg: pd.DataFrame) -> pd.DataFrame:
    radians = np.deg2rad(phase_deg.to_numpy(dtype=float))
    unwrapped = np.unwrap(radians, axis=1)
    values = np.rad2deg(unwrapped)
    return pd.DataFrame(values, index=phase_deg.index, columns=phase_deg.columns)


def analyze_component(
    component_path: Path,
    parameter: str,
    views: Sequence[FluxView],
    device_label: str | None,
    phase_unit: str,
    wrap_phase: bool,
    freq_slices: Sequence[float],
    bias_slices: Sequence[float],
    use_matplotlib: bool,
) -> None:
    component_name = component_path.stem
    print(f"\n=== Flux dependence analysis: {component_name} ===")

    pivot_amp, pivot_phase_raw, amp_metadata, phase_metadata = load_flux_pivots(
        component_path, parameter
    )
    phase_deg = convert_phase_to_degrees(pivot_phase_raw, phase_metadata.get("unit"))
    phase_deg_unwrapped = unwrap_phase_deg(phase_deg)
    stats = build_sample_statistics(pivot_amp, phase_deg_unwrapped, amp_metadata.get("unit"))
    print_dataframe_table("Sample statistics", stats)

    phase_matrix, phase_label = _prepare_phase_matrix(phase_deg_unwrapped, phase_unit, wrap_phase)
    power_text = _format_power_text(amp_metadata.get("probe_power_dbm"))
    label = device_label or component_name
    base_title = f"FluxDep - {label}"
    if power_text:
        base_title = f"{base_title} - {power_text}"

    for view in views:
        view_label = _view_label(view)
        title = f"{base_title} - {view_label}"
        render_flux_heatmap(
            dataset_name=title,
            pivot_amp=pivot_amp,
            pivot_phase=phase_matrix,
            view=view,
            phase_label=phase_label,
            use_matplotlib=use_matplotlib,
        )

    for freq in freq_slices:
        slice_info = _extract_slice(pivot_amp, phase_matrix, axis="frequency", target=freq)
        if slice_info is None:
            print(f"[Warning] Unable to extract frequency slice near {freq} GHz")
            continue
        actual_value, amp_series, phase_series, x_axis_label = slice_info
        render_flux_slice(
            title=f"{base_title} - Freq Slice @ {actual_value:.3f} GHz",
            x_values=amp_series.index.to_numpy(dtype=float),
            amplitude_values=amp_series.to_numpy(dtype=float),
            phase_values=phase_series.to_numpy(dtype=float),
            x_axis_label=x_axis_label,
            phase_label=phase_label,
            use_matplotlib=use_matplotlib,
        )

    for bias in bias_slices:
        slice_info = _extract_slice(pivot_amp, phase_matrix, axis="bias", target=bias)
        if slice_info is None:
            print(f"[Warning] Unable to extract bias slice near {bias} mA")
            continue
        actual_value, amp_series, phase_series, x_axis_label = slice_info
        render_flux_slice(
            title=f"{base_title} - Bias Slice @ {actual_value:.3f} mA",
            x_values=amp_series.index.to_numpy(dtype=float),
            amplitude_values=amp_series.to_numpy(dtype=float),
            phase_values=phase_series.to_numpy(dtype=float),
            x_axis_label=x_axis_label,
            phase_label=phase_label,
            use_matplotlib=use_matplotlib,
        )


def run() -> None:
    args = parse_args()
    component_ids = args.components if args.components else list(DEFAULT_COMPONENT_IDS)
    if not component_ids:
        print("[Warning] No component IDs provided.")
        return

    views = _resolve_views(args.view)
    freq_slices = args.slice_frequency if args.slice_frequency else list(DEFAULT_SLICE_FREQUENCIES)
    bias_slices = args.slice_bias if args.slice_bias else list(DEFAULT_SLICE_BIASES)

    for identifier in component_ids:
        component_path = resolve_component_path(identifier)
        if component_path is None:
            continue
        analyze_component(
            component_path,
            parameter=args.parameter,
            views=views,
            device_label=args.device,
            phase_unit=args.phase_unit,
            wrap_phase=args.wrap_phase,
            freq_slices=freq_slices,
            bias_slices=bias_slices,
            use_matplotlib=args.matplotlib,
        )


def _resolve_views(selection: str) -> list[FluxView]:
    if selection == "all":
        return ["amplitude", "phase", "combined"]
    return [cast(FluxView, selection)]


def _view_label(view: FluxView) -> str:
    if view == "amplitude":
        return "Amplitude"
    if view == "phase":
        return "Phase"
    return "Amplitude+Phase"


def _format_power_text(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        numeric = float(value)
        return f"{numeric:.0f} dBm"
    except ValueError:
        return value


def _prepare_phase_matrix(
    phase_deg_unwrapped: pd.DataFrame,
    phase_unit: str,
    wrap_phase: bool,
) -> tuple[pd.DataFrame, str]:
    base_values = phase_deg_unwrapped.to_numpy(dtype=float)

    if phase_unit == "rad":
        values = np.deg2rad(base_values)
        label = "Phase [rad]"
        limit = np.pi
    else:
        values = base_values
        label = "Phase [deg]"
        limit = 180.0

    if wrap_phase:
        values = ((values + limit) % (2 * limit)) - limit

    matrix = pd.DataFrame(
        values, index=phase_deg_unwrapped.index, columns=phase_deg_unwrapped.columns
    )
    return matrix, label


def _extract_slice(
    pivot_amp: pd.DataFrame,
    pivot_phase: pd.DataFrame,
    axis: Literal["frequency", "bias"],
    target: float,
) -> tuple[float, pd.Series, pd.Series, str] | None:
    if axis == "frequency":
        axis_values = pivot_amp.index.to_numpy(dtype=float)
        if axis_values.size == 0:
            return None
        idx = int(np.argmin(np.abs(axis_values - target)))
        actual_val = axis_values[idx]
        amp_series = pivot_amp.iloc[idx]
        phase_series = pivot_phase.iloc[idx]
        x_label = "Bias Current [mA]"
    else:
        axis_values = pivot_amp.columns.to_numpy(dtype=float)
        if axis_values.size == 0:
            return None
        idx = int(np.argmin(np.abs(axis_values - target)))
        actual_val = axis_values[idx]
        amp_series = pivot_amp.iloc[:, idx]
        phase_series = pivot_phase.iloc[:, idx]
        x_label = "Frequency [GHz]"
    return actual_val, amp_series, phase_series, x_label


if __name__ == "__main__":
    run()
