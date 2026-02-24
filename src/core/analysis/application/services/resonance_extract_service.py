from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from core.analysis.application.analysis.extraction.admittance import extract_modes_from_dataframe
from core.analysis.application.services.data_record_management import (
    DataRecordManagementService,
)
from core.analysis.application.services.dataset_management import DatasetManagementService
from core.analysis.application.services.parameter_management import ParameterManagementService


class ResonanceExtractService:
    """
    Application service orchestrating resonance extraction from existing dataset records.
    (Non-fitting methods like Im(Y)=0 Zero-Crossing)
    """

    def __init__(self) -> None:
        self.dataset_service = DatasetManagementService()
        self.data_record_service = DataRecordManagementService()
        self.param_service = ParameterManagementService()

    def extract_admittance(
        self,
        dataset_identifier: str,
        bias_index: int | None = None,
    ) -> dict[str, typing.Any]:
        """
        Extract resonance modes from a dataset's Admittance (Im(Y)) records.
        Returns the extracted modes and optionally saves them as derived parameters.
        """
        dataset = self.dataset_service.get_dataset(dataset_identifier)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_identifier}")

        # Find matching admittance records
        all_records = self.data_record_service.list_records()
        y_records = [
            r
            for r in all_records
            if r.dataset_id == dataset.id
            and r.data_type == "y_parameters"
            and r.representation in ("imaginary", "imag")
        ]

        if not y_records:
            raise ValueError(
                f"No Imaginary Admittance records found for dataset {dataset_identifier}"
            )

        # Fetch detailed records
        detailed_records = [self.data_record_service.get_record(r.id) for r in y_records]

        dfs = []
        for rec in detailed_records:
            if rec is None:
                continue

            y_vals = np.array(rec.values, dtype=float)
            if not rec.axes or not rec.axes[0].get("values"):
                continue

            f_vals = np.array(rec.axes[0]["values"], dtype=float)

            if y_vals.ndim == 1:
                if len(y_vals) != len(f_vals):
                    continue
                df_part = pd.DataFrame(
                    {
                        "Freq [GHz]": f_vals / 1e9
                        if np.max(f_vals) > 1e6
                        else f_vals,  # Handle Hz vs GHz
                        "im(Y) []": y_vals,
                    }
                )
                if len(rec.axes) > 1 and rec.axes[1].get("name") in ("L_jun", "l_jun"):
                    df_part["L_jun [nH]"] = float(rec.axes[1]["values"][0])
                dfs.append(df_part)

            elif y_vals.ndim == 2:
                # 2D array: typically [Freq, L_jun]
                # Check axes[1] for L_jun
                l_jun_vals = [0.0]
                if len(rec.axes) > 1 and rec.axes[1].get("name") in ("L_jun", "l_jun"):
                    l_jun_vals = [float(v) for v in rec.axes[1]["values"]]

                if y_vals.shape[1] != len(l_jun_vals):
                    # Fallback single L_jun or mismatch
                    pass

                f_ghz = f_vals / 1e9 if np.max(f_vals) > 1e6 else f_vals

                for bi, l_val in enumerate(l_jun_vals):
                    if bi < y_vals.shape[1]:
                        df_part = pd.DataFrame(
                            {
                                "Freq [GHz]": f_ghz,
                                "im(Y) []": y_vals[:, bi],
                                "L_jun [nH]": float(l_val),
                            }
                        )
                        dfs.append(df_part)

        if not dfs:
            raise ValueError("No valid frequency/admittance axes found in records.")

        full_df = pd.concat(dfs, ignore_index=True)

        # Run extraction
        result_df = extract_modes_from_dataframe(full_df)

        if result_df is None or result_df.empty:
            raise ValueError("No resonance modes found from extraction.")

        # Slice by bias index if requested
        if bias_index is not None:
            if bias_index >= len(result_df):
                raise ValueError(
                    f"Selected bias_index {bias_index} is out of bounds "
                    f"(max: {len(result_df) - 1})."
                )
            result_df = result_df.iloc[[bias_index]]

        # Persist extracted modes to the dataset as derived parameters
        method_name = "admittance_zero_crossing"

        for idx, row in result_df.iterrows():
            l_jun_val = row["L_jun"] if "L_jun" in row else None
            # Formatting the param name based on bias index
            suffix = f"_b{idx}" if len(result_df) > 1 else ""

            mode_cols = [c for c in row.index if "Mode" in str(c)]
            for m_idx, mode_col in enumerate(mode_cols):
                f_ghz = row[mode_col]
                if pd.isna(f_ghz):
                    continue

                self.param_service.create_or_update_param(
                    dataset.id,
                    name=f"fr_ghz_{m_idx}{suffix}",
                    value=float(f_ghz),
                    unit="GHz",
                    device_type="resonator",
                    method=method_name,
                )

        return {
            "dataset_id": dataset.id,
            "extraction_method": method_name,
            "results": result_df,
        }
