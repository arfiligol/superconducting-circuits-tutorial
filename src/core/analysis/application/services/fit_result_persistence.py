"""Persist SQUID fitting outputs into SQLite."""

from __future__ import annotations

from dataclasses import dataclass

from core.analysis.domain.schemas.fitting import AnalysisEntry
from core.shared.persistence import DataRecord, DerivedParameter, DeviceType, get_unit_of_work

FIT_METHOD = "lc_squid_fit"


@dataclass(frozen=True)
class PersistSummary:
    """Created-row counters after persisting fit outputs."""

    data_records: int
    derived_parameters: int


def persist_lc_squid_fit_outputs(
    dataset_id: int,
    entry: AnalysisEntry,
    device_type: DeviceType = DeviceType.OTHER,
    replace_existing: bool = True,
) -> PersistSummary:
    """
    Persist fitting outputs for one dataset.

    Stored outputs:
    - DataRecord(data_type=analysis_result, parameter=f_resonance)
    - DataRecord(data_type=analysis_result, parameter=f_resonance_fit)
    - DerivedParameter(name=Ls_nH, C_eff_pF, method=lc_squid_fit)
    """
    created_data_records = 0
    created_derived_params = 0

    with get_unit_of_work() as uow:
        dataset = uow.datasets.get(dataset_id)
        if dataset is None:
            raise ValueError(f"Dataset ID {dataset_id} not found.")

        if replace_existing:
            _remove_previous_fit_outputs(uow, dataset_id)

        for mode_name, mode_result in entry.fits.items():
            if mode_result.status != "success":
                continue

            raw_axes = [
                {
                    "name": "L_jun",
                    "unit": "nH",
                    "values": [float(value) for value in mode_result.raw_data.L_jun],
                }
            ]
            raw_values = [float(value) for value in mode_result.raw_data.Freq]

            uow.data_records.add(
                DataRecord(
                    dataset_id=dataset_id,
                    data_type="analysis_result",
                    parameter="f_resonance",
                    representation=mode_name,
                    axes=raw_axes,
                    values=raw_values,
                )
            )
            created_data_records += 1

            fit_axes = [
                {
                    "name": "L_jun",
                    "unit": "nH",
                    "values": [float(value) for value in mode_result.fit_curve.L_jun],
                }
            ]
            fit_values = [float(value) for value in mode_result.fit_curve.Freq]

            uow.data_records.add(
                DataRecord(
                    dataset_id=dataset_id,
                    data_type="analysis_result",
                    parameter="f_resonance_fit",
                    representation=mode_name,
                    axes=fit_axes,
                    values=fit_values,
                )
            )
            created_data_records += 1

            shared_extra = {
                "mode": mode_name,
                "rmse": float(mode_result.metrics.RMSE),
                "source": FIT_METHOD,
            }

            uow.derived_params.add(
                DerivedParameter(
                    dataset_id=dataset_id,
                    device_type=device_type,
                    name="Ls_nH",
                    value=float(mode_result.params.Ls_nH),
                    unit="nH",
                    method=FIT_METHOD,
                    extra=shared_extra,
                )
            )
            created_derived_params += 1

            uow.derived_params.add(
                DerivedParameter(
                    dataset_id=dataset_id,
                    device_type=device_type,
                    name="C_eff_pF",
                    value=float(mode_result.params.C_eff_pF),
                    unit="pF",
                    method=FIT_METHOD,
                    extra=shared_extra,
                )
            )
            created_derived_params += 1

        uow.commit()

    return PersistSummary(
        data_records=created_data_records,
        derived_parameters=created_derived_params,
    )


def _remove_previous_fit_outputs(uow, dataset_id: int) -> None:
    """Delete older SQUID fitting outputs for idempotent persistence."""
    for record in uow.data_records.list_by_dataset(dataset_id):
        if record.data_type != "analysis_result":
            continue
        if record.parameter in {"f_resonance", "f_resonance_fit"}:
            uow.data_records.delete(record)

    for param in uow.derived_params.list_by_dataset(dataset_id):
        if param.method != FIT_METHOD:
            continue
        if param.name in {"Ls_nH", "C_eff_pF"}:
            uow.derived_params.delete(param)
