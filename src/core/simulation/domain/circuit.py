"""
Circuit Domain Models.

These Pydantic models represent circuit definitions that can be passed
to the Julia simulation engine via JuliaCall.
"""

from pydantic import BaseModel, Field


class ComponentValue(BaseModel):
    """A component value with units."""

    name: str = Field(description="Component name (e.g., 'L', 'C', 'R50')")
    value: float = Field(description="Numeric value")
    unit: str = Field(description="Unit string (e.g., 'nH', 'pF', 'Ohm')")


class CircuitDefinition(BaseModel):
    """
    Definition of a superconducting circuit for simulation.

    Example:
        circuit = CircuitDefinition(
            name="Simple LC",
            components=[
                ComponentValue(name="L", value=10.0, unit="nH"),
                ComponentValue(name="C", value=1.0, unit="pF"),
            ],
            topology=[
                ("P1", "1", "0", 1),
                ("R50", "1", "0", "R50"),
                ("L", "1", "2", "L"),
                ("C", "2", "0", "C"),
            ],
        )
    """

    name: str = Field(description="Circuit name for identification")
    components: list[ComponentValue] = Field(description="List of component values")
    topology: list[tuple[str, str, str, str | int]] = Field(
        description="Circuit topology as (name, node1, node2, value/ref)"
    )


class FrequencyRange(BaseModel):
    """Frequency sweep configuration."""

    start_ghz: float = Field(description="Start frequency in GHz")
    stop_ghz: float = Field(description="Stop frequency in GHz")
    points: int = Field(default=1000, description="Number of frequency points")


class SimulationConfig(BaseModel):
    """Configuration for hbsolve simulation."""

    pump_freq_ghz: float = Field(description="Pump frequency in GHz")
    n_modulation_harmonics: int = Field(default=10, description="Number of modulation harmonics")
    n_pump_harmonics: int = Field(default=20, description="Number of pump harmonics")


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
