# First Simulation

Let's run your first superconducting circuit simulation!

## Goal

Simulate a simple LC resonator and observe its S11 response.

## Circuit Structure

```
     ┌───┐
Port─┤ L ├─┬─ GND
     └───┘ │
           C
           │
          GND
```

## Code

```julia title="examples/01_simple_lc/lc_resonator.jl"
using JosephsonCircuits

# Define units
const nH = 1e-9
const pF = 1e-12
const GHz = 1e9

# Define circuit topology
@variables L C R50

circuit = [
    ("P1", "1", "0", 1),      # Port 1
    ("R50", "1", "0", R50),   # 50Ω impedance
    ("L", "1", "2", L),       # Inductor
    ("C", "2", "0", C),       # Capacitor
]

# Circuit parameters
circuitdefs = Dict(
    L => 10nH,
    C => 1pF,
    R50 => 50,
)

# Frequency range
ws = 2π * (0.1:0.01:10) * GHz
wp = (2π * 5.0GHz,)
sources = [(mode=(1,), port=1, current=0.0)]

# Run simulation
sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)

# Extract S11
S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)
```

## Results

The simulation yields S11 parameters showing the LC resonator's frequency response. The resonance frequency is approximately:

$$f_0 = \frac{1}{2\pi\sqrt{LC}} \approx 1.59 \text{ GHz}$$

## Next Steps

- 👉 [Understanding hbsolve](understanding-hbsolve.md) — Learn more about the simulation function
- 👉 [LC Resonator Tutorial](../../tutorials/lc-resonator.md) — More detailed examples
