from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple, cast

import numpy as np
import pandas as pd

from src.preprocess.naming import strip_component_suffix
from src.preprocess.record_utils import upsert_component_record, write_component_record
from src.preprocess.schema import (
    ParameterAxis,
    ParameterDataset,
    ParameterFamily,
    ParameterRepresentation,
    SourceType,
)
from src.utils import DATA_DIR, RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR

PREPROCESSED_DIR = DATA_DIR / "preprocessed"
DEFAULT_FILES: Sequence[str] = [
    "LJPAL6572_B44D1_FluxDep_-2to2mA_0.1mA_3.8to8.0GHz_-55dBm_201_30_73.392.txt",
]


class FluxDependenceArgs(NamedTuple):
    txt: list[Path]
    component_id: str | None
    output: Path | None
    parameter: str


def parse_args() -> FluxDependenceArgs:
    parser = argparse.ArgumentParser(
        description="Convert flux dependence TXT sweeps to preprocessed JSON."
    )
    _ = parser.add_argument(
        "txt",
        nargs="*",
        type=Path,
        help="Path(s) to flux dependence TXT (defaults to DEFAULT_FILES).",
    )
    _ = parser.add_argument("--component-id", help="Override component identifier for the record.")
    _ = parser.add_argument(
        "--output",
        type=Path,
        help="Destination JSON (default: data/preprocessed/<component_id>.json).",
    )
    _ = parser.add_argument(
        "--parameter",
        default="S11",
        help="Parameter name to associate with the amplitude/phase datasets (default: S11).",
    )
    return cast(FluxDependenceArgs, cast(object, parser.parse_args()))


def unwrap_phase_degrees(series: pd.Series[float]) -> np.ndarray:
    return np.rad2deg(np.unwrap(np.deg2rad(series.to_numpy(dtype=float))))


def read_flux_file(path: Path) -> tuple[pd.DataFrame, float | None]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    bias_idx = next(
        (i for i, line in enumerate(lines) if line.lower().startswith("bias current")),
        None,
    )
    if bias_idx is None or bias_idx + 1 >= len(lines):
        raise ValueError("Bias current block not found in flux dependence file.")
    bias_values = [float(value) for value in lines[bias_idx + 1].split(",") if value]
    bias_count = len(bias_values)

    data_start = None
    for offset in range(bias_idx + 2, len(lines)):
        if lines[offset].lower().startswith("frequency"):
            data_start = offset + 1
            break
    if data_start is None:
        raise ValueError("Frequency data section not found in flux dependence file.")

    power_line = next((line for line in lines if "probe power" in line.lower()), "")
    power_dbm: float | None = None
    if power_line:
        suffix = power_line.split("]")[-1].strip()
        try:
            power_dbm = float(suffix)
        except ValueError:
            power_dbm = None

    records: list[dict[str, float]] = []
    for line in lines[data_start:]:
        parts = [part for part in line.split(",") if part]
        if len(parts) < 1 + 2 * bias_count:
            continue
        freq_ghz = float(parts[0])
        amp_slice = parts[1 : 1 + bias_count]
        phase_slice = parts[1 + bias_count : 1 + 2 * bias_count]
        amplitudes = [float(value) for value in amp_slice]
        phases = [float(value) for value in phase_slice]
        for bias_mA, amp_db, phase_deg in zip(bias_values, amplitudes, phases, strict=True):
            records.append(
                {
                    "Frequency_GHz": freq_ghz,
                    "Bias_mA": bias_mA,
                    "Amplitude_dB": amp_db,
                    "Phase_deg": phase_deg,
                }
            )
    if not records:
        raise ValueError("No amplitude/phase samples parsed from flux dependence file.")
    df = pd.DataFrame(records)
    df.sort_values(["Frequency_GHz", "Bias_mA"], inplace=True)
    df["Phase_deg_unwrapped"] = df.groupby("Frequency_GHz")["Phase_deg"].transform(
        unwrap_phase_degrees
    )
    return df, power_dbm


def pivot_quantity(df: pd.DataFrame, column: str) -> pd.DataFrame:
    pivot = df.pivot(index="Frequency_GHz", columns="Bias_mA", values=column)
    pivot = pivot.sort_index()
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)
    return pivot


def build_dataset(
    *,
    component_id: str,
    pivot: pd.DataFrame,
    parameter: str,
    representation: ParameterRepresentation,
    dataset_suffix: str,
    metadata: dict[str, str],
) -> ParameterDataset:
    freq_axis = ParameterAxis(
        name="Frequency", unit="GHz", values=[float(v) for v in pivot.index.tolist()]
    )
    bias_axis = ParameterAxis(
        name="Bias", unit="mA", values=[float(v) for v in pivot.columns.tolist()]
    )
    return ParameterDataset(
        dataset_id=f"{component_id}-{dataset_suffix}",
        family=ParameterFamily.s_parameters,
        parameter=parameter,
        representation=representation,
        ports=["port1"],
        axes=[freq_axis, bias_axis],
        values=pivot.values.tolist(),
        metadata=metadata,
    )


def determine_component_id(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    return strip_component_suffix(path.stem)


def main() -> None:
    args = parse_args()
    input_files = args.txt if args.txt else [Path(path) for path in DEFAULT_FILES]
    if not input_files:
        raise ValueError("No flux dependence TXT files specified.")

    for raw_path in input_files:
        if not raw_path.exists():
            candidate = RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR / raw_path
            if candidate.exists():
                raw_path = candidate
            else:
                print(f"[Warning] File not found: {raw_path}")
                continue

        df, power_dbm = read_flux_file(raw_path)
        amp_pivot = pivot_quantity(df, "Amplitude_dB")
        phase_pivot = pivot_quantity(df, "Phase_deg_unwrapped")

        component_id = determine_component_id(raw_path, args.component_id)
        parameter_name = args.parameter
        output_path = args.output or (PREPROCESSED_DIR / f"{component_id}.json")
        metadata_common = {}
        if power_dbm is not None:
            metadata_common["probe_power_dbm"] = f"{power_dbm:.3f}"

        amp_dataset = build_dataset(
            component_id=component_id,
            pivot=amp_pivot,
            parameter=parameter_name,
            representation=ParameterRepresentation.amplitude,
            dataset_suffix="flux-amplitude",
            metadata={**metadata_common, "unit": "dB"},
        )
        merged = upsert_component_record(
            output_path=output_path,
            component_id=component_id,
            source_type=SourceType.measurement,
            dataset=amp_dataset,
            raw_path=raw_path,
        )
        write_component_record(merged, output_path)

        phase_dataset = build_dataset(
            component_id=component_id,
            pivot=phase_pivot,
            parameter=parameter_name,
            representation=ParameterRepresentation.phase,
            dataset_suffix="flux-phase",
            metadata={**metadata_common, "unit": "deg"},
        )
        merged = upsert_component_record(
            output_path=output_path,
            component_id=component_id,
            source_type=SourceType.measurement,
            dataset=phase_dataset,
            raw_path=raw_path,
        )
        write_component_record(merged, output_path)
        print(f"[OK] Wrote flux dependence record -> {output_path}")


if __name__ == "__main__":
    main()
