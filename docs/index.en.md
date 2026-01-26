---
aliases:
  - "Superconducting Circuits Tutorial"
tags:
  - diataxis/reference
  - status/draft
---

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

## Getting Started

1. [Installation](how-to/getting-started/installation.md) — Set up Julia and dependencies
2. [First Simulation](how-to/getting-started/first-simulation.md) — Run your first circuit simulation
3. [Understanding hbsolve](how-to/getting-started/understanding-hbsolve.md) — Learn the core function

## Tutorial Topics

| Topic | Description |
|-------|-------------|
| [LC Resonator](tutorials/lc-resonator.md) | The most basic circuit model |
| [Parameter Sweep](tutorials/parameter-sweep.md) | Single and multi-dimensional sweeps |

## Project Structure

This project uses an **App-Centric Hybrid Architecture**. All core source code resides in `src/`.

### 1. Source Root (`src/`)
The polyglot source center:

- **`sc_analysis/`** (Python): Core analysis logic (Clean Architecture).
- **`sc_app/`** (Python): NiceGUI application interface.
- **`plotting.jl`** (Julia): Shared plotting utilities.

### 2. Interfaces
- **`scripts/`**: Python CLI scripts (invoke `src/sc_analysis`).
- **`examples/`**: Julia simulation and tutorial examples.

### 3. Documentation
- **`docs/`**: Documentation site (MkDocs).
