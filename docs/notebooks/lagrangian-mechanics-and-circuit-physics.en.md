---
aliases:
- Lagrangian Mechanics and Circuit Physics
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: Explain how Lagrangian mechanics maps onto superconducting circuits
version: v0.1.0
last_updated: 2026-02-16
updated_by: team
---

# How Does Lagrangian Mechanics Connect to Circuit Physics?

## Question This Page Answers

Why can a circuit be written with a Lagrangian, similar to a mechanical system, and then quantized?

## Prerequisite Mapping

- Classical: Lagrange equations and generalized coordinates
- Electromagnetism: capacitive and inductive energy
- Quantum: canonical quantization

## Physics Core

Using node-flux variables `\phi_i`, a common form is

$$
\mathcal{L}(\{\phi_i\},\{\dot\phi_i\}) = T(\dot\phi) - U(\phi),
$$

where

- `T` comes from the capacitance network (kinetic-like term)
- `U` comes from inductive and Josephson potentials

With conjugate momentum

$$
q_i = \frac{\partial \mathcal{L}}{\partial \dot\phi_i},
$$

we build the Hamiltonian and quantize the circuit model.

!!! note "Historical Context"
    The Lagrangian/Hamiltonian circuit formalism created a shared language between circuit design and quantum-system modeling.

## Engineering Mapping

- Circuit parameters (C, L, EJ) map directly to mode frequencies and couplings.
- Coordinate choice (node flux vs loop flux) changes model compactness and numerical behavior.

## Limits and Approximations

- Lumped-element assumptions require component sizes much smaller than relevant wavelengths.
- Distributed and packaging effects need extra treatment at high frequency or large geometry.

## Cross-Document Navigation

- Previous: [Why Does Nonlinearity Create Unequal Level Spacing?](why-nonlinearity-makes-unequal-level-spacing.en.md)
- Next: [Why Can SQUIDs Control Nonlinear Inductance?](squid-controls-nonlinear-inductance.en.md)
- Task-first: [SQUID Fitting](../../how-to/fit-model/squid.en.md)
