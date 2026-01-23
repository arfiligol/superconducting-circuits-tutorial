# Parameter Sweep

Learn how to systematically sweep circuit parameters — an important technique for analyzing circuit behavior.

## Single-Dimensional Sweep

Sweep a single parameter to observe its effect on circuit response.

### Example: Sweeping Inductance

```julia title="examples/02_parameter_sweep/single_sweep.jl"
using JosephsonCircuits
using PlotlyJS

const nH = 1e-9
const pF = 1e-12
const GHz = 1e9

@variables L C R50

circuit = [
    ("P1", "1", "0", 1),
    ("R50", "1", "0", R50),
    ("L", "1", "2", L),
    ("C", "2", "0", C),
]

# Base parameters
base_defs = Dict(C => 1pF, R50 => 50)

# Sweep range
L_values = (5:1:15) * nH

# Simulation settings
ws = 2π * (0.1:0.01:10) * GHz
wp = (2π * 5.0GHz,)
sources = [(mode=(1,), port=1, current=0.0)]

# Store results
traces = []

for L_val in L_values
    defs = merge(base_defs, Dict(L => L_val))
    sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, defs)

    freqs = sol.linearized.w / (2π * GHz)
    S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)

    push!(traces, scatter(
        x=freqs,
        y=rad2deg.(angle.(S11)),
        mode="lines",
        name="L = $(round(L_val/nH, digits=1)) nH"
    ))
end

plot(traces)
```

## Multi-Dimensional Sweep

Sweep multiple parameters simultaneously.

### Example: Sweeping L and C

```julia title="examples/02_parameter_sweep/multi_sweep.jl"
using JosephsonCircuits
using DataFrames

const nH = 1e-9
const pF = 1e-12
const GHz = 1e9

# Sweep grid
L_values = [5, 10, 15] * nH
C_values = [0.5, 1.0, 1.5] * pF

# Results table
results = DataFrame(L_nH=Float64[], C_pF=Float64[], f0_GHz=Float64[])

for L_val in L_values
    for C_val in C_values
        # Theoretical resonance frequency
        f0 = 1 / (2π * sqrt(L_val * C_val)) / GHz

        push!(results, (L_val/nH, C_val/pF, f0))
    end
end

println(results)
```

## Using ili_plot

The project provides the `ili_plot` utility to simplify PlotlyJS plotting:

```julia
include("src/plotting.jl")

# After collecting all traces
ili_plot(
    traces,
    "S11 Phase vs Frequency",
    "Frequency (GHz)",
    "Phase (deg)",
    "Inductance"
)
```

## Next Steps

👉 [Plotting Utilities ili_plot](../reference/utilities.md) — Learn more about plotting tools
