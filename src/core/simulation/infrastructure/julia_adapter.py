"""
Julia Adapter for JosephsonCircuits.jl via JuliaCall.

This module provides the Python-Julia interoperability layer.
"""

from pathlib import Path

from core.simulation.domain.circuit import (
    CircuitDefinition,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
)

# Path to the Julia bridge file
_JULIA_BRIDGE_PATH = Path(__file__).parent / "hbsolve.jl"


class JuliaSimulator:
    """
    Adapter for calling JosephsonCircuits.jl from Python via JuliaCall.

    Usage:
        simulator = JuliaSimulator()
        result = simulator.run_hbsolve(circuit, freq_range, config)
    """

    def __init__(self) -> None:
        """Initialize the Julia environment and load JosephsonCircuits.jl."""
        self._jl = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of Julia runtime."""
        if self._initialized:
            return

        try:
            from juliacall import Main as jl  # type: ignore

            self._jl = jl

            # Load the Julia bridge file
            if _JULIA_BRIDGE_PATH.exists():
                jl.include(str(_JULIA_BRIDGE_PATH))
            else:
                # Fallback: load JosephsonCircuits directly
                jl.seval("using JosephsonCircuits")

            self._initialized = True
        except ImportError as e:
            msg = (
                "juliacall is not installed. "
                "Install it with: uv add juliacall\n"
                "Also ensure Julia and JosephsonCircuits.jl are installed."
            )
            raise ImportError(msg) from e

    def run_lc_simulation(
        self,
        inductance_nh: float,
        capacitance_pf: float,
        freq_range: FrequencyRange,
    ) -> SimulationResult:
        """
        Run a simple LC resonator simulation.

        Args:
            inductance_nh: Inductance in nanohenries.
            capacitance_pf: Capacitance in picofarads.
            freq_range: Frequency sweep configuration.

        Returns:
            SimulationResult with S11 data.
        """
        self._ensure_initialized()
        assert self._jl is not None  # Guaranteed by _ensure_initialized

        # Call Julia function
        result = self._jl.run_lc_simulation(
            float(inductance_nh),
            float(capacitance_pf),
            float(freq_range.start_ghz),
            float(freq_range.stop_ghz),
            int(freq_range.points),
        )

        # Convert Julia Dict to Python
        return SimulationResult(
            frequencies_ghz=list(result["frequencies_ghz"]),
            s11_real=list(result["s11_real"]),
            s11_imag=list(result["s11_imag"]),
        )

    def run_hbsolve(
        self,
        circuit: CircuitDefinition,
        freq_range: FrequencyRange,
        config: SimulationConfig,
    ) -> SimulationResult:
        """
        Run harmonic balance simulation for a custom circuit.

        Args:
            circuit: Circuit definition with topology and component values.
            freq_range: Frequency sweep range.
            config: Simulation configuration (harmonics, pump, etc.).

        Returns:
            SimulationResult with S11 data.
        """
        self._ensure_initialized()
        assert self._jl is not None  # Guaranteed by _ensure_initialized

        # Convert Python models to Julia-compatible format
        topology = [(elem[0], elem[1], elem[2], elem[3]) for elem in circuit.topology]

        component_values = {
            comp.name: comp.value * self._get_unit_multiplier(comp.unit)
            for comp in circuit.components
        }

        # Call Julia function
        result = self._jl.run_custom_simulation(
            topology,
            component_values,
            float(freq_range.start_ghz),
            float(freq_range.stop_ghz),
            int(freq_range.points),
        )

        return SimulationResult(
            frequencies_ghz=list(result["frequencies_ghz"]),
            s11_real=list(result["s11_real"]),
            s11_imag=list(result["s11_imag"]),
        )

    @staticmethod
    def _get_unit_multiplier(unit: str) -> float:
        """Convert unit string to multiplier."""
        unit_map = {
            "H": 1.0,
            "mH": 1e-3,
            "uH": 1e-6,
            "nH": 1e-9,
            "pH": 1e-12,
            "F": 1.0,
            "mF": 1e-3,
            "uF": 1e-6,
            "nF": 1e-9,
            "pF": 1e-12,
            "fF": 1e-15,
            "Ohm": 1.0,
            "kOhm": 1e3,
            "MOhm": 1e6,
        }
        return unit_map.get(unit, 1.0)
