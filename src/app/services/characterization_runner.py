"""Application-level execution service for Characterization analyses."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from core.analysis.application.services.characterization_fitting_service import (
    CharacterizationFittingService,
    SquidFittingConfig,
    Y11FittingConfig,
)
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.persistence import DataRecord, get_unit_of_work


@dataclass(frozen=True)
class SweepSupportDiagnostic:
    """Support boundary for one analysis against selected parameter-sweep traces."""

    status: Literal["sweep-ready", "partial", "blocked"]
    reason: str


def _value_ndim(values: object) -> int:
    """Infer nested list dimensionality without loading numerical libraries."""
    if not isinstance(values, list) or not values:
        return 1
    first = values[0]
    if isinstance(first, list):
        return 1 + _value_ndim(first)
    return 1


def _axis_name(record: DataRecord, index: int) -> str:
    if index >= len(record.axes):
        return ""
    return str(record.axes[index].get("name", "")).strip().lower()


def _is_l_jun_axis(name: str) -> bool:
    return name in {"l_jun", "l_ind"}


def _is_sweep_record(record: DataRecord) -> bool:
    shape = record.trace_shape()
    value_ndim = len(shape) if shape else _value_ndim(record.values)
    if value_ndim > 1:
        return True
    if len(record.axes) <= 1:
        return False
    return record.axis_length(1) > 1


def _load_selected_records(
    dataset_id: int,
    trace_record_ids: Sequence[int] | None,
) -> list[DataRecord]:
    with get_unit_of_work() as uow:
        records = list(uow.data_records.list_by_dataset(dataset_id))
        if trace_record_ids is None:
            return records
        selected_ids = {int(record_id) for record_id in trace_record_ids}
        return [record for record in records if int(record.id or 0) in selected_ids]


def _selected_s21_records(records: Iterable[DataRecord]) -> list[DataRecord]:
    return [
        record
        for record in records
        if str(record.data_type) in {"s_parameters", "s_params"}
        and str(record.parameter).strip().upper() == "S21"
    ]


def _diagnose_analysis_sweep_support_from_records(
    *,
    analysis_id: str,
    records: Sequence[DataRecord],
) -> SweepSupportDiagnostic | None:
    """Classify parameter-sweep support for one analysis against selected records."""
    sweep_records = [record for record in records if _is_sweep_record(record)]
    if not sweep_records:
        return None

    max_ndim = max(
        len(record.trace_shape()) or _value_ndim(record.values) for record in sweep_records
    )
    second_axis_names = {_axis_name(record, 1) for record in sweep_records if len(record.axes) > 1}
    has_non_l_jun_second_axis = any(
        axis_name and not _is_l_jun_axis(axis_name) for axis_name in second_axis_names
    )

    if analysis_id == "admittance_extraction":
        if max_ndim > 2:
            return SweepSupportDiagnostic(
                status="blocked",
                reason="Admittance extraction supports up to 2D sweeps only.",
            )
        if has_non_l_jun_second_axis:
            return SweepSupportDiagnostic(
                status="blocked",
                reason="Admittance extraction requires a single L_jun sweep axis for 2D traces.",
            )
        return SweepSupportDiagnostic(
            status="sweep-ready",
            reason="2D Freq x L_jun admittance sweeps are supported.",
        )

    if analysis_id in {"y11_fit", "squid_fitting"}:
        if max_ndim > 2:
            return SweepSupportDiagnostic(
                status="blocked",
                reason="This fitting path supports up to 2D sweeps only.",
            )
        if has_non_l_jun_second_axis:
            return SweepSupportDiagnostic(
                status="blocked",
                reason="This fitting path requires a 2D Freq x L_jun sweep.",
            )
        return SweepSupportDiagnostic(
            status="sweep-ready",
            reason="2D Freq x L_jun sweeps are supported.",
        )

    if analysis_id == "s21_resonance_fit":
        s21_sweep_records = [
            record for record in _selected_s21_records(records) if _is_sweep_record(record)
        ]
        if not s21_sweep_records:
            return None

        s21_max_ndim = max(
            len(record.trace_shape()) or _value_ndim(record.values) for record in s21_sweep_records
        )
        if s21_max_ndim > 2:
            return SweepSupportDiagnostic(
                status="blocked",
                reason="S21 resonance fitting supports at most one sweep axis.",
            )
        s21_second_axis_names = {
            _axis_name(record, 1) for record in s21_sweep_records if len(record.axes) > 1
        }
        if s21_second_axis_names and all(_is_l_jun_axis(name) for name in s21_second_axis_names):
            return SweepSupportDiagnostic(
                status="sweep-ready",
                reason=(
                    "2D Freq x L_jun sweeps persist per-slice bias and render Mode vs L_jun."
                ),
            )
        return SweepSupportDiagnostic(
            status="partial",
            reason=(
                "Single-axis 2D sweeps run per slice, but only L_jun sweeps get the canonical "
                "Mode vs L_jun artifact."
            ),
        )

    return None


def diagnose_analysis_sweep_support(
    *,
    analysis_id: str,
    dataset_id: int,
    trace_record_ids: Sequence[int] | None,
) -> SweepSupportDiagnostic | None:
    """Load selected traces and classify parameter-sweep support for one analysis."""
    records = _load_selected_records(dataset_id, trace_record_ids)
    return _diagnose_analysis_sweep_support_from_records(
        analysis_id=analysis_id,
        records=records,
    )


def _config_int(
    config_state: Mapping[str, str | float | int | None],
    name: str,
    default: int,
) -> int:
    value = config_state.get(name)
    if value is None:
        return default
    return int(value)


def _config_float(config_state: Mapping[str, str | float | int | None], name: str) -> float | None:
    value = config_state.get(name)
    if value is None:
        return None
    return float(value)


def _config_str(
    config_state: Mapping[str, str | float | int | None],
    name: str,
    default: str,
) -> str:
    value = config_state.get(name)
    if value is None:
        return default
    return str(value)


def execute_analysis_run(
    *,
    analysis_id: str,
    dataset_id: int,
    config_state: Mapping[str, str | float | int | None],
    trace_record_ids: Sequence[int] | None = None,
    trace_mode_group: str | None = None,
) -> None:
    """Execute one characterization analysis run for one dataset scope."""
    trace_ids = list(trace_record_ids) if trace_record_ids is not None else None
    sweep_support = diagnose_analysis_sweep_support(
        analysis_id=analysis_id,
        dataset_id=dataset_id,
        trace_record_ids=trace_ids,
    )
    if sweep_support is not None and sweep_support.status == "blocked":
        raise ValueError(f"Sweep support: blocked - {sweep_support.reason}")

    if analysis_id == "admittance_extraction":
        ResonanceExtractService().extract_admittance(
            str(dataset_id),
            record_ids=trace_ids,
            trace_mode_group=trace_mode_group,
        )
        return

    if analysis_id == "s21_resonance_fit":
        ResonanceFitService().perform_fit(
            dataset_identifier=str(dataset_id),
            parameter="S21",
            model=_config_str(config_state, "model", "notch"),
            resonators=_config_int(config_state, "resonators", 1),
            f_min=_config_float(config_state, "f_min"),
            f_max=_config_float(config_state, "f_max"),
            record_ids=trace_ids,
        )
        return

    if analysis_id == "squid_fitting":
        CharacterizationFittingService().run_squid_fitting(
            dataset_id=dataset_id,
            config=SquidFittingConfig(
                fit_model=_config_str(config_state, "fit_model", "WITH_LS"),
                ls_min_nh=_config_float(config_state, "ls_min_nh"),
                ls_max_nh=_config_float(config_state, "ls_max_nh"),
                c_min_pf=_config_float(config_state, "c_min_pf"),
                c_max_pf=_config_float(config_state, "c_max_pf"),
                fixed_c_pf=_config_float(config_state, "fixed_c_pf"),
                fit_min_nh=_config_float(config_state, "fit_min_nh"),
                fit_max_nh=_config_float(config_state, "fit_max_nh"),
            ),
            record_ids=trace_ids,
            trace_mode_group=trace_mode_group,
        )
        return

    if analysis_id == "y11_fit":
        CharacterizationFittingService().run_y11_fitting(
            dataset_id=dataset_id,
            config=Y11FittingConfig(
                ls1_init_nh=float(_config_float(config_state, "ls1_init_nh") or 0.01),
                ls2_init_nh=float(_config_float(config_state, "ls2_init_nh") or 0.01),
                c_init_pf=float(_config_float(config_state, "c_init_pf") or 0.885),
                c_max_pf=float(_config_float(config_state, "c_max_pf") or 3.0),
            ),
            record_ids=trace_ids,
            trace_mode_group=trace_mode_group,
        )
        return

    raise ValueError(f"Unsupported analysis id: {analysis_id}")


__all__ = [
    "SweepSupportDiagnostic",
    "_diagnose_analysis_sweep_support_from_records",
    "diagnose_analysis_sweep_support",
    "execute_analysis_run",
]
