"""Tests for Julia adapter validation and error mapping."""

import pytest

from core.simulation.domain.circuit import (
    CircuitDefinition,
    DriveSourceConfig,
    FrequencyRange,
    SimulationConfig,
)
from core.simulation.infrastructure.julia_adapter import JuliaSimulator


class _FakeJuliaMain:
    def __init__(self, behavior):
        self._behavior = behavior

    def run_custom_simulation(self, *args):
        return self._behavior(*args)


def _build_simulator(fake_behavior) -> JuliaSimulator:
    simulator = JuliaSimulator()
    simulator._initialized = True
    simulator._jl = _FakeJuliaMain(fake_behavior)
    return simulator


def _default_config() -> SimulationConfig:
    return SimulationConfig(pump_freq_ghz=5.0, n_modulation_harmonics=10, n_pump_harmonics=20)


def test_run_hbsolve_raises_input_error_for_missing_component_reference():
    circuit = CircuitDefinition(
        name="bad-ref",
        parameters={"C1": {"default": 1.0, "unit": "pF"}},
        topology=[("P1", "1", "0", 1), ("R1", "1", "0", "R1"), ("C1", "1", "0", "C1")],
    )
    simulator = _build_simulator(lambda *_: pytest.fail("Julia should not be called"))

    with pytest.raises(ValueError, match="SimulationInputError: topology references undefined"):
        simulator.run_hbsolve(
            circuit,
            FrequencyRange(start_ghz=1.0, stop_ghz=5.0, points=101),
            _default_config(),
        )


def test_run_hbsolve_raises_input_error_when_port_has_no_shunt_resistor():
    circuit = CircuitDefinition(
        name="no-port-r",
        parameters={
            "L1": {"default": 10.0, "unit": "nH"},
            "C1": {"default": 1.0, "unit": "pF"},
        },
        topology=[("P1", "1", "0", 1), ("L1", "1", "2", "L1"), ("C1", "2", "0", "C1")],
    )
    simulator = _build_simulator(lambda *_: pytest.fail("Julia should not be called"))

    with pytest.raises(
        ValueError,
        match="SimulationInputError: each port node needs a shunt resistor",
    ):
        simulator.run_hbsolve(
            circuit,
            FrequencyRange(start_ghz=1.0, stop_ghz=5.0, points=101),
            _default_config(),
        )


def test_run_hbsolve_maps_singular_exception_to_numerical_error():
    circuit = CircuitDefinition(
        name="singular",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1": {"default": 10.0, "unit": "nH"},
            "C1": {"default": 1.0, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
            ("L1", "1", "0", "L1"),
            ("C1", "1", "0", "C1"),
        ],
    )

    def _raise_singular(*_):
        raise Exception(
            "TaskFailedException nested task error: LinearAlgebra.SingularException(11)"
        )

    simulator = _build_simulator(_raise_singular)

    with pytest.raises(
        RuntimeError,
        match="SimulationNumericalError: solver matrix became singular",
    ):
        simulator.run_hbsolve(
            circuit,
            FrequencyRange(start_ghz=1.0, stop_ghz=10.0, points=1001),
            _default_config(),
        )


def test_run_hbsolve_raises_input_error_for_unsupported_unit():
    circuit = CircuitDefinition(
        name="bad-unit",
        parameters={"R1": {"default": 50.0, "unit": "ohms"}},
        topology=[("P1", "1", "0", 1), ("R1", "1", "0", "R1")],
    )
    simulator = _build_simulator(lambda *_: pytest.fail("Julia should not be called"))

    with pytest.raises(ValueError, match="SimulationInputError: unsupported unit"):
        simulator.run_hbsolve(
            circuit,
            FrequencyRange(start_ghz=1.0, stop_ghz=3.0, points=51),
            _default_config(),
        )


def test_run_hbsolve_returns_result_when_julia_succeeds():
    circuit = CircuitDefinition(
        name="ok",
        parameters={"R50": {"default": 50.0, "unit": "Ohm"}},
        topology=[("P1", "1", "0", 1), ("R50", "1", "0", "R50")],
    )

    def _ok(*_):
        return {
            "frequencies_ghz": [1.0, 2.0],
            "s11_real": [0.1, 0.2],
            "s11_imag": [-0.1, -0.2],
        }

    simulator = _build_simulator(_ok)
    result = simulator.run_hbsolve(
        circuit,
        FrequencyRange(start_ghz=1.0, stop_ghz=2.0, points=2),
        _default_config(),
    )

    assert result.frequencies_ghz == [1.0, 2.0]
    assert result.s11_real == [0.1, 0.2]
    assert result.s11_imag == [-0.1, -0.2]


def test_run_hbsolve_rejects_source_port_not_declared_in_schema():
    circuit = CircuitDefinition(
        name="port-mismatch",
        parameters={"R50": {"default": 50.0, "unit": "Ohm"}},
        topology=[("P1", "1", "0", 1), ("R50", "1", "0", "R50")],
    )
    simulator = _build_simulator(lambda *_: pytest.fail("Julia should not be called"))
    config = SimulationConfig(
        pump_freq_ghz=5.0,
        sources=[DriveSourceConfig(pump_freq_ghz=5.0, port=2, current_amp=0.0)],
    )

    with pytest.raises(
        ValueError,
        match="SimulationInputError: source #1 targets port 2, but schema only defines ports: 1",
    ):
        simulator.run_hbsolve(
            circuit,
            FrequencyRange(start_ghz=1.0, stop_ghz=2.0, points=2),
            config,
        )


def test_run_hbsolve_forwards_hbsolve_config_parameters():
    circuit = CircuitDefinition(
        name="forward-config",
        parameters={"R50": {"default": 50.0, "unit": "Ohm"}},
        topology=[("P1", "1", "0", 1), ("R50", "1", "0", "R50")],
    )
    captured = {}

    def _capture(*args):
        captured["args"] = args
        return {
            "frequencies_ghz": [1.0],
            "s11_real": [0.1],
            "s11_imag": [0.0],
        }

    simulator = _build_simulator(_capture)
    config = SimulationConfig(
        pump_freq_ghz=6.5,
        n_modulation_harmonics=4,
        n_pump_harmonics=7,
        include_dc=True,
        enable_three_wave_mixing=True,
        enable_four_wave_mixing=False,
        max_intermod_order=9,
        max_iterations=200,
        f_tol=1e-9,
        line_search_switch_tol=1e-6,
        alpha_min=1e-5,
        sources=[
            DriveSourceConfig(pump_freq_ghz=4.65001, port=1, current_amp=2.5e-6),
            DriveSourceConfig(pump_freq_ghz=4.85001, port=1, current_amp=-1.2e-6),
        ],
    )

    simulator.run_hbsolve(
        circuit,
        FrequencyRange(start_ghz=1.0, stop_ghz=2.0, points=2),
        config,
    )

    args = captured["args"]
    assert args[5] == pytest.approx([4.65001, 4.85001])
    assert args[6] == pytest.approx([2.5e-6, -1.2e-6])
    assert args[7] == [1, 1]
    assert args[8] == [[1, 0], [0, 1]]
    assert args[9] == 4
    assert args[10] == 7
    assert args[11] is True
    assert args[12] is True
    assert args[13] is False
    assert args[14] == 9
    assert args[15] == 200
    assert args[16] == pytest.approx(1e-9)
    assert args[17] == pytest.approx(1e-6)
    assert args[18] == pytest.approx(1e-5)
