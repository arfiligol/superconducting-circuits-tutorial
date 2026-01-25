"""
Simulation Use Cases.

This module orchestrates the simulation workflow.
"""

from core.simulation.domain.circuit import (
    CircuitDefinition,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
)
from core.simulation.infrastructure.julia_adapter import JuliaSimulator


def run_simulation(
    circuit: CircuitDefinition,
    freq_range: FrequencyRange,
    config: SimulationConfig | None = None,
) -> SimulationResult:
    """
    Run a circuit simulation.

    This is the main entry point for simulation use cases.

    Args:
        circuit: Circuit definition.
        freq_range: Frequency sweep range.
        config: Optional simulation config. Defaults to sensible values.

    Returns:
        SimulationResult with S-parameter data.
    """
    if config is None:
        config = SimulationConfig(
            pump_freq_ghz=5.0,
            n_modulation_harmonics=10,
            n_pump_harmonics=20,
        )

    simulator = JuliaSimulator()
    return simulator.run_hbsolve(circuit, freq_range, config)
