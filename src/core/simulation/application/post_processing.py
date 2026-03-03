"""Port-level post-processing helpers for simulation matrix results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from core.simulation.domain.circuit import SimulationResult

type ModeFilter = Literal["base", "sideband", "all"]


@dataclass(frozen=True)
class PortMatrixSweep:
    """Complex Y-matrix sweep in one fixed mode and one fixed basis."""

    frequencies_ghz: tuple[float, ...]
    mode: tuple[int, ...]
    labels: tuple[str, ...]
    y_matrices: tuple[np.ndarray, ...]
    source_kind: Literal["y", "z", "s"]

    @property
    def dimension(self) -> int:
        """Return matrix dimension."""
        return len(self.labels)

    def trace(self, row: int, col: int) -> list[complex]:
        """Return one complex trace from all frequency slices."""
        if row < 0 or col < 0 or row >= self.dimension or col >= self.dimension:
            raise IndexError("Trace index out of range.")
        return [complex(matrix[row, col]) for matrix in self.y_matrices]


def filtered_modes(result: SimulationResult, mode_filter: ModeFilter) -> list[tuple[int, ...]]:
    """Return available modes filtered by mode family."""
    modes = result.available_mode_indices
    if mode_filter == "all":
        return modes
    if mode_filter == "base":
        return [mode for mode in modes if _is_base_mode(mode)]
    return [mode for mode in modes if not _is_base_mode(mode)]


def build_port_y_sweep(
    *,
    result: SimulationResult,
    mode: tuple[int, ...],
    ports: list[int] | None = None,
    reference_impedance_ohm: float = 50.0,
) -> PortMatrixSweep:
    """Build one port-space Y-matrix sweep for one selected mode tuple."""
    selected_mode = SimulationResult.normalize_mode(mode)
    selected_ports = sorted(set(ports or result.available_port_indices))
    if not selected_ports:
        raise ValueError("No ports are available for post-processing.")
    if reference_impedance_ohm <= 0:
        raise ValueError("Reference impedance must be positive.")

    labels = tuple(str(port) for port in selected_ports)
    freq_count = len(result.frequencies_ghz)
    if freq_count == 0:
        raise ValueError("Simulation result has no frequency points.")

    y_traces = _try_mode_matrix_from_family(
        result=result,
        mode=selected_mode,
        ports=selected_ports,
        family="y",
    )
    if y_traces is not None:
        matrices = _matrix_stack_from_traces(
            traces=y_traces,
            ports=selected_ports,
            frequency_count=freq_count,
        )
        return PortMatrixSweep(
            frequencies_ghz=tuple(float(value) for value in result.frequencies_ghz),
            mode=selected_mode,
            labels=labels,
            y_matrices=tuple(matrices),
            source_kind="y",
        )

    z_traces = _try_mode_matrix_from_family(
        result=result,
        mode=selected_mode,
        ports=selected_ports,
        family="z",
    )
    if z_traces is not None:
        z_matrices = _matrix_stack_from_traces(
            traces=z_traces,
            ports=selected_ports,
            frequency_count=freq_count,
        )
        y_matrices = tuple(
            _safe_matrix_inverse(matrix, context="Z->Y conversion")
            for matrix in z_matrices
        )
        return PortMatrixSweep(
            frequencies_ghz=tuple(float(value) for value in result.frequencies_ghz),
            mode=selected_mode,
            labels=labels,
            y_matrices=y_matrices,
            source_kind="z",
        )

    s_traces = _try_mode_matrix_from_family(
        result=result,
        mode=selected_mode,
        ports=selected_ports,
        family="s",
    )
    if s_traces is None:
        raise ValueError(
            "Mode-aware Y/Z/S matrix traces are unavailable for this mode/port selection."
        )

    s_matrices = _matrix_stack_from_traces(
        traces=s_traces,
        ports=selected_ports,
        frequency_count=freq_count,
    )
    y_matrices = tuple(
        _safe_matrix_inverse(
            _z_from_s(matrix, reference_impedance_ohm=reference_impedance_ohm),
            context="S->Z->Y conversion",
        )
        for matrix in s_matrices
    )
    return PortMatrixSweep(
        frequencies_ghz=tuple(float(value) for value in result.frequencies_ghz),
        mode=selected_mode,
        labels=labels,
        y_matrices=y_matrices,
        source_kind="s",
    )


def apply_coordinate_transform(
    sweep: PortMatrixSweep,
    transform_matrix: np.ndarray,
    *,
    labels: tuple[str, ...] | None = None,
) -> PortMatrixSweep:
    """Apply Y_m = A^{-T} Y A^{-1} to all frequency slices."""
    matrix_a = np.asarray(transform_matrix, dtype=np.complex128)
    if matrix_a.shape != (sweep.dimension, sweep.dimension):
        raise ValueError("Transform matrix shape does not match sweep dimension.")
    a_inverse = _safe_matrix_inverse(matrix_a, context="coordinate transform matrix")

    transformed = tuple(
        (a_inverse.T @ np.asarray(matrix, dtype=np.complex128) @ a_inverse)
        for matrix in sweep.y_matrices
    )
    return PortMatrixSweep(
        frequencies_ghz=sweep.frequencies_ghz,
        mode=sweep.mode,
        labels=labels or sweep.labels,
        y_matrices=transformed,
        source_kind=sweep.source_kind,
    )


def kron_reduce(
    sweep: PortMatrixSweep,
    *,
    keep_indices: list[int],
) -> PortMatrixSweep:
    """Apply Schur-complement Kron reduction on every frequency slice."""
    if not keep_indices:
        raise ValueError("Kron reduction requires at least one kept index.")

    dim = sweep.dimension
    normalized_keep = sorted(set(int(index) for index in keep_indices))
    if any(index < 0 or index >= dim for index in normalized_keep):
        raise ValueError("Kron keep indices out of range.")

    drop = [index for index in range(dim) if index not in normalized_keep]
    if not drop:
        return sweep

    reduced_matrices: list[np.ndarray] = []
    keep_array = np.asarray(normalized_keep, dtype=int)
    drop_array = np.asarray(drop, dtype=int)
    for matrix in sweep.y_matrices:
        y = np.asarray(matrix, dtype=np.complex128)
        y_bb = y[np.ix_(keep_array, keep_array)]
        y_bi = y[np.ix_(keep_array, drop_array)]
        y_ib = y[np.ix_(drop_array, keep_array)]
        y_ii = y[np.ix_(drop_array, drop_array)]
        reduced = y_bb - (y_bi @ np.linalg.solve(y_ii, y_ib))
        reduced_matrices.append(reduced)

    reduced_labels = tuple(sweep.labels[index] for index in normalized_keep)
    return PortMatrixSweep(
        frequencies_ghz=sweep.frequencies_ghz,
        mode=sweep.mode,
        labels=reduced_labels,
        y_matrices=tuple(reduced_matrices),
        source_kind=sweep.source_kind,
    )


def build_common_differential_transform(
    *,
    dimension: int,
    first_index: int,
    second_index: int,
    alpha: float,
    beta: float,
) -> np.ndarray:
    """Build an in-place cm/dm basis transform matrix."""
    if dimension < 2:
        raise ValueError("Common/differential transform requires at least 2 dimensions.")
    if first_index == second_index:
        raise ValueError("Common/differential transform requires two distinct indices.")
    if first_index < 0 or second_index < 0 or first_index >= dimension or second_index >= dimension:
        raise ValueError("Transform indices out of range.")
    if abs((alpha + beta) - 1.0) > 1e-6:
        raise ValueError("alpha + beta must equal 1.")

    matrix = np.eye(dimension, dtype=np.complex128)
    matrix[first_index, :] = 0.0
    matrix[first_index, first_index] = float(alpha)
    matrix[first_index, second_index] = float(beta)

    matrix[second_index, :] = 0.0
    matrix[second_index, first_index] = 1.0
    matrix[second_index, second_index] = -1.0
    return matrix


def _is_base_mode(mode: tuple[int, ...]) -> bool:
    return all(value == 0 for value in mode)


def _try_mode_matrix_from_family(
    *,
    result: SimulationResult,
    mode: tuple[int, ...],
    ports: list[int],
    family: Literal["y", "z", "s"],
) -> dict[tuple[int, int], list[complex]] | None:
    traces: dict[tuple[int, int], list[complex]] = {}
    getter = {
        "y": result.get_mode_y_parameter_complex,
        "z": result.get_mode_z_parameter_complex,
        "s": result.get_mode_s_parameter_complex,
    }[family]
    try:
        for output_port in ports:
            for input_port in ports:
                traces[(output_port, input_port)] = getter(
                    mode,
                    output_port,
                    mode,
                    input_port,
                )
    except KeyError:
        return None
    return traces


def _matrix_stack_from_traces(
    *,
    traces: dict[tuple[int, int], list[complex]],
    ports: list[int],
    frequency_count: int,
) -> list[np.ndarray]:
    matrices: list[np.ndarray] = []
    port_count = len(ports)
    for frequency_index in range(frequency_count):
        matrix = np.zeros((port_count, port_count), dtype=np.complex128)
        for output_row, output_port in enumerate(ports):
            for input_col, input_port in enumerate(ports):
                values = traces[(output_port, input_port)]
                if len(values) != frequency_count:
                    raise ValueError("Inconsistent trace length across matrix entries.")
                matrix[output_row, input_col] = values[frequency_index]
        matrices.append(matrix)
    return matrices


def _safe_matrix_inverse(matrix: np.ndarray, *, context: str) -> np.ndarray:
    try:
        identity = np.eye(matrix.shape[0], dtype=np.complex128)
        return np.linalg.solve(matrix, identity)
    except np.linalg.LinAlgError as exc:
        raise ValueError(f"Matrix inversion failed in {context}: {exc}") from exc


def _z_from_s(matrix_s: np.ndarray, *, reference_impedance_ohm: float) -> np.ndarray:
    identity = np.eye(matrix_s.shape[0], dtype=np.complex128)
    right_inverse = _safe_matrix_inverse(identity - matrix_s, context="S to Z conversion")
    return float(reference_impedance_ohm) * ((identity + matrix_s) @ right_inverse)
