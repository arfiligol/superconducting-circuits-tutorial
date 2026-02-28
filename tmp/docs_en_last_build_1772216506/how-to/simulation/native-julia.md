---
aliases:
  - "Native Julia Simulation"
tags:
  - diataxis/how-to
  - status/stable
  - topic/simulation
  - topic/julia
  - topic/advanced
status: stable
owner: docs-team
audience: user
scope: "Native Julia simulation advanced tutorial"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Native Julia Simulation

This tutorial explains how to use JosephsonCircuits.jl directly for circuit simulation. Suitable for advanced users or developers extending functionality.

## When to Choose Native Julia?

| Situation | Recommended Approach |
|-----------|---------------------|
| Quick simulation, standard analysis | Python CLI/API |
| Complex circuits, custom components | **Native Julia** |
| Developing new simulation features | **Native Julia** |
| Performance-critical applications | **Native Julia** |

## Environment Setup

### Using Project Julia Environment

```bash
cd superconducting-circuits-tutorial
julia --project=.
```

### Load Package

```julia
using JosephsonCircuits
using Plots  # Optional, for plotting
```

## Basic Syntax

### Unit Definitions

```julia
# Common units
nH = 1e-9   # nanohenry
pF = 1e-12  # picofarad
fF = 1e-15  # femtofarad
GHz = 1e9   # gigahertz
MHz = 1e6   # megahertz
```

### Symbolic Variables

```julia
using JosephsonCircuits: @variables

@variables L C Cj Lj R50
```

### Circuit Definition

Circuits are defined as arrays of tuples, each with the format:
`(component_name, node1, node2, value)`

```julia
circuit = [
    ("P1", "1", "0", 1),       # Port (fixed value 1)
    ("R50", "1", "0", R50),    # Resistor
    ("L", "1", "2", L),        # Inductor
    ("C", "2", "0", C),        # Capacitor
]
```

### Parameter Values

```julia
circuitdefs = Dict(
    L => 10nH,
    C => 1pF,
    R50 => 50.0,
)
```

## Running Harmonic Balance

### Frequency Setup

```julia
# Frequency range
f_start, f_stop, n_points = 0.1GHz, 5GHz, 100
frequencies = range(f_start, f_stop, length=n_points)
ws = 2π .* frequencies  # Angular frequency
```

### Pump Setup

```julia
# Pump frequency and source settings
wp = (2π * 5GHz,)  # Pump frequency
sources = [(mode=(1,), port=1, current=0.0)]
```

### Run Simulation

```julia
# hbsolve parameters: (ws, wp, sources, Npumpharmonics, Nmodulationharmonics, circuit, circuitdefs)
sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)
```

## Extracting S-Parameters

```julia
# Extract S11
S11 = sol.linearized.S(
    outputmode=(0,),
    outputport=1,
    inputmode=(0,),
    inputport=1,
    freqindex=:
)

# Calculate magnitude and phase
S11_mag = abs.(S11)
S11_phase = angle.(S11)

# Find resonance
min_idx = argmin(S11_mag)
resonance_freq = frequencies[min_idx] / GHz
println("Resonance frequency: $(resonance_freq) GHz")
```

## Advanced: Josephson Junction

Simulating circuits with Josephson Junctions:

```julia
@variables Lj Cj Ic

# SQUID circuit example
circuit = [
    ("P1", "1", "0", 1),
    ("R50", "1", "0", 50.0),
    ("C", "1", "2", C),
    ("Lj", "2", "0", Lj),     # Junction inductance
    ("Cj", "2", "0", Cj),     # Junction capacitance
]

# Junction parameters
Φ0 = 2.067833848e-15  # Flux quantum
Ic = 1e-6             # Critical current (1 μA)
Lj0 = Φ0 / (2π * Ic)  # Josephson inductance

circuitdefs = Dict(
    C => 10fF,
    Lj => Lj0,
    Cj => 5fF,
)
```

## Parameter Sweep

```julia
# Sweep capacitance values
C_values = [0.5, 1.0, 1.5, 2.0] .* pF
results = []

for C_val in C_values
    circuitdefs[C] = C_val
    sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)
    S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)
    push!(results, (C=C_val, S11=S11))
end
```

## Multithreading Acceleration

```julia
using Base.Threads

# Check thread count
println("Using $(nthreads()) threads")

# Parallel sweep
Threads.@threads for i in 1:length(C_values)
    # ... simulation logic
end
```

Launch Julia with specified thread count:

```bash
julia --project=. --threads=auto
```

## Related Resources

- [JosephsonCircuits.jl Documentation](https://qicklab.github.io/JosephsonCircuits.jl/)
- [Tutorial: LC Resonator](../../tutorials/lc-resonator.md) - Starter tutorial
- [Extend Julia Functions](../extend/extend-julia-functions.md) - Contributor guide
