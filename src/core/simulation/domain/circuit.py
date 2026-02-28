"""
Circuit Domain Models.

These Pydantic models represent circuit definitions that can be passed
to the Julia simulation engine via JuliaCall.
"""

from pydantic import BaseModel, Field


class ParameterSpec(BaseModel):
    """Parameter specification referenced by topology value_ref."""

    default: float = Field(description="Default numeric value")
    unit: str = Field(description="Unit string (e.g., 'nH', 'pF', 'Ohm')")
    sweepable: bool = Field(default=True, description="Whether this parameter is sweepable")


class CircuitDefinition(BaseModel):
    """
    Definition of a superconducting circuit for simulation.

    Example:
        circuit = CircuitDefinition(
            name="Simple LC",
            parameters={
                "R50": ParameterSpec(default=50.0, unit="Ohm"),
                "L1": ParameterSpec(default=10.0, unit="nH"),
                "C1": ParameterSpec(default=1.0, unit="pF"),
            },
            topology=[
                ("P1", "1", "0", 1),
                ("R1", "1", "0", "R50"),
                ("L1", "1", "2", "L1"),
                ("C1", "2", "0", "C1"),
            ],
        )
    """

    name: str = Field(description="Circuit name for identification")
    parameters: dict[str, ParameterSpec] = Field(
        description="Parameter map for topology value references"
    )
    topology: list[tuple[str, str, str, str | int]] = Field(
        description="Circuit topology as (name, node1, node2, value_ref/port_index)"
    )


class FrequencyRange(BaseModel):
    """Frequency sweep configuration."""

    start_ghz: float = Field(description="Start frequency in GHz")
    stop_ghz: float = Field(description="Stop frequency in GHz")
    points: int = Field(default=1000, description="Number of frequency points")


class DriveSourceConfig(BaseModel):
    """Single hbsolve source specification."""

    pump_freq_ghz: float = Field(default=5.0, description="Pump frequency for this source (GHz).")
    port: int = Field(default=1, description="Source port index.")
    current_amp: float = Field(default=0.0, description="Source current amplitude in A.")


class SimulationConfig(BaseModel):
    """Configuration for hbsolve simulation."""

    pump_freq_ghz: float = Field(default=5.0, description="Pump frequency in GHz")
    pump_current_amp: float = Field(
        default=0.0,
        description="Legacy single-source current amplitude in A (used when sources is empty).",
    )
    pump_port: int = Field(
        default=1,
        description="Legacy single-source port index (used when sources is empty).",
    )
    pump_mode_index: int = Field(
        default=1,
        description="Legacy single-source mode index (used when sources is empty).",
    )
    n_modulation_harmonics: int = Field(default=10, description="Number of modulation harmonics")
    n_pump_harmonics: int = Field(default=20, description="Number of pump harmonics")
    sources: list[DriveSourceConfig] | None = Field(
        default=None,
        description=(
            "Drive source list passed to hbsolve. If omitted, a single legacy source "
            "(pump_freq_ghz, pump_port, pump_current_amp) is used."
        ),
    )
    include_dc: bool = Field(default=False, description="Include DC term in harmonic solve")
    enable_three_wave_mixing: bool = Field(default=False, description="Enable 3-wave mixing")
    enable_four_wave_mixing: bool = Field(default=True, description="Enable 4-wave mixing")
    max_intermod_order: int | None = Field(
        default=None,
        description="Maximum intermodulation order (None means infinite).",
    )
    max_iterations: int = Field(default=1000, description="Maximum nonlinear solver iterations")
    f_tol: float = Field(default=1e-8, description="Nonlinear solver tolerance")
    line_search_switch_tol: float = Field(
        default=1e-5,
        description="Switch-off line search tolerance",
    )
    alpha_min: float = Field(default=1e-4, description="Minimum line-search alpha")


class SimulationResult(BaseModel):
    """Result from a circuit simulation."""

    frequencies_ghz: list[float] = Field(description="Frequency points in GHz")
    s11_real: list[float] = Field(description="Real part of S11")
    s11_imag: list[float] = Field(description="Imaginary part of S11")

    @property
    def s11_magnitude(self) -> list[float]:
        """Calculate |S11| magnitude."""
        import math

        return [math.sqrt(r**2 + i**2) for r, i in zip(self.s11_real, self.s11_imag, strict=False)]

    @property
    def s11_phase_deg(self) -> list[float]:
        """Calculate S11 phase in degrees."""
        import math

        return [
            math.degrees(math.atan2(i, r))
            for r, i in zip(self.s11_real, self.s11_imag, strict=False)
        ]
