---
aliases:
- SQUID Control of Nonlinear Inductance
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: Explain why a SQUID can tune effective Josephson inductance
version: v0.1.0
last_updated: 2026-02-16
updated_by: team
---

# Why Can SQUIDs Control Nonlinear Inductance?

## Question This Page Answers

Why can external flux bias tune SQUID effective inductance and nonlinearity, even with fixed device geometry?

## Prerequisite Mapping

- Quantum: phase difference and single-valuedness
- Electromagnetism: external flux and loop constraints
- Classical: equivalent parameters and small-signal linearization

## Physics Core

For a symmetric SQUID under common approximations,

$$
E_J^{\mathrm{eff}}(\Phi_{\mathrm{ext}}) \approx 2E_{J0}\cos\left(\pi\frac{\Phi_{\mathrm{ext}}}{\Phi_0}\right).
$$

Josephson inductance is approximately inverse to this energy scale, so flux bias tunes effective inductance:

$$
L_J^{\mathrm{eff}} \propto \frac{1}{E_J^{\mathrm{eff}}}.
$$

!!! note "Historical Context"
    Tunable inductance enabled practical tunable qubits, parametric amplifiers, and reconfigurable couplers on a single platform.

## Engineering Mapping

- Flux bias tunes frequency, nonlinearity, and coupling.
- Design tradeoffs are set by tunability range, sensitivity, and noise susceptibility.

## Limits and Approximations

- If symmetry or small-loop assumptions break, include asymmetry and self-inductance.
- Near `E_J^{\mathrm{eff}} \to 0`, noise and higher-order effects become more critical.

## Cross-Document Navigation

- Previous: [How Does Lagrangian Mechanics Connect to Circuit Physics?](lagrangian-mechanics-and-circuit-physics.en.md)
- Task-first: [SQUID Fitting](../../how-to/fit-model/squid.en.md)
- Task-first: [Flux Dependence Plot](../../reference/cli/flux-dependence-plot.en.md)
