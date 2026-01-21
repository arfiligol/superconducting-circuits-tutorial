from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from src.extraction import extract_from_admittance, normalize_mode_columns
from src.utils import RAW_LAYOUT_ADMITTANCE_DIR
from src.visualization import print_dataframe_table

# Configure the list of admittance files to inspect
INPUT_FILES: Sequence[str] = [
    "PF6FQ_Q0_Float_Im_Y11.csv"
    # "LJPAL658_v1_Im_Y11.csv",
    # "LJPAL658_v2_Im_Y11.csv",
    # "LJPAL658_v3_Im_Y11.csv",
    # "LJPAL658_v1_No_Pump_Line_Im_Y11.csv",
    # "LJPAL658_v2_No_Pump_Line_Im_Y11.csv",
    # "LJPAL658_v3_No_Pump_Line_Im_Y11.csv",
]


def _version_key(filename: str) -> tuple[int, str]:
    """Sort helper based on `_v#` tokens inside filenames."""
    match = re.search(r"_v(\d+)", filename, flags=re.IGNORECASE)
    version = int(match.group(1)) if match else 10_000
    return (version, filename)


def resolve_csv_path(path_value: Path) -> Path | None:
    """Resolve a relative CSV path against `data/raw/admittance`."""
    if path_value.exists():
        return path_value
    candidate = RAW_LAYOUT_ADMITTANCE_DIR / path_value
    if candidate.exists():
        return candidate
    print(f"[Warning] File not found: {path_value}")
    return None


def inspect_file(csv_path: Path) -> None:
    """Extract and print resonances from a CSV file."""
    print(f"=== Extracting resonances from {csv_path.name} ===")
    df_res: pd.DataFrame | None = extract_from_admittance(csv_path)
    if df_res is None or df_res.empty:
        print("  > Extraction failed or returned empty.\n")
        return

    df_res = normalize_mode_columns(df_res)

    print_dataframe_table("Extracted Resonances", df_res)


def main() -> None:
    print("=== SQUID JPA Resonance Inspection ===")
    for file_name in sorted(INPUT_FILES, key=_version_key):
        csv_path = resolve_csv_path(Path(file_name))
        if csv_path is None:
            continue
        inspect_file(csv_path)


if __name__ == "__main__":
    main()
