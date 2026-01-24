# Harmonic Balance Method

Harmonic Balance is a numerical method for solving the steady-state response of nonlinear circuits.

## Basic Concept

For circuits containing nonlinear elements (like Josephson Junctions), time-domain analysis is very time-consuming. The core idea of Harmonic Balance is:

1. **Assume**: The signal can be represented by a finite number of harmonics
2. **Transform**: Convert nonlinear equations to the frequency domain
3. **Solve**: Balance the harmonic components

## Why Use It?

| Method | Pros | Cons |
|--------|------|------|
| Time-domain | Intuitive | Slow for nonlinear circuits |
| Harmonic Balance | Fast steady-state | Must choose harmonics count |

## In JosephsonCircuits.jl

```julia
sol = hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs)
```

- `Nmodulationharmonics`: Number of modulation harmonics
- `Npumpharmonics`: Number of pump harmonics

!!! warning "Choosing Harmonic Count"
    More harmonics means more accurate but slower. Start with small values (e.g., 10) and increase until results converge.

## Further Reading

- [JosephsonCircuits.jl Documentation](https://github.com/QICKLab/JosephsonCircuits.jl)
