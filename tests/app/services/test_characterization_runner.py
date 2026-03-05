"""Tests for characterization analysis execution service."""

from __future__ import annotations

import pytest

from app.services.characterization_runner import execute_analysis_run


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


def test_execute_analysis_run_rejects_unknown_analysis_id() -> None:
    with pytest.raises(ValueError, match="Unsupported analysis id"):
        execute_analysis_run(
            analysis_id="unknown_analysis",
            dataset_id=1,
            config_state={},
            trace_record_ids=None,
            trace_mode_group=None,
        )
