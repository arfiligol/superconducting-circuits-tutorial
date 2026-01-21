from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple, cast

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
from src.utils import DATA_DIR, RAW_LAYOUT_ADMITTANCE_DIR

PREPROCESSED_DIR = DATA_DIR / "preprocessed"
DEFAULT_FILES: Sequence[str] = [
    # "LJPAL658_v1_Im_Y11.csv",
    # "LJPAL658_v2_Im_Y11.csv",
    # "LJPAL658_v3_Im_Y11.csv",
    # "LJPAL6572_B46D1_Im_Y11.csv",
    # "LJPAL6572_B46D2_Im_Y11.csv",
    # "LJPAL6574_B46D1_Im_Y11.csv",
    # "PF6FQ_Q0_Float_Im_Y11.csv",
    # "PF6FQ_Q0_diff_Im_Y11.csv",
    # "PF6FQ_Q0_Float_Deembed_Im_Y11.csv",
    # "PF6FQ_Q0_Float_No_Deembed_Im_Y11.csv",
    # "PF6FQ_Q1_Float_Im_Y11.csv",
    # "PF6FQ_Q0_Float_No_L_Im_Y11.csv",
    # "PF6FQ_Q2_Float_Im_Y11.csv",
    # "PF6FQ_Q3_Float_Im_Y11.csv",
    # "PF6FQ_Q4_Float_Im_Y11.csv",
    # "PF6FQ_Q5_Float_Im_Y11.csv",
    "PF6FQ_Q0_Readout_Im_Y11.csv",
    "PF6FQ_Q0_XY_and_Readout_Im_Y11.csv",
    "PF6FQ_Q0_XY_Im_Y11.csv",
]


def detect_columns(df: pd.DataFrame) -> tuple[str, str, str]:
    l_cols = [c for c in df.columns if "l_jun" in c.lower() or "l_ind" in c.lower()]
    if not l_cols:
        raise ValueError("Unable to locate L_jun column.")
    freq_cols = [c for c in df.columns if "freq" in c.lower()]
    if not freq_cols:
        raise ValueError("Unable to locate frequency column.")
    y_cols = [c for c in df.columns if "y" in c.lower()]
    if not y_cols:
        raise ValueError("Unable to locate admittance column.")
    return l_cols[0], freq_cols[0], y_cols[0]


def reshape_matrix(df: pd.DataFrame, l_col: str, freq_col: str, y_col: str) -> pd.DataFrame:
    pivot = df.pivot(index=freq_col, columns=l_col, values=y_col).sort_index()
    pivot = pivot[sorted(pivot.columns)]
    return pivot


def derive_parameter_name(column: str) -> str:
    lower = column.lower()
    if "y11" in lower or "(rect" in lower:
        return "Y11"
    if "y22" in lower:
        return "Y22"
    if "y12" in lower:
        return "Y12"
    if "y21" in lower:
        return "Y21"
    return "Y"


def build_component_record(
    component_id: str,
    pivot: pd.DataFrame,
    raw_path: Path,
    parameter_name: str,
) -> ComponentRecord:
    frequency_axis = ParameterAxis(name="Freq", unit="GHz", values=pivot.index.tolist())
    bias_axis = ParameterAxis(name="L_jun", unit="nH", values=[float(x) for x in pivot.columns])

    dataset = ParameterDataset(
        dataset_id=f"{component_id}-{parameter_name}-imag",
        family=ParameterFamily.y_parameters,
        parameter=parameter_name,
        representation=ParameterRepresentation.imaginary,
        ports=["port1"],
        axes=[frequency_axis, bias_axis],
        values=pivot.values.tolist(),
        metadata={},
    )

    record = ComponentRecord(
        component_id=component_id,
        source_type=SourceType.measurement,
        datasets=[dataset],
        raw_files=[RawFileMeta(path=str(raw_path))],
    )
    return record


def determine_component_id(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    return strip_component_suffix(path.stem)


class ProgramArgs(NamedTuple):
    csv: list[Path]
    component_id: str | None
    output: Path | None


def parse_args() -> ProgramArgs:
    parser = argparse.ArgumentParser(
        description="Convert HFSS admittance CSV to preprocessed JSON."
    )
    _ = parser.add_argument(
        "csv",
        nargs="*",
        type=Path,
        help="Path(s) to HFSS admittance CSV (defaults to DEFAULT_FILES).",
    )
    _ = parser.add_argument("--component-id", help="Override component identifier")
    _ = parser.add_argument(
        "--output",
        type=Path,
        help="Destination JSON file (defaults to data/preprocessed/<component_id>.json)",
    )
    args = cast(ProgramArgs, cast(object, parser.parse_args()))
    return ProgramArgs(csv=args.csv, component_id=args.component_id, output=args.output)


def main() -> None:
    args = parse_args()
    input_files = args.csv if args.csv else [Path(path) for path in DEFAULT_FILES]
    if not input_files:
        raise ValueError("No input CSVs specified.")

    for raw_path in input_files:
        if not raw_path.exists():
            candidate = RAW_LAYOUT_ADMITTANCE_DIR / raw_path
            if candidate.exists():
                raw_path = candidate
            else:
                print(f"[Warning] File not found: {raw_path}")
                continue

        df = pd.read_csv(raw_path)
        l_col, freq_col, y_col = detect_columns(df)
        pivot = reshape_matrix(df, l_col, freq_col, y_col)
        component_id = determine_component_id(raw_path, args.component_id)
        parameter_name = derive_parameter_name(y_col)

        record = build_component_record(component_id, pivot, raw_path, parameter_name)

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
