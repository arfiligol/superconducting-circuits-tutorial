---
aliases:
  - "LC Resonator Simulation"
tags:
  - how-to
  - simulation
  - tutorial
status: stable
owner: docs-team
audience: user
scope: "LC resonator simulation tutorial"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# LC Resonator Simulation

This tutorial introduces how to simulate a simple LC resonator and analyze its S-parameter response.

## Background

The LC resonator is the most basic component in superconducting circuits. Its resonance frequency is determined by the inductance (L) and capacitance (C):

$$
f_0 = \frac{1}{2\pi\sqrt{LC}}
$$

For example, a resonator with L = 10 nH and C = 1 pF has a resonance frequency of approximately 1.59 GHz.

## Method A: Python CLI (Recommended)

The simplest approach is to use the CLI tool `sc-simulate-lc`:

```bash
# Simulate an LC resonator with L=10nH, C=1pF
# Frequency range: 0.1 - 5 GHz, 100 points
uv run sc-simulate-lc -L 10 -C 1 --start 0.1 --stop 5 --points 100
```

**Expected Output**:

```
Simulating LC resonator: L=10.0 nH, C=1.0 pF
Frequency range: 0.1 - 5.0 GHz (100 points)

Expected resonance: 1.592 GHz
Simulation complete: 100 points
Resonance found at: X.XXX GHz
```

### Option Reference

| Option | Description | Default |
|--------|-------------|---------|
| `-L` | Inductance (nH) | Required |
| `-C` | Capacitance (pF) | Required |
| `--start` | Start frequency (GHz) | 0.1 |
| `--stop` | Stop frequency (GHz) | 10.0 |
| `--points` | Number of frequency points | 100 |
| `--output` | Output JSON file path | None |

## Method B: Python API

For more complex operations in Python scripts:

```python
from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import FrequencyRange

# Initialize simulator
simulator = JuliaSimulator()

# Define frequency range
freq_range = FrequencyRange(
    start_ghz=0.1,
    stop_ghz=5.0,
    points=100
)

# Run simulation
result = simulator.run_lc_simulation(
    inductance_nh=10.0,
    capacitance_pf=1.0,
    freq_range=freq_range
)

# Access results
print(f"Frequency points: {len(result.frequencies_ghz)}")
print(f"S11 data: {result.s11_real[:5]}...")  # First 5 points
```

For detailed API documentation, see [Python API Guide](python-api.md).

## Method C: Native Julia

For users familiar with Julia, you can use JosephsonCircuits.jl directly:

```julia
using JosephsonCircuits

# Units
nH, pF, GHz = 1e-9, 1e-12, 1e9

# Define circuit
@variables L C R50
circuit = [
    ("P1", "1", "0", 1),       # Port 1
    ("R50", "1", "0", R50),    # 50Ω impedance
    ("L", "1", "2", L),        # Inductor
    ("C", "2", "0", C),        # Capacitor
]

circuitdefs = Dict(
    L => 10nH,
    C => 1pF,
    R50 => 50.0,
)

# Frequency sweep
frequencies = range(0.1, 5, length=100) .* GHz
ws = 2π .* frequencies

# Run Harmonic Balance
wp = (2π * 5GHz,)
sources = [(mode=(1,), port=1, current=0.0)]
sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)

# Extract S11
S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)
```

For detailed instructions, see [Native Julia Simulation](native-julia.md).

## Interpreting Results

Simulation results include S11 parameters:

- **S11 Magnitude**: Minimum (dip) at resonance frequency
- **S11 Phase**: Sharp transition at resonance

## Next Steps

- [Python API Guide](python-api.md) - Custom circuit topologies
- [Native Julia Simulation](native-julia.md) - Advanced simulation techniques
- [CLI Reference](../../reference/cli/sc-simulate-lc.md) - Complete option reference
