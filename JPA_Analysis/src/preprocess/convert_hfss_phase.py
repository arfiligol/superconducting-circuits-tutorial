from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from src.preprocess.naming import strip_component_suffix
from src.preprocess.record_utils import upsert_component_record, write_component_record
from src.preprocess.schema import (
    ComponentRecord,
    ParameterAxis,
    ParameterDataset,
    ParameterFamily,
    ParameterRepresentation,
    RawFileMeta,
    SourceType,
)
from src.utils import DATA_DIR, RAW_LAYOUT_PHASE_DIR

PREPROCESSED_DIR = DATA_DIR / "preprocessed"
DEFAULT_FILES: Sequence[str] = ["LJPAL658_v3_S11_Phase_Deg.csv"]


def detect_columns(df: pd.DataFrame) -> tuple[str, str, str]:
    l_cols = [c for c in df.columns if "l_jun" in c.lower()]
    if not l_cols:
        raise ValueError("Unable to locate L_jun column.")
    freq_cols = [c for c in df.columns if "freq" in c.lower()]
    if not freq_cols:
        raise ValueError("Unable to locate frequency column.")
    phase_cols = [
        c for c in df.columns if "phase" in c.lower() or "deg(" in c.lower() or "cang" in c.lower()
    ]
    if not phase_cols:
        raise ValueError("Unable to locate phase column.")
    return l_cols[0], freq_cols[0], phase_cols[0]


def reshape_matrix(df: pd.DataFrame, l_col: str, freq_col: str, phase_col: str) -> pd.DataFrame:
    pivot = df.pivot(index=freq_col, columns=l_col, values=phase_col).sort_index()
    pivot = pivot[sorted(pivot.columns)]
    return pivot


def determine_component_id(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    return strip_component_suffix(path.stem)


def convert_to_radians(matrix: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(np.deg2rad(matrix), index=matrix.index, columns=matrix.columns)


def build_component_record(
    component_id: str,
    pivot_rad: pd.DataFrame,
    raw_path: Path,
    parameter_name: str,
) -> ComponentRecord:
    freq_axis = ParameterAxis(name="Freq", unit="GHz", values=pivot_rad.index.tolist())
    bias_axis = ParameterAxis(
        name="L_jun", unit="nH", values=pivot_rad.columns.astype(float).tolist()
    )

    dataset_phase = ParameterDataset(
        dataset_id=f"{component_id}-{parameter_name}-phase",
        family=ParameterFamily.s_parameters,
        parameter=parameter_name,
        representation=ParameterRepresentation.phase,
        ports=["port1"],
        axes=[freq_axis, bias_axis],
        values=pivot_rad.values.tolist(),
        metadata={},
    )

    record = ComponentRecord(
        component_id=component_id,
        source_type=SourceType.measurement,
        datasets=[dataset_phase],
        raw_files=[RawFileMeta(path=str(raw_path))],
    )
    return record


class HFSSArgs(argparse.Namespace):
    csv: list[Path] | None = None
    component_id: str | None = None
    output: Path | None = None


def parse_args() -> HFSSArgs:
    parser = argparse.ArgumentParser(description="Convert HFSS phase CSV to preprocessed JSON.")
    parser.add_argument(
        "csv",
        nargs="*",
        type=Path,
        help="Path(s) to HFSS phase CSV (defaults to DEFAULT_FILES).",
    )
    parser.add_argument("--component-id", help="Override component identifier")
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination JSON file (defaults to data/preprocessed/<component_id>.json)",
    )
    return parser.parse_args(namespace=HFSSArgs())


def main() -> None:
    args = parse_args()
    input_files = args.csv if args.csv else [Path(path) for path in DEFAULT_FILES]
    if not input_files:
        raise ValueError("No input CSVs specified.")

    for raw_path in input_files:
        if not raw_path.exists():
            candidate = RAW_LAYOUT_PHASE_DIR / raw_path
            if candidate.exists():
                raw_path = candidate
            else:
                print(f"[Warning] File not found: {raw_path}")
                continue

        df: pd.DataFrame = pd.read_csv(raw_path)  # type: ignore
        l_col, freq_col, phase_col = detect_columns(df)
        pivot_deg = reshape_matrix(df, l_col, freq_col, phase_col)
        pivot_rad = convert_to_radians(pivot_deg)
        component_id = determine_component_id(raw_path, args.component_id)
        record = build_component_record(component_id, pivot_rad, raw_path, parameter_name="S11")

        output_path = args.output or (PREPROCESSED_DIR / f"{component_id}.json")
        merged = upsert_component_record(
            output_path=output_path,
            component_id=component_id,
            source_type=record.source_type,
            dataset=record.datasets[0],
            raw_path=raw_path,
        )
        write_component_record(merged, output_path)
        print(f"[OK] Wrote preprocessed record -> {output_path}")


if __name__ == "__main__":
    main()
