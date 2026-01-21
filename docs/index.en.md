# Superconducting Circuits Tutorial

Welcome to the Superconducting Circuits Simulation Tutorial! This site uses [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) for circuit simulation.

## What is this?

This is a combined **learning** and **research** resource:

- 🎓 **Learn**: Start from basics and learn how to simulate superconducting circuits with JosephsonCircuits.jl
- 🔬 **Research**: Notes on circuit model behavior and package exploration
- 💻 **Practice**: Every tutorial has corresponding executable code

## Who is this for?

- Graduate students learning superconducting quantum circuit simulation
- Researchers using JosephsonCircuits.jl
- Anyone interested in JPA (Josephson Parametric Amplifier) and Qubit simulation

## Quick Start

1. [Installation](getting-started/installation.md) — Set up Julia and dependencies
2. [First Simulation](getting-started/first-simulation.md) — Run your first circuit simulation
3. [Understanding hbsolve](getting-started/understanding-hbsolve.md) — Learn the core function

## Tutorial Topics

| Topic | Description |
|-------|-------------|
| [LC Resonator](tutorials/lc-resonator.md) | The most basic circuit model |
| [Parameter Sweep](tutorials/parameter-sweep.md) | Single and multi-dimensional sweeps |

## Project Structure

```
superconducting-circuits-tutorial/
├── docs/          # Documentation (this website)
├── examples/      # Executable Julia examples
├── sandbox/       # Experimental area (not version controlled)
└── src/           # Shared utilities (ili_plot, etc.)
```
