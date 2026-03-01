"""
Circuit Domain Models.

These Pydantic models represent circuit definitions that can be passed
to the Julia simulation engine via JuliaCall.
"""

import math

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
    mode_components: tuple[int, ...] | None = Field(
        default=None,
        description=(
            "Explicit hbsolve mode tuple for this source. "
            "Use (0,) for DC, (1,) for the first pump tone, or (1, 0)/(0, 1) for multi-pump."
        ),
    )


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
    port_indices: list[int] = Field(
        default_factory=lambda: [1],
        description="Available simulated port indices.",
    )
    s_parameter_real: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Real-part traces keyed by zero-mode S-parameter label (for example S21).",
    )
    s_parameter_imag: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Imag-part traces keyed by zero-mode S-parameter label (for example S21).",
    )
    mode_indices: list[tuple[int, ...]] = Field(
        default_factory=lambda: [(0,)],
        description="Available signal/idler mode tuples reported by hbsolve.",
    )
    s_parameter_mode_real: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Real-part traces keyed by mode-aware S-parameter label.",
    )
    s_parameter_mode_imag: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Imag-part traces keyed by mode-aware S-parameter label.",
    )
    z_parameter_mode_real: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Real-part traces keyed by mode-aware native Z-parameter label.",
    )
    z_parameter_mode_imag: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Imag-part traces keyed by mode-aware native Z-parameter label.",
    )
    y_parameter_mode_real: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Real-part traces keyed by mode-aware Y-parameter label.",
    )
    y_parameter_mode_imag: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Imag-part traces keyed by mode-aware Y-parameter label.",
    )
    qe_parameter_mode: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Mode-aware QE traces keyed by output/input mode+port label.",
    )
    qe_ideal_parameter_mode: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Mode-aware QEideal traces keyed by output/input mode+port label.",
    )
    cm_parameter_mode: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Mode-aware commutation traces keyed by output mode+port label.",
    )

    def _resolved_s_parameter_real(self) -> dict[str, list[float]]:
        """Return the real-part trace map with a guaranteed S11 fallback."""
        return self.s_parameter_real or {"S11": self.s11_real}

    def _resolved_s_parameter_imag(self) -> dict[str, list[float]]:
        """Return the imag-part trace map with a guaranteed S11 fallback."""
        return self.s_parameter_imag or {"S11": self.s11_imag}

    @staticmethod
    def normalize_mode(mode: tuple[int, ...] | list[int]) -> tuple[int, ...]:
        """Normalize any mode sequence to a canonical tuple of ints."""
        normalized = tuple(int(value) for value in mode)
        return normalized or (0,)

    @classmethod
    def mode_token(cls, mode: tuple[int, ...] | list[int]) -> str:
        """Encode a mode tuple into a stable string token."""
        normalized = cls.normalize_mode(mode)
        return ",".join(str(value) for value in normalized)

    @classmethod
    def parse_mode_token(cls, token: str) -> tuple[int, ...]:
        """Decode a canonical mode token back into a tuple."""
        cleaned = str(token).strip()
        if not cleaned:
            return (0,)
        return cls.normalize_mode(int(part.strip()) for part in cleaned.split(","))

    @property
    def available_port_indices(self) -> list[int]:
        """Return sorted available ports, derived from traces when not explicitly set."""
        normalized = sorted({int(port) for port in self.port_indices if int(port) >= 1})
        if normalized:
            return normalized

        detected_ports: set[int] = set()
        for label in self._resolved_s_parameter_real():
            parsed = self._parse_s_parameter_label(label)
            if parsed is None:
                continue
            detected_ports.update(parsed)
        return sorted(detected_ports) or [1]

    @property
    def available_mode_indices(self) -> list[tuple[int, ...]]:
        """Return sorted available signal/idler mode tuples."""

        def _mode_sort_key(mode: tuple[int, ...]) -> tuple[int, int, tuple[int, ...]]:
            return (0 if all(value == 0 for value in mode) else 1, sum(abs(v) for v in mode), mode)

        if self.mode_indices:
            unique_modes = {self.normalize_mode(mode) for mode in self.mode_indices}
            return sorted(unique_modes, key=_mode_sort_key)

        detected_modes: set[tuple[int, ...]] = set()
        for label in self.s_parameter_mode_real:
            parsed = self._parse_mode_trace_label(label)
            if parsed is None:
                continue
            output_mode, _, input_mode, _ = parsed
            detected_modes.add(output_mode)
            detected_modes.add(input_mode)
        return sorted(detected_modes, key=_mode_sort_key) or [(0,)]

    @property
    def available_s_parameter_labels(self) -> list[str]:
        """Return sorted available zero-mode S-parameter labels."""
        labels = set(self._resolved_s_parameter_real()) & set(self._resolved_s_parameter_imag())
        return sorted(labels) or ["S11"]

    @property
    def available_mode_s_parameter_labels(self) -> list[str]:
        """Return sorted available mode-aware S-parameter labels."""
        labels = set(self._resolved_mode_s_parameter_real()) & set(
            self._resolved_mode_s_parameter_imag()
        )
        return sorted(labels)

    @property
    def available_mode_z_parameter_labels(self) -> list[str]:
        """Return sorted available mode-aware native Z-parameter labels."""
        labels = set(self.z_parameter_mode_real) & set(self.z_parameter_mode_imag)
        return sorted(labels)

    @property
    def available_mode_y_parameter_labels(self) -> list[str]:
        """Return sorted available mode-aware Y-parameter labels."""
        labels = set(self.y_parameter_mode_real) & set(self.y_parameter_mode_imag)
        return sorted(labels)

    @property
    def available_mode_qe_labels(self) -> list[str]:
        """Return sorted available mode-aware QE labels."""
        return sorted(self.qe_parameter_mode)

    @property
    def available_mode_qe_ideal_labels(self) -> list[str]:
        """Return sorted available mode-aware QEideal labels."""
        return sorted(self.qe_ideal_parameter_mode)

    @property
    def available_mode_cm_labels(self) -> list[str]:
        """Return sorted available mode-aware CM labels."""
        return sorted(self.cm_parameter_mode)

    @staticmethod
    def _parse_s_parameter_label(label: str) -> tuple[int, int] | None:
        """Parse labels like S21 into (output_port, input_port)."""
        if not label.startswith("S"):
            return None
        digits = label[1:]
        if len(digits) != 2 or not digits.isdigit():
            return None
        output_port = int(digits[0])
        input_port = int(digits[1])
        if output_port < 1 or input_port < 1:
            return None
        return (output_port, input_port)

    @staticmethod
    def _trace_label(output_port: int, input_port: int) -> str:
        """Build the canonical zero-mode trace label."""
        return f"S{int(output_port)}{int(input_port)}"

    @classmethod
    def _mode_trace_label(
        cls,
        output_mode: tuple[int, ...] | list[int],
        output_port: int,
        input_mode: tuple[int, ...] | list[int],
        input_port: int,
    ) -> str:
        """Build the canonical mode-aware trace label."""
        return (
            f"om={cls.mode_token(output_mode)}|op={int(output_port)}|"
            f"im={cls.mode_token(input_mode)}|ip={int(input_port)}"
        )

    @classmethod
    def _parse_mode_trace_label(
        cls,
        label: str,
    ) -> tuple[tuple[int, ...], int, tuple[int, ...], int] | None:
        """Parse a mode-aware trace label into output/input modes and ports."""
        parts = str(label).split("|")
        if len(parts) != 4:
            return None
        try:
            part_map = {
                segment.split("=", maxsplit=1)[0]: segment.split("=", maxsplit=1)[1]
                for segment in parts
            }
            output_mode = cls.parse_mode_token(part_map["om"])
            output_port = int(part_map["op"])
            input_mode = cls.parse_mode_token(part_map["im"])
            input_port = int(part_map["ip"])
        except (KeyError, ValueError, IndexError):
            return None
        return (output_mode, output_port, input_mode, input_port)

    @classmethod
    def _cm_trace_label(
        cls,
        output_mode: tuple[int, ...] | list[int],
        output_port: int,
    ) -> str:
        """Build the canonical mode-aware CM label."""
        return f"om={cls.mode_token(output_mode)}|op={int(output_port)}"

    @classmethod
    def _parse_cm_trace_label(cls, label: str) -> tuple[tuple[int, ...], int] | None:
        """Parse a mode-aware commutation label."""
        parts = str(label).split("|")
        if len(parts) != 2:
            return None
        try:
            part_map = {
                segment.split("=", maxsplit=1)[0]: segment.split("=", maxsplit=1)[1]
                for segment in parts
            }
            output_mode = cls.parse_mode_token(part_map["om"])
            output_port = int(part_map["op"])
        except (KeyError, ValueError, IndexError):
            return None
        return (output_mode, output_port)

    def _resolved_mode_s_parameter_real(self) -> dict[str, list[float]]:
        """Return the mode-aware real-part S map with a zero-mode fallback."""
        if self.s_parameter_mode_real:
            return self.s_parameter_mode_real

        zero_mode = (0,)
        return {
            self._mode_trace_label(zero_mode, output_port, zero_mode, input_port): (
                self.get_s_parameter_real(output_port, input_port)
            )
            for output_port in self.available_port_indices
            for input_port in self.available_port_indices
            if self._trace_label(output_port, input_port) in self.available_s_parameter_labels
        }

    def _resolved_mode_s_parameter_imag(self) -> dict[str, list[float]]:
        """Return the mode-aware imag-part S map with a zero-mode fallback."""
        if self.s_parameter_mode_imag:
            return self.s_parameter_mode_imag

        zero_mode = (0,)
        return {
            self._mode_trace_label(zero_mode, output_port, zero_mode, input_port): (
                self.get_s_parameter_imag(output_port, input_port)
            )
            for output_port in self.available_port_indices
            for input_port in self.available_port_indices
            if self._trace_label(output_port, input_port) in self.available_s_parameter_labels
        }

    def get_s_parameter_real(self, output_port: int = 1, input_port: int = 1) -> list[float]:
        """Return the real part of the requested zero-mode S-parameter."""
        label = self._trace_label(output_port, input_port)
        return self.get_s_parameter_real_by_label(label)

    def get_s_parameter_real_by_label(self, label: str) -> list[float]:
        """Return the real part of a zero-mode S-parameter by canonical label."""
        trace_map = self._resolved_s_parameter_real()
        if label in trace_map:
            return trace_map[label]
        if label == "S11":
            return self.s11_real
        raise KeyError(f"S-parameter trace '{label}' is not available.")

    def get_s_parameter_imag(self, output_port: int = 1, input_port: int = 1) -> list[float]:
        """Return the imaginary part of the requested zero-mode S-parameter."""
        label = self._trace_label(output_port, input_port)
        return self.get_s_parameter_imag_by_label(label)

    def get_s_parameter_imag_by_label(self, label: str) -> list[float]:
        """Return the imaginary part of a zero-mode S-parameter by canonical label."""
        trace_map = self._resolved_s_parameter_imag()
        if label in trace_map:
            return trace_map[label]
        if label == "S11":
            return self.s11_imag
        raise KeyError(f"S-parameter trace '{label}' is not available.")

    def get_s_parameter_complex(
        self,
        output_port: int = 1,
        input_port: int = 1,
    ) -> list[complex]:
        """Return the requested complex zero-mode S-parameter trace."""
        return self.get_mode_s_parameter_complex((0,), output_port, (0,), input_port)

    def get_mode_s_parameter_real(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Return the real part of the requested mode-aware S-parameter."""
        label = self._mode_trace_label(output_mode, output_port, input_mode, input_port)
        trace_map = self._resolved_mode_s_parameter_real()
        if label in trace_map:
            return trace_map[label]
        raise KeyError(f"Mode-aware S trace '{label}' is not available.")

    def get_mode_s_parameter_imag(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Return the imaginary part of the requested mode-aware S-parameter."""
        label = self._mode_trace_label(output_mode, output_port, input_mode, input_port)
        trace_map = self._resolved_mode_s_parameter_imag()
        if label in trace_map:
            return trace_map[label]
        raise KeyError(f"Mode-aware S trace '{label}' is not available.")

    def get_mode_s_parameter_complex(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[complex]:
        """Return the requested complex mode-aware S-parameter trace."""
        return [
            complex(r, i)
            for r, i in zip(
                self.get_mode_s_parameter_real(output_mode, output_port, input_mode, input_port),
                self.get_mode_s_parameter_imag(output_mode, output_port, input_mode, input_port),
                strict=False,
            )
        ]

    def get_s_parameter_magnitude(
        self,
        output_port: int = 1,
        input_port: int = 1,
    ) -> list[float]:
        """Calculate |Sij| for the selected trace."""
        return self.get_mode_s_parameter_magnitude((0,), output_port, (0,), input_port)

    def get_mode_s_parameter_magnitude(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Calculate |S| for the selected mode-aware trace."""
        return [
            math.sqrt(r**2 + i**2)
            for r, i in zip(
                self.get_mode_s_parameter_real(output_mode, output_port, input_mode, input_port),
                self.get_mode_s_parameter_imag(output_mode, output_port, input_mode, input_port),
                strict=False,
            )
        ]

    def get_s_parameter_db(
        self,
        output_port: int = 1,
        input_port: int = 1,
    ) -> list[float]:
        """Calculate 20*log10(|Sij|) for the selected trace."""
        return self.get_mode_s_parameter_db((0,), output_port, (0,), input_port)

    def get_mode_s_parameter_db(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Calculate 20*log10(|S|) for the selected mode-aware trace."""
        values: list[float] = []
        for magnitude in self.get_mode_s_parameter_magnitude(
            output_mode,
            output_port,
            input_mode,
            input_port,
        ):
            values.append(20.0 * math.log10(max(magnitude, 1e-15)))
        return values

    def get_s_parameter_phase_deg(
        self,
        output_port: int = 1,
        input_port: int = 1,
    ) -> list[float]:
        """Calculate phase(Sij) in degrees."""
        return self.get_mode_s_parameter_phase_deg((0,), output_port, (0,), input_port)

    def get_mode_s_parameter_phase_deg(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Calculate phase(S) in degrees for the selected mode-aware trace."""
        return [
            math.degrees(math.atan2(i, r))
            for r, i in zip(
                self.get_mode_s_parameter_real(output_mode, output_port, input_mode, input_port),
                self.get_mode_s_parameter_imag(output_mode, output_port, input_mode, input_port),
                strict=False,
            )
        ]

    def get_gain_linear(self, output_port: int = 1, input_port: int = 1) -> list[float]:
        """Calculate power gain as |Sij|^2."""
        return self.get_mode_gain_linear((0,), output_port, (0,), input_port)

    def get_mode_gain_linear(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Calculate power gain as |S|^2 for the selected mode-aware trace."""
        magnitudes = self.get_mode_s_parameter_magnitude(
            output_mode,
            output_port,
            input_mode,
            input_port,
        )
        return [magnitude**2 for magnitude in magnitudes]

    def get_gain_db(self, output_port: int = 1, input_port: int = 1) -> list[float]:
        """Calculate gain in dB as 10*log10(|Sij|^2)."""
        return self.get_mode_gain_db((0,), output_port, (0,), input_port)

    def get_mode_gain_db(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Calculate gain in dB as 10*log10(|S|^2) for the selected mode-aware trace."""
        values: list[float] = []
        for gain in self.get_mode_gain_linear(output_mode, output_port, input_mode, input_port):
            values.append(10.0 * math.log10(max(gain, 1e-30)))
        return values

    def _get_mode_complex_trace(
        self,
        *,
        real_map: dict[str, list[float]],
        imag_map: dict[str, list[float]],
        label: str,
        family_name: str,
    ) -> list[complex]:
        """Resolve a complex-valued mode-aware trace from parallel real/imag maps."""
        if label not in real_map or label not in imag_map:
            raise KeyError(f"Mode-aware {family_name} trace '{label}' is not available.")
        return [complex(r, i) for r, i in zip(real_map[label], imag_map[label], strict=False)]

    def get_mode_z_parameter_complex(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[complex]:
        """Return the native mode-aware Z-parameter trace."""
        label = self._mode_trace_label(output_mode, output_port, input_mode, input_port)
        return self._get_mode_complex_trace(
            real_map=self.z_parameter_mode_real,
            imag_map=self.z_parameter_mode_imag,
            label=label,
            family_name="Z",
        )

    def get_mode_y_parameter_complex(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[complex]:
        """Return the mode-aware Y-parameter trace."""
        label = self._mode_trace_label(output_mode, output_port, input_mode, input_port)
        return self._get_mode_complex_trace(
            real_map=self.y_parameter_mode_real,
            imag_map=self.y_parameter_mode_imag,
            label=label,
            family_name="Y",
        )

    def get_mode_qe(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Return the mode-aware QE trace."""
        label = self._mode_trace_label(output_mode, output_port, input_mode, input_port)
        if label in self.qe_parameter_mode:
            return self.qe_parameter_mode[label]
        raise KeyError(f"Mode-aware QE trace '{label}' is not available.")

    def get_mode_qe_ideal(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
        input_mode: tuple[int, ...] | list[int] = (0,),
        input_port: int = 1,
    ) -> list[float]:
        """Return the mode-aware ideal QE trace."""
        label = self._mode_trace_label(output_mode, output_port, input_mode, input_port)
        if label in self.qe_ideal_parameter_mode:
            return self.qe_ideal_parameter_mode[label]
        raise KeyError(f"Mode-aware QEideal trace '{label}' is not available.")

    def get_mode_cm(
        self,
        output_mode: tuple[int, ...] | list[int] = (0,),
        output_port: int = 1,
    ) -> list[float]:
        """Return the mode-aware commutation trace."""
        label = self._cm_trace_label(output_mode, output_port)
        if label in self.cm_parameter_mode:
            return self.cm_parameter_mode[label]
        raise KeyError(f"Mode-aware CM trace '{label}' is not available.")

    @property
    def s11_complex(self) -> list[complex]:
        """Return complex S11 values."""
        return self.get_s_parameter_complex(1, 1)

    @property
    def s11_magnitude(self) -> list[float]:
        """Calculate |S11| magnitude."""
        return self.get_s_parameter_magnitude(1, 1)

    @property
    def s11_db(self) -> list[float]:
        """Calculate 20*log10(|S11|)."""
        return self.get_s_parameter_db(1, 1)

    @property
    def s11_phase_deg(self) -> list[float]:
        """Calculate S11 phase in degrees."""
        return self.get_s_parameter_phase_deg(1, 1)

    @property
    def return_gain_linear(self) -> list[float]:
        """Calculate return gain as |S11|^2."""
        return self.get_gain_linear(1, 1)

    @property
    def return_gain_db(self) -> list[float]:
        """Calculate return gain in dB as 10*log10(|S11|^2)."""
        return self.get_gain_db(1, 1)

    def calculate_input_impedance_ohm(
        self,
        reference_impedance_ohm: float = 50.0,
        port: int = 1,
    ) -> list[complex]:
        """Convert Sii to input impedance using a real reference impedance."""
        try:
            return self.get_mode_z_parameter_complex((0,), port, (0,), port)
        except KeyError:
            pass

        epsilon = 1e-12
        values: list[complex] = []

        for s11 in self.get_s_parameter_complex(port, port):
            denominator = 1.0 - s11
            if abs(denominator) <= epsilon:
                values.append(complex(float("nan"), float("nan")))
                continue
            values.append(reference_impedance_ohm * ((1.0 + s11) / denominator))

        return values

    def calculate_input_admittance_s(
        self,
        reference_impedance_ohm: float = 50.0,
        port: int = 1,
    ) -> list[complex]:
        """Convert Sii to input admittance using a real reference impedance."""
        try:
            return self.get_mode_y_parameter_complex((0,), port, (0,), port)
        except KeyError:
            pass

        epsilon = 1e-18
        values: list[complex] = []

        for impedance in self.calculate_input_impedance_ohm(
            reference_impedance_ohm,
            port=port,
        ):
            if not (impedance.real == impedance.real and impedance.imag == impedance.imag):
                values.append(complex(float("nan"), float("nan")))
                continue
            if abs(impedance) <= epsilon:
                values.append(complex(float("nan"), float("nan")))
                continue
            values.append(1.0 / impedance)

        return values
