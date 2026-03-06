"""Tests for characterization analysis execution service."""

from __future__ import annotations

import pytest

from app.services.characterization_runner import (
    SweepSupportDiagnostic,
    _diagnose_analysis_sweep_support_from_records,
    execute_analysis_run,
)
from core.shared.persistence import DataRecord


def _record(
    *,
    data_type: str,
    parameter: str,
    representation: str,
    axes: list[dict[str, object]],
    values: object,
) -> DataRecord:
    return DataRecord(
        dataset_id=1,
        data_type=data_type,
        parameter=parameter,
        representation=representation,
        axes=axes,
        values=values,
    )


def test_execute_analysis_run_dispatches_admittance_extraction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_extract_admittance(
        self: object,
        dataset_id: str,
        *,
        record_ids: list[int] | None = None,
        trace_mode_group: str | None = None,
    ) -> None:
        captured["dataset_id"] = dataset_id
        captured["record_ids"] = record_ids
        captured["trace_mode_group"] = trace_mode_group

    monkeypatch.setattr(
        "core.analysis.application.services.resonance_extract_service.ResonanceExtractService.extract_admittance",
        _fake_extract_admittance,
    )

    execute_analysis_run(
        analysis_id="admittance_extraction",
        dataset_id=12,
        config_state={},
        trace_record_ids=[1, 2],
        trace_mode_group="base",
    )

    assert captured == {
        "dataset_id": "12",
        "record_ids": [1, 2],
        "trace_mode_group": "base",
    }


def test_execute_analysis_run_dispatches_squid_fitting_with_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_run_squid_fitting(
        self: object,
        *,
        dataset_id: int,
        config: object,
        record_ids: list[int] | None = None,
        trace_mode_group: str | None = None,
    ) -> None:
        captured["dataset_id"] = dataset_id
        captured["config"] = config
        captured["record_ids"] = record_ids
        captured["trace_mode_group"] = trace_mode_group

    monkeypatch.setattr(
        "core.analysis.application.services.characterization_fitting_service.CharacterizationFittingService.run_squid_fitting",
        _fake_run_squid_fitting,
    )

    execute_analysis_run(
        analysis_id="squid_fitting",
        dataset_id=7,
        config_state={"fit_model": "FIXED_C", "fixed_c_pf": 0.123},
        trace_record_ids=[9],
        trace_mode_group="sideband",
    )

    config = captured["config"]
    assert captured["dataset_id"] == 7
    assert captured["record_ids"] == [9]
    assert captured["trace_mode_group"] == "sideband"
    assert config.fit_model == "FIXED_C"
    assert config.fixed_c_pf == pytest.approx(0.123)


def test_diagnose_analysis_sweep_support_marks_y11_and_squid_ready_for_2d_ljun() -> None:
    y11_record = _record(
        data_type="y_parameters",
        parameter="Y11",
        representation="imaginary",
        axes=[
            {"name": "Freq", "values": [4.0, 5.0]},
            {"name": "L_jun", "values": [1.0, 2.0]},
        ],
        values=[[0.1, 0.2], [0.3, 0.4]],
    )

    y11_support = _diagnose_analysis_sweep_support_from_records(
        analysis_id="y11_fit",
        records=[y11_record],
    )
    squid_support = _diagnose_analysis_sweep_support_from_records(
        analysis_id="squid_fitting",
        records=[y11_record],
    )
    admittance_support = _diagnose_analysis_sweep_support_from_records(
        analysis_id="admittance_extraction",
        records=[y11_record],
    )

    assert y11_support == SweepSupportDiagnostic(
        status="sweep-ready",
        reason="2D Freq x L_jun sweeps are supported.",
    )
    assert squid_support == SweepSupportDiagnostic(
        status="sweep-ready",
        reason="2D Freq x L_jun sweeps are supported.",
    )
    assert admittance_support == SweepSupportDiagnostic(
        status="sweep-ready",
        reason="2D Freq x L_jun admittance sweeps are supported.",
    )


def test_diagnose_analysis_sweep_support_blocks_wrong_sweep_axis() -> None:
    wrong_axis_record = _record(
        data_type="y_parameters",
        parameter="Y11",
        representation="imaginary",
        axes=[
            {"name": "Freq", "values": [4.0, 5.0]},
            {"name": "Pump", "values": [0.0, 1.0]},
        ],
        values=[[0.1, 0.2], [0.3, 0.4]],
    )

    diagnostic = _diagnose_analysis_sweep_support_from_records(
        analysis_id="y11_fit",
        records=[wrong_axis_record],
    )

    assert diagnostic == SweepSupportDiagnostic(
        status="blocked",
        reason="This fitting path requires a 2D Freq x L_jun sweep.",
    )


def test_diagnose_analysis_sweep_support_marks_s21_2d_as_partial() -> None:
    s21_record = _record(
        data_type="s_parameters",
        parameter="S21",
        representation="real",
        axes=[
            {"name": "Freq", "values": [4.0, 5.0]},
            {"name": "Pump", "values": [0.0, 1.0]},
        ],
        values=[[0.1, 0.2], [0.3, 0.4]],
    )

    diagnostic = _diagnose_analysis_sweep_support_from_records(
        analysis_id="s21_resonance_fit",
        records=[s21_record],
    )

    assert diagnostic == SweepSupportDiagnostic(
        status="partial",
        reason=(
            "Single-axis 2D sweeps run per slice, but sweep artifact/provenance support "
            "is still partial."
        ),
    )


def test_diagnose_analysis_sweep_support_blocks_multi_axis_sweeps() -> None:
    multi_axis_record = _record(
        data_type="s_parameters",
        parameter="S21",
        representation="real",
        axes=[
            {"name": "Freq", "values": [4.0, 5.0]},
            {"name": "L_jun", "values": [1.0, 2.0]},
            {"name": "Pump", "values": [0.0, 1.0]},
        ],
        values=[[[0.1, 0.2], [0.3, 0.4]], [[0.5, 0.6], [0.7, 0.8]]],
    )

    diagnostic = _diagnose_analysis_sweep_support_from_records(
        analysis_id="s21_resonance_fit",
        records=[multi_axis_record],
    )

    assert diagnostic == SweepSupportDiagnostic(
        status="blocked",
        reason="S21 resonance fitting is blocked for sweeps beyond one extra axis.",
    )


def test_execute_analysis_run_blocks_unsupported_sweep_before_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.characterization_runner.diagnose_analysis_sweep_support",
        lambda **_: SweepSupportDiagnostic(
            status="blocked",
            reason="Admittance extraction supports up to 2D sweeps only.",
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            r"Sweep support: blocked - Admittance extraction supports up to 2D sweeps only\."
        ),
    ):
        execute_analysis_run(
            analysis_id="admittance_extraction",
            dataset_id=12,
            config_state={},
            trace_record_ids=[1, 2],
            trace_mode_group="base",
        )


def test_execute_analysis_run_rejects_unknown_analysis_id() -> None:
    with pytest.raises(ValueError, match="Unsupported analysis id"):
        execute_analysis_run(
            analysis_id="unknown_analysis",
            dataset_id=1,
            config_state={},
            trace_record_ids=None,
            trace_mode_group=None,
        )
