---
aliases:
- Nonlinearity and Unequal Level Spacing
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: Explain why Josephson nonlinearity creates anharmonic level spacing
version: v0.1.0
last_updated: 2026-02-16
updated_by: team
---

# Why Does Nonlinearity Create Unequal Level Spacing?

## Question This Page Answers

Why does Josephson nonlinearity make `|0\rangle\to|1\rangle` and `|1\rangle\to|2\rangle` transition energies different?

## Prerequisite Mapping

- Quantum: quantized oscillator and perturbative intuition
- Classical: potential curvature and small oscillations
- Electromagnetism: capacitive and inductive energy

## Physics Core

A linear LC oscillator has a quadratic potential and equally spaced levels. For a Josephson element,

$$
U_J(\varphi) = -E_J\cos\varphi.
$$

Expanding near a stable point yields higher-order terms:

$$
U(\varphi) \approx \frac{1}{2}k\varphi^2 + \alpha\varphi^4 + \cdots
$$

These non-quadratic terms create state-dependent energy corrections, producing anharmonic level spacing.

!!! note "Historical Context"
    Observable anharmonicity is a key reason superconducting circuits can function as controllable two-level systems (qubits).

## Engineering Mapping

- Anharmonicity controls transition selectivity.
- Too little anharmonicity increases leakage; too much can increase sensitivity to noise and bias errors.

## Limits and Approximations

- Local expansion is valid only near the operating point.
- Under strong drive, higher-order and multi-level effects become important.

## Cross-Document Navigation

- Previous: [Why Is Magnetic Flux Quantized?](why-flux-is-quantized.en.md)
- Next: [How Does Lagrangian Mechanics Connect to Circuit Physics?](lagrangian-mechanics-and-circuit-physics.en.md)
