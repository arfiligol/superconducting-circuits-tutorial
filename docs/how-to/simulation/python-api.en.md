---
aliases:
  - "Python Simulation API"
tags:
  - how-to
  - simulation
  - python
  - api
status: stable
owner: docs-team
audience: user
scope: "Python simulation API usage guide"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Python API Guide

This tutorial explains how to use the simulation API in Python scripts.

## Prerequisites

1. **uv environment installed**: `uv sync`
2. **Julia dependencies**: Automatically installed via `juliapkg` on first run

## Basic Usage

### Import Modules

```python
from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import (
    FrequencyRange,
    SimulationResult,
    CircuitDefinition,
    ComponentValue,
)
```

### Initialize Simulator

```python
# Simulator lazily initializes Julia environment on first call
simulator = JuliaSimulator()
```

!!! note
    First initialization may take several seconds as Julia and JosephsonCircuits.jl are loaded.

## LC Resonator Simulation

The simplest simulation approach:

```python
from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import FrequencyRange

simulator = JuliaSimulator()

# Define frequency range
freq_range = FrequencyRange(
    start_ghz=0.1,
    stop_ghz=5.0,
    points=100
)

# Run LC simulation
result = simulator.run_lc_simulation(
    inductance_nh=10.0,   # Inductance (nH)
    capacitance_pf=1.0,   # Capacitance (pF)
    freq_range=freq_range
)
```

## Result Processing

`SimulationResult` contains the following attributes:

```python
# Frequency array (GHz)
frequencies = result.frequencies_ghz  # List[float]

# S11 parameters
s11_real = result.s11_real  # List[float]
s11_imag = result.s11_imag  # List[float]

# Calculate magnitude and phase
import numpy as np

s11_complex = np.array(s11_real) + 1j * np.array(s11_imag)
s11_mag = np.abs(s11_complex)
s11_phase = np.angle(s11_complex)

# Find resonance frequency (S11 minimum)
resonance_idx = np.argmin(s11_mag)
resonance_freq = frequencies[resonance_idx]
print(f"Resonance frequency: {resonance_freq:.3f} GHz")
```

## Custom Circuits

For more complex circuit topologies, use the `run_hbsolve` method:

```python
from core.simulation.domain.circuit import (
    CircuitDefinition,
    ComponentValue,
    FrequencyRange,
    SimulationConfig,
)

# Define circuit components
components = [
    ComponentValue(name="L1", value=10.0, unit="nH"),
    ComponentValue(name="C1", value=1.0, unit="pF"),
    ComponentValue(name="R50", value=50.0, unit="Ohm"),
]

# Define topology (name, node1, node2, value_key)
topology = [
    ("P1", "1", "0", 1),       # Port
    ("R50", "1", "0", "R50"),  # Termination impedance
    ("L1", "1", "2", "L1"),    # Inductor
    ("C1", "2", "0", "C1"),    # Capacitor
]

# Create circuit definition
circuit = CircuitDefinition(
    name="Custom LC Resonator",
    topology=topology,
    components=components
)

# Frequency range
freq_range = FrequencyRange(start_ghz=0.1, stop_ghz=5.0, points=100)

# Simulation config (use defaults)
config = SimulationConfig()

# Run simulation
result = simulator.run_hbsolve(circuit, freq_range, config)
```

## Supported Units

`ComponentValue` supports the following units:

| Type | Supported Units |
|------|-----------------|
| Inductance | `H`, `mH`, `uH`, `nH`, `pH` |
| Capacitance | `F`, `mF`, `uF`, `nF`, `pF`, `fF` |
| Resistance | `Ohm`, `kOhm`, `MOhm` |

## Error Handling

```python
try:
    result = simulator.run_lc_simulation(
        inductance_nh=10.0,
        capacitance_pf=1.0,
        freq_range=freq_range
    )
except ImportError as e:
    print("juliacall not installed, run: uv add juliacall")
except Exception as e:
    print(f"Simulation error: {e}")
```

## Related Resources

- [LC Resonator Simulation](lc-resonator.md) - Getting started tutorial
- [Native Julia Simulation](native-julia.md) - Advanced techniques
- [Extend Julia Functions](../extend/extend-julia-functions.md) - Add new simulation types
