"""Tests for port-level simulation post-processing helpers."""

from __future__ import annotations

import numpy as np

from core.simulation.application.post_processing import (
    apply_coordinate_transform,
    build_common_differential_transform,
    build_port_y_sweep,
    filtered_modes,
    kron_reduce,
)
from core.simulation.domain.circuit import SimulationResult


def _mode_label(mode: tuple[int, ...], op: int, ip: int) -> str:
    token = SimulationResult.mode_token(mode)
    return f"om={token}|op={op}|im={token}|ip={ip}"


def _base_result_with_y() -> SimulationResult:
    mode = (0,)
    y_real = {
        _mode_label(mode, 1, 1): [2.0, 2.0],
        _mode_label(mode, 1, 2): [-1.0, -1.0],
        _mode_label(mode, 2, 1): [-1.0, -1.0],
        _mode_label(mode, 2, 2): [2.0, 2.0],
    }
    y_imag = {label: [0.0, 0.0] for label in y_real}
    return SimulationResult(
        frequencies_ghz=[5.0, 6.0],
        s11_real=[0.0, 0.0],
        s11_imag=[0.0, 0.0],
        port_indices=[1, 2],
        mode_indices=[(0,), (1,)],
        y_parameter_mode_real=y_real,
        y_parameter_mode_imag=y_imag,
    )


def test_filtered_modes_supports_base_and_sideband() -> None:
    result = _base_result_with_y()

    assert filtered_modes(result, "base") == [(0,)]
    assert filtered_modes(result, "sideband") == [(1,)]
    assert filtered_modes(result, "all") == [(0,), (1,)]


def test_build_port_y_sweep_reads_native_y_matrix() -> None:
    result = _base_result_with_y()

    sweep = build_port_y_sweep(result=result, mode=(0,))

    assert sweep.source_kind == "y"
    assert sweep.labels == ("1", "2")
    assert np.allclose(sweep.y_matrices[0], np.array([[2.0, -1.0], [-1.0, 2.0]]))


def test_build_port_y_sweep_falls_back_to_z_then_inverse() -> None:
    mode = (0,)
    z_real = {
        _mode_label(mode, 1, 1): [50.0, 50.0],
        _mode_label(mode, 1, 2): [0.0, 0.0],
        _mode_label(mode, 2, 1): [0.0, 0.0],
        _mode_label(mode, 2, 2): [25.0, 25.0],
    }
    z_imag = {label: [0.0, 0.0] for label in z_real}
    result = SimulationResult(
        frequencies_ghz=[5.0, 6.0],
        s11_real=[0.0, 0.0],
        s11_imag=[0.0, 0.0],
        port_indices=[1, 2],
        mode_indices=[mode],
        z_parameter_mode_real=z_real,
        z_parameter_mode_imag=z_imag,
    )

    sweep = build_port_y_sweep(result=result, mode=mode)

    assert sweep.source_kind == "z"
    assert np.allclose(sweep.y_matrices[0], np.array([[0.02, 0.0], [0.0, 0.04]]))


def test_build_port_y_sweep_falls_back_to_s_then_converts() -> None:
    mode = (0,)
    s_real = {
        _mode_label(mode, 1, 1): [0.0, 0.0],
        _mode_label(mode, 1, 2): [0.0, 0.0],
        _mode_label(mode, 2, 1): [0.0, 0.0],
        _mode_label(mode, 2, 2): [0.0, 0.0],
    }
    s_imag = {label: [0.0, 0.0] for label in s_real}
    result = SimulationResult(
        frequencies_ghz=[5.0, 6.0],
        s11_real=[0.0, 0.0],
        s11_imag=[0.0, 0.0],
        port_indices=[1, 2],
        mode_indices=[mode],
        s_parameter_mode_real=s_real,
        s_parameter_mode_imag=s_imag,
    )

    sweep = build_port_y_sweep(result=result, mode=mode, reference_impedance_ohm=50.0)

    assert sweep.source_kind == "s"
    assert np.allclose(sweep.y_matrices[0], np.array([[0.02, 0.0], [0.0, 0.02]]))


def test_coordinate_transform_and_kron_reduction_pipeline() -> None:
    result = _base_result_with_y()
    sweep = build_port_y_sweep(result=result, mode=(0,))

    transform = build_common_differential_transform(
        dimension=2,
        first_index=0,
        second_index=1,
        alpha=0.5,
        beta=0.5,
    )
    transformed = apply_coordinate_transform(
        sweep,
        transform_matrix=transform,
        labels=("cm(1,2)", "dm(1,2)"),
    )
    reduced = kron_reduce(transformed, keep_indices=[1])

    assert transformed.labels == ("cm(1,2)", "dm(1,2)")
    assert reduced.labels == ("dm(1,2)",)

    expected_first = transformed.y_matrices[0]
    y_dd = expected_first[1:2, 1:2]
    y_do = expected_first[1:2, 0:1]
    y_od = expected_first[0:1, 1:2]
    y_oo = expected_first[0:1, 0:1]
    expected_reduced = y_dd - (y_do @ np.linalg.solve(y_oo, y_od))
    assert np.allclose(reduced.y_matrices[0], expected_reduced)
