---
aliases:
- Why Flux Is Quantized
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: Explain the origin of flux quantization in superconducting loops
version: v0.1.0
last_updated: 2026-02-16
updated_by: team
---

# Why Is Magnetic Flux Quantized?

## Question This Page Answers

Why are allowed flux values in a superconducting closed loop not continuous, but constrained near integer multiples of the flux quantum `\Phi_0`?

## Prerequisite Mapping

- Quantum: single-valued wavefunction and phase
- Electromagnetism: vector potential `\mathbf{A}` and Stokes theorem
- Classical: closed-loop integrals and constraints

## Physics Core

With the superconducting order parameter

$$
\Psi(\mathbf{r}) = |\Psi(\mathbf{r})| e^{i\theta(\mathbf{r})},
$$

the gauge-invariant phase gradient is

$$
\nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A}.
$$

Integrating around a closed loop `C`, single-valuedness requires

$$
\oint_C \left(\nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A}\right)\cdot d\mathbf{l} = 2\pi n,
\quad n\in\mathbb{Z}.
$$

This leads to flux quantization (under common approximations):

$$
\Phi \approx n\Phi_0.
$$

!!! note "Historical Context"
    Flux quantization turned superconductivity as a macroscopic quantum state into a measurable fact, and became foundational for SQUID-based sensing.

## Engineering Mapping

- `\Phi/\Phi_0` sets the SQUID operating bias point.
- The quantization constraint defines allowed phase branches in loop dynamics.

## Limits and Approximations

- Clear quantization needs coherence and temperature conditions.
- In multi-junction loops, phase jumps across Josephson junctions must be included.

## Cross-Document Navigation

- Next: [Why Does Nonlinearity Create Unequal Level Spacing?](why-nonlinearity-makes-unequal-level-spacing.en.md)
- Task-first: [Flux Analysis](../../tutorials/flux-analysis.en.md)
