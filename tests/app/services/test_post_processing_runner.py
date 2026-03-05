"""Tests for Simulation post-processing runner use-case service."""

from __future__ import annotations

import pytest

from app.services.post_processing_runner import (
    PostProcessingRunRequest,
    execute_post_processing_pipeline,
)
from core.simulation.domain.circuit import SimulationResult


def _sample_result() -> SimulationResult:
    frequencies = [1.0, 2.0]
    s11_real = [0.1, 0.2]
    s11_imag = [0.0, 0.0]
    mode = (0,)
    y_mode_real: dict[str, list[float]] = {}
    y_mode_imag: dict[str, list[float]] = {}
    for output_port, input_port, value in (
        (1, 1, 1.0),
        (1, 2, 0.0),
        (2, 1, 0.0),
        (2, 2, 2.0),
    ):
        label = SimulationResult._mode_trace_label(mode, output_port, mode, input_port)
        y_mode_real[label] = [value, value]
        y_mode_imag[label] = [0.0, 0.0]
    return SimulationResult(
        frequencies_ghz=frequencies,
        s11_real=s11_real,
        s11_imag=s11_imag,
        port_indices=[1, 2],
        mode_indices=[(0,)],
        y_parameter_mode_real=y_mode_real,
        y_parameter_mode_imag=y_mode_imag,
    )


def test_execute_post_processing_pipeline_requires_mode_selection() -> None:
    with pytest.raises(ValueError, match="Please select one mode before running post-processing"):
        execute_post_processing_pipeline(
            PostProcessingRunRequest(
                result=_sample_result(),
                input_source="raw_y",
                mode_filter="base",
                mode_token="",
                reference_impedance_ohm=50.0,
                step_sequence=[],
                circuit_definition=None,
                has_ptc_result=False,
            ),
            estimate_auto_weights=lambda _definition, _port_a, _port_b: (0.5, 0.5),
        )


def test_execute_post_processing_pipeline_identity_marks_not_hfss_comparable() -> None:
    run = execute_post_processing_pipeline(
        PostProcessingRunRequest(
            result=_sample_result(),
            input_source="raw_y",
            mode_filter="base",
            mode_token="0",
            reference_impedance_ohm=50.0,
            step_sequence=[
                {
                    "id": 1,
                    "type": "coordinate_transform",
                    "enabled": True,
                    "template": "identity",
                }
            ],
            circuit_definition=None,
            has_ptc_result=False,
        ),
        estimate_auto_weights=lambda _definition, _port_a, _port_b: (0.5, 0.5),
    )

    assert run.sweep.labels == ("1", "2")
    assert run.flow_spec["hfss_comparable"] is False
    assert "Port Termination Compensation is disabled." in str(
        run.flow_spec["hfss_not_comparable_reason"]
    )
    assert run.flow_spec["steps"][0]["template"] == "identity"


def test_execute_post_processing_pipeline_ct_plus_kron_marks_hfss_comparable() -> None:
    run = execute_post_processing_pipeline(
        PostProcessingRunRequest(
            result=_sample_result(),
            input_source="ptc_y",
            mode_filter="base",
            mode_token="0",
            reference_impedance_ohm=50.0,
            step_sequence=[
                {
                    "id": 1,
                    "type": "coordinate_transform",
                    "enabled": True,
                    "template": "cm_dm",
                    "weight_mode": "manual",
                    "alpha": 0.5,
                    "beta": 0.5,
                    "port_a": 1,
                    "port_b": 2,
                },
                {
                    "id": 2,
                    "type": "kron_reduction",
                    "enabled": True,
                    "keep_labels": ["dm(1,2)"],
                },
            ],
            circuit_definition=None,
            has_ptc_result=True,
        ),
        estimate_auto_weights=lambda _definition, _port_a, _port_b: (0.5, 0.5),
    )

    assert run.sweep.labels == ("dm(1,2)",)
    assert run.flow_spec["hfss_comparable"] is True
    assert run.flow_spec["input_y_source"] == "ptc_y"
    assert len(run.flow_spec["steps"]) == 2
    assert run.normalized_steps[0]["alpha"] == 0.5
