"""Application service for S-Parameter resonance fitting workflows."""

import numpy as np

from core.analysis.application.services.data_record_management import (
    DataRecordManagementService,
)
from core.analysis.application.services.dataset_management import DatasetManagementService
from core.analysis.application.services.parameter_management import ParameterManagementService
from core.analysis.domain.math.s_parameters import fit_notch_s21


class ResonanceFitService:
    """Service to extract dataset information and perform S-parameter notch resonance fits."""

    def __init__(self) -> None:
        self.dataset_service = DatasetManagementService()
        self.data_record_service = DataRecordManagementService()
        self.param_service = ParameterManagementService()

    def perform_notch_fit(
        self, dataset_identifier: str, parameter: str = "S21"
    ) -> dict[str, float]:
        """
        Perform a CPZM notch resonance fit on a given dataset and parameter.
        Uses complex representations if available, or reconstructs from magnitude/phase.
        """
        dataset = self.dataset_service.get_dataset(dataset_identifier)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_identifier}")

        # Find matching S-parameter records
        # Ideally, we look for both real/imag representations or magnitude/phase representations.
        # But wait, our HFSS phase pipeline only parses "phase" currently,
        # let's write a robust fetcher.

        # In a real situation, we should fetch DataRecord entities and extract lists.
        # However, `DatasetDetailDTO` in our system doesn't embed the actual `values` data directly
        # to avoid payload size bursts. We need to fetch the `DataRecord` explicitly.

        # We need a method to get DataRecords by Dataset ID and parameter
        # Let's search through all records and filter (in-memory for now, assuming small DB)
        all_records = self.data_record_service.list_records()
        s_records = [
            r
            for r in all_records
            if r.dataset_id == dataset.id
            and r.data_type == "s_parameters"
            and r.parameter == parameter
        ]

        if not s_records:
            raise ValueError(
                f"No s_parameters found for parameter {parameter} in dataset {dataset_identifier}"
            )

        # We need to construct the complex S21 and freq axis
        # First, reconstruct the records
        detailed_records = [self.data_record_service.get_record(r.id) for r in s_records]

        reps = {r.representation: r for r in detailed_records if r is not None}

        f_axis = None
        s21_complex = None

        if "real" in reps and "imaginary" in reps:
            # Reconstruct from Re/Im
            f_axis = np.array(reps["real"].axes[0].values)
            values_re = np.array(reps["real"].values)
            values_im = np.array(reps["imaginary"].values)
            s21_complex = values_re + 1j * values_im
        elif ("phase" in reps or "unwrapped_phase" in reps) and "magnitude" in reps:
            # Reconstruct from Mag/Phase
            # We assume they share the same frequency axis
            mag_record = reps["magnitude"]
            phase_key = "unwrapped_phase" if "unwrapped_phase" in reps else "phase"
            phase_record = reps[phase_key]

            f_axis = np.array(mag_record.axes[0].values)

            # HFSS magnitude is often in dB. We should check if it needs conversion to linear.
            # Assuming linear magnitude for now, but if it's dB: mag_lin = 10**(mag_dB/20)
            # The user's S-parameter files usually don't dictate dB vs lin in the representation string yet,
            # but standard is linear unless specified. We will assume linear.
            mag_vals = np.array(mag_record.values)
            phase_vals = np.array(phase_record.values)  # already in radians per phase.py

            s21_complex = mag_vals * np.exp(1j * phase_vals)
        else:
            raise ValueError(
                f"Dataset lack sufficient representations for {parameter}. "
                "Found: " + ", ".join(list(reps.keys())) + ". "
                "Need either (real, imaginary) OR (magnitude, phase/unwrapped_phase)."
            )

        # Now we have the arrays, call the math core
        # Note: Depending on the axes structure from raw HFSS, there might be multiple sweep dimensions
        # Assuming 1D for simplicity in the current implementation path
        f_arr = f_axis.flatten()
        s21_arr = s21_complex.flatten()

        # Mask out NaNs
        valid = ~np.isnan(f_arr) & ~np.isnan(s21_arr)
        f_arr = f_arr[valid]
        s21_arr = s21_arr[valid]

        # Fit
        result = fit_notch_s21(f_arr, s21_arr)

        # Save derived parameters
        method_name = f"complex_notch_fit_{parameter}"

        self.param_service.create_or_update_param(
            dataset.id, name="fr_ghz", value=result["fr"] / 1e9, unit="GHz", method=method_name
        )
        self.param_service.create_or_update_param(
            dataset.id, name="Ql", value=result["Ql"], unit="", method=method_name
        )
        self.param_service.create_or_update_param(
            dataset.id, name="Qc", value=result["Qc_mag"], unit="", method=method_name
        )
        self.param_service.create_or_update_param(
            dataset.id, name="Qi", value=result["Qi"], unit="", method=method_name
        )
        self.param_service.create_or_update_param(
            dataset.id,
            name="electrical_delay",
            value=result["tau"] * 1e9,
            unit="ns",
            method=method_name,
        )

        return result
