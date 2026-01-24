# Understanding hbsolve

`hbsolve` is the core function of JosephsonCircuits.jl, using the **Harmonic Balance** method to solve nonlinear circuits.

## Function Signature

```julia
hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs; kwargs...)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ws` | `Vector` | Signal frequencies (rad/s) |
| `wp` | `Tuple` | Pump frequencies (rad/s) |
| `sources` | `Vector` | Source definitions |
| `Nmodulationharmonics` | `Tuple` | Number of modulation harmonics |
| `Npumpharmonics` | `Tuple` | Number of pump harmonics |
| `circuit` | `Vector` | Circuit netlist |
| `circuitdefs` | `Dict` | Parameter values |

## Circuit Netlist Format

```julia
circuit = [
    ("element_name", "node+", "node-", symbol_or_value),
    ...
]
```

Common elements:

- `"P1"` — Port
- `"R"` — Resistor
- `"L"` — Inductor
- `"C"` — Capacitor
- `"LJ"` — Josephson Junction

## Return Value

`hbsolve` returns a solution object containing:

```julia
sol.linearized.S  # S-parameter function
sol.linearized.Z  # Z matrix
sol.linearized.w  # Frequency vector
```

### Extracting S11

```julia
S11 = sol.linearized.S(
    outputmode=(0,),
    outputport=1,
    inputmode=(0,),
    inputport=1,
    freqindex=:
)
```

## Tips

!!! tip "Performance Optimization"
    Reducing `Npumpharmonics` and `Nmodulationharmonics` speeds up computation but may affect accuracy.

!!! note "Using returnZ"
    Add `returnZ=true` to also get the impedance matrix for admittance calculations.
