---
aliases:
  - "Simulation Guide"
tags:
  - diataxis/how-to
  - status/stable
  - topic/simulation
status: stable
owner: docs-team
audience: user
scope: "Circuit simulation tutorial index"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Circuit Simulation

This project uses [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) for superconducting circuit simulation.

## Choose Your Approach

We provide **two main approaches** for simulation, with Python as the primary method:

| Approach | Target Audience | Learning Curve |
|----------|-----------------|----------------|
| **Python CLI/API** | Most users | ⭐ Easy |
| **Native Julia** | Advanced users, extension development | ⭐⭐⭐ Advanced |

## Tutorial List

### Python API

| Tutorial | Description |
|----------|-------------|
| [Python API Guide](python-api.md) | Define circuits, set parameters, and run simulations in Python scripts |

### Native Julia

| Tutorial | Description |
|----------|-------------|
| [Native Julia Simulation](native-julia.md) | Use JosephsonCircuits.jl directly for simulation |

## Related Resources

- [CLI Reference: sc-simulate-lc](../../reference/cli/sc-simulate-lc.md) - Command options
- [Tutorial: LC Resonator](../../tutorials/lc-resonator.md) - End-to-end starter tutorial
- [Physics (Rebuild In Progress)](../../explanation/physics/index.en.md) - Physics section status
- [Extend Julia Functions](../extend/extend-julia-functions.md) - Contributor guide
