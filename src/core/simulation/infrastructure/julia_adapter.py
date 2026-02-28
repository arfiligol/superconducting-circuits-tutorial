"""
Julia Adapter for JosephsonCircuits.jl via JuliaCall.

This module provides the Python-Julia interoperability layer.
"""

import sys
from pathlib import Path

from core.simulation.domain.circuit import (
    CircuitDefinition,
    DriveSourceConfig,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
)

# Path to the Julia bridge file
_JULIA_BRIDGE_PATH = Path(__file__).parent / "hbsolve.jl"
_REPO_ROOT = Path(__file__).resolve().parents[4]


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
            # Ensure subprocess workers discover repository-level `juliapkg.json`.
            repo_root = str(_REPO_ROOT)
            if repo_root not in sys.path:
                sys.path.append(repo_root)

            from juliacall import Main as jl  # type: ignore

            self._jl = jl

            # Load the Julia bridge file
            if _JULIA_BRIDGE_PATH.exists():
                try:
                    jl.include(str(_JULIA_BRIDGE_PATH))
                except Exception as e:
                    if "Package JosephsonCircuits not found" not in str(e):
                        raise

                    # Fallback for fresh subprocesses where Juliapkg env is not yet materialized.
                    jl.seval("import Pkg; Pkg.instantiate()")
                    try:
                        jl.include(str(_JULIA_BRIDGE_PATH))
                    except Exception as e_retry:
                        if "Package JosephsonCircuits not found" not in str(e_retry):
                            raise
                        jl.seval('import Pkg; Pkg.add("JosephsonCircuits")')
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
            circuit: Circuit definition with topology and parameter values.
            freq_range: Frequency sweep range.
            config: Simulation configuration (harmonics, pump, etc.).

        Returns:
            SimulationResult with S11 data.
        """
        self._ensure_initialized()
        assert self._jl is not None  # Guaranteed by _ensure_initialized

        self._validate_circuit_inputs(circuit)
        available_ports = self._extract_available_port_indices(circuit)
        sources = self._build_effective_sources(config)
        self._validate_solver_config(config, sources, available_ports)

        # Convert Python models to Julia-compatible format
        topology = [(elem[0], elem[1], elem[2], elem[3]) for elem in circuit.topology]

        component_values = {
            param_name: param_spec.default * self._get_unit_multiplier(param_spec.unit)
            for param_name, param_spec in circuit.parameters.items()
        }

        max_intermod_order = (
            config.max_intermod_order if config.max_intermod_order is not None else -1
        )

        try:
            # Call Julia function
            result = self._jl.run_custom_simulation(
                topology,
                component_values,
                float(freq_range.start_ghz),
                float(freq_range.stop_ghz),
                int(freq_range.points),
                [float(src.pump_freq_ghz) for src in sources],
                [float(src.current_amp) for src in sources],
                [int(src.port) for src in sources],
                self._build_source_mode_vectors(len(sources)),
                int(config.n_modulation_harmonics),
                int(config.n_pump_harmonics),
                bool(config.include_dc),
                bool(config.enable_three_wave_mixing),
                bool(config.enable_four_wave_mixing),
                int(max_intermod_order),
                int(config.max_iterations),
                float(config.f_tol),
                float(config.line_search_switch_tol),
                float(config.alpha_min),
            )
        except Exception as e:
            detail = str(e)
            if "Ports without resistors detected" in detail:
                raise ValueError(
                    "SimulationInputError: each port node must include a shunt resistor "
                    "to ground (for example 50 Ohm).\n\n"
                    f"Julia detail:\n{detail[:3000]}"
                ) from e
            if "SingularException" in detail:
                raise RuntimeError(
                    "SimulationNumericalError: solver matrix became singular. "
                    "This is usually due to ill-conditioned topology/value combinations "
                    "(for example floating nodes or problematic parallel branches).\n\n"
                    f"Julia detail:\n{detail[:3000]}"
                ) from e
            raise

        return SimulationResult(
            frequencies_ghz=list(result["frequencies_ghz"]),
            s11_real=list(result["s11_real"]),
            s11_imag=list(result["s11_imag"]),
        )

    @staticmethod
    def _validate_circuit_inputs(circuit: CircuitDefinition) -> None:
        """Validate basic circuit integrity before invoking Julia."""
        parameter_names = set(circuit.parameters)
        topology_value_refs: list[str] = []
        port_nodes: list[str] = []

        for comp_name, node1_raw, node2_raw, value_ref in circuit.topology:
            node1 = str(node1_raw)
            node2 = str(node2_raw)
            name_lower = comp_name.lower()

            if name_lower.startswith("p"):
                port_nodes.append(node1 if node1.lower() not in {"0", "gnd"} else node2)
                continue

            if not isinstance(value_ref, str):
                raise ValueError(
                    "SimulationInputError: non-port topology entries must use string "
                    f"value_ref. Got '{value_ref}' in element '{comp_name}'."
                )
            ref_name = value_ref
            topology_value_refs.append(ref_name)
            if ref_name not in parameter_names:
                raise ValueError(
                    f"SimulationInputError: topology references undefined parameter '{ref_name}'."
                )

        for port_node in port_nodes:
            has_shunt_resistor = any(
                comp_name.lower().startswith("r")
                and (
                    (str(node1_raw) == port_node and str(node2_raw).lower() in {"0", "gnd"})
                    or (str(node2_raw) == port_node and str(node1_raw).lower() in {"0", "gnd"})
                )
                for comp_name, node1_raw, node2_raw, _ in circuit.topology
            )
            if not has_shunt_resistor:
                raise ValueError(
                    "SimulationInputError: each port node needs a shunt resistor to ground "
                    f"(missing at node '{port_node}')."
                )

        if not topology_value_refs and circuit.parameters:
            raise ValueError(
                "SimulationInputError: no parameter references were found in topology."
            )

    @staticmethod
    def _extract_available_port_indices(circuit: CircuitDefinition) -> set[int]:
        """Collect declared port indices from circuit topology."""
        ports: set[int] = set()
        for comp_name, _, _, value_ref in circuit.topology:
            if not comp_name.lower().startswith("p"):
                continue

            port_index: int | None = None
            try:
                port_index = int(value_ref)
            except (TypeError, ValueError):
                digits = "".join(ch for ch in comp_name if ch.isdigit())
                if digits:
                    port_index = int(digits)

            if port_index is not None and port_index >= 1:
                ports.add(port_index)
        return ports

    @staticmethod
    def _build_effective_sources(config: SimulationConfig) -> list[DriveSourceConfig]:
        """Resolve sources list with fallback to legacy single-source fields."""
        if config.sources is not None:
            return list(config.sources)

        return [
            DriveSourceConfig(
                pump_freq_ghz=float(config.pump_freq_ghz),
                port=int(config.pump_port),
                current_amp=float(config.pump_current_amp),
            )
        ]

    @staticmethod
    def _build_source_mode_vectors(source_count: int) -> list[list[int]]:
        """Build one-hot mode vectors matching number of configured pump tones."""
        mode_vectors: list[list[int]] = []
        for idx in range(source_count):
            mode = [0] * source_count
            mode[idx] = 1
            mode_vectors.append(mode)
        return mode_vectors

    @staticmethod
    def _validate_solver_config(
        config: SimulationConfig,
        sources: list[DriveSourceConfig],
        available_ports: set[int],
    ) -> None:
        """Validate hbsolve controls before calling Julia."""
        JuliaSimulator._validate_solver_controls(config)
        if not sources:
            raise ValueError("SimulationInputError: at least one source is required.")

        for index, source in enumerate(sources, start=1):
            if source.pump_freq_ghz <= 0:
                raise ValueError(
                    f"SimulationInputError: source #{index} pump_freq_ghz must be > 0."
                )
            if source.port < 1:
                raise ValueError(f"SimulationInputError: source #{index} port must be >= 1.")
            if available_ports and source.port not in available_ports:
                ordered_ports = ", ".join(str(p) for p in sorted(available_ports))
                raise ValueError(
                    "SimulationInputError: source "
                    f"#{index} targets port {source.port}, but schema only defines ports: "
                    f"{ordered_ports}."
                )

    @staticmethod
    def _validate_solver_controls(config: SimulationConfig) -> None:
        """Validate shared (non-source) hbsolve controls."""
        if config.pump_freq_ghz <= 0:
            raise ValueError("SimulationInputError: pump_freq_ghz must be > 0.")
        if config.n_modulation_harmonics < 0:
            raise ValueError("SimulationInputError: n_modulation_harmonics must be >= 0.")
        if config.n_pump_harmonics < 0:
            raise ValueError("SimulationInputError: n_pump_harmonics must be >= 0.")
        if config.max_iterations < 1:
            raise ValueError("SimulationInputError: max_iterations must be >= 1.")
        if config.f_tol <= 0:
            raise ValueError("SimulationInputError: f_tol must be > 0.")
        if config.line_search_switch_tol <= 0:
            raise ValueError("SimulationInputError: line_search_switch_tol must be > 0.")
        if config.alpha_min <= 0:
            raise ValueError("SimulationInputError: alpha_min must be > 0.")
        if config.max_intermod_order is not None and config.max_intermod_order < 1:
            raise ValueError("SimulationInputError: max_intermod_order must be >= 1 or None.")

    @staticmethod
    def _get_unit_multiplier(unit: str) -> float:
        """Convert unit string to multiplier."""
        normalized = unit.strip().lower()
        unit_map = {
            "h": 1.0,
            "mh": 1e-3,
            "uh": 1e-6,
            "nh": 1e-9,
            "ph": 1e-12,
            "f": 1.0,
            "mf": 1e-3,
            "uf": 1e-6,
            "nf": 1e-9,
            "pf": 1e-12,
            "ff": 1e-15,
            "ohm": 1.0,
            "kohm": 1e3,
            "mohm": 1e6,
        }
        if normalized not in unit_map:
            allowed_units = ", ".join(sorted(unit_map.keys()))
            raise ValueError(
                f"SimulationInputError: unsupported unit '{unit}'. Allowed: {allowed_units}."
            )
        return unit_map[normalized]
