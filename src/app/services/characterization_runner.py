"""Application-level execution service for Characterization analyses."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from core.analysis.application.services.characterization_fitting_service import (
    CharacterizationFittingService,
    SquidFittingConfig,
    Y11FittingConfig,
)
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.analysis.application.services.resonance_fit_service import ResonanceFitService


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


__all__ = ["execute_analysis_run"]
