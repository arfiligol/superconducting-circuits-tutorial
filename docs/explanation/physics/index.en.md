---
aliases:
- Physics Explanation
tags:
- diataxis/explanation
- audience/team
- topic/physics
status: draft
owner: docs-team
audience: team
scope: "Knowledge architecture overview for superconducting quantum circuit physics"
version: v1.0.0
last_updated: 2026-02-24
updated_by: team
---

# Physics Knowledge Architecture

This section builds the theoretical foundation for superconducting quantum circuits, organized from fundamental principles to engineering practice.

Each page opens with either a **physics question** or a **historical/community narrative** so readers immediately understand its context. The page skeleton includes sequentially: an opener, prerequisite mapping, physics core (equations and symbol definitions), engineering mapping, limits/approximations, and cross-document navigation links. Content follows the A–I knowledge architecture and can be read linearly or entered at any point.

!!! info "Writing Guidelines"
    - All content follows the [Explanation Physics Guardrail](../../reference/guardrails/documentation-design/explanation-physics.md)
    - Each page declares its node type (Principle / Model / Method / Device)
    - Tool operation steps belong in [How-to Guides](../../how-to/index.md)

---

## A. Foundations: The Four Pillars { #a-foundations }

> The four pillars of physics as prerequisites for superconducting quantum circuits.

| ID | Topic | Node Type |
|----|-------|-----------|
| A1 | Classical Mechanics → Hamiltonian / Lagrangian mindset | Principle |
| A2 | Electromagnetism → fields, energy flow, boundary conditions | Principle |
| A3 | Statistical / Thermal Physics → noise, dissipation, temperature, fluctuation | Principle |
| A4 | Quantum Mechanics → states, measurement, open systems | Principle |

---

## B. Electromagnetics to Circuits { #b-em-to-circuits }

> From Maxwell's equations to computable circuit models. This is the modeling foundation for all simulation and analysis.

| ID | Topic | Node Type |
|----|-------|-----------|
| B1 | Lumped vs Distributed | Model |
| B2 | Transmission Lines & Modes | Model |
| B3 | Impedance, Admittance, Matching | Model |
| B4 | Scattering Parameters (S-parameters) | Model |
| B5 | Resonators & Coupling (Q, κ, bandwidth, ringdown) | Model |
| B6 | [Network Reduction (Kron, port reduction, equivalent circuits)](./schur-complement-kron-reduction.md) | Model |

---

## C. Superconductivity & Dissipation { #c-superconductivity }

> Fundamental physics of superconductors and energy loss mechanisms. Understanding these reveals not only how to design high-Q components, but also why superconductors can function as quantum systems for building quantum computers.

| ID | Topic | Node Type |
|----|-------|-----------|
| C1 | Superconductivity basics (London, BCS, two-fluid intuition) | Principle |
| C2 | Surface impedance / kinetic inductance | Model |
| C3 | Loss channels (dielectric, conductor, radiation, quasiparticles, TLS) | Model |
| C4 | Noise taxonomy (Johnson, 1/f, amplifier noise, quantum noise) | Model |

---

## D. Josephson Physics & Nonlinearity { #d-josephson }

> The Josephson junction is the core nonlinear element. All qubits and parametric amplifiers are built on this foundation.

| ID | Topic | Node Type |
|----|-------|-----------|
| D1 | Josephson relations & junction models | Device / Model |
| D2 | SQUID / arrays / tunability | Device |
| D3 | Nonlinear oscillators & Duffing | Model |
| D4 | Parametric processes (3-wave / 4-wave mixing) | Model / Method |

---

## E. Quantum Circuits Formalism { #e-quantum-circuits }

> Circuit quantization: from classical circuits to quantum Hamiltonians.

| ID | Topic | Node Type |
|----|-------|-----------|
| E1 | Circuit quantization (node flux, charge, constraints) | Method |
| E2 | Lagrangian → Hamiltonian → quantization | Method |
| E3 | Linearization & black-box quantization intuition | Method |
| E4 | Open quantum systems (input-output, master equation) | Model |
| E5 | Dispersive physics (χ, cross-Kerr, Purcell-like channels) | Model |

---

## F. Core Building Blocks { #f-building-blocks }

> Core devices in superconducting quantum circuits.

| ID | Topic | Node Type |
|----|-------|-----------|
| F1 | Resonators (CPW, lumped, 3D, metamaterial) | Device |
| F2 | Qubits (transmon family, fluxonium, etc.) | Device |
| F3 | Couplers & tunable elements | Device |
| F4 | Readout chain & amplifiers (JPA/JPC/JTWPA/HEMT) | Device |

---

## G. Design & Simulation (Principles) { #g-simulation }

> Physical principles behind simulation tools. For tool operation, see How-to.

| ID | Topic | Node Type |
|----|-------|-----------|
| G1 | Circuit simulators (lumped, harmonic balance, time-domain) | Method |
| G2 | EM simulation (FEM / MoM) & port definitions | Method |
| G3 | Parameter extraction (S→Y/Z, mode extraction, energy participation) | Method |
| G4 | Vector fitting & rational models | Method |
| G5 | Quantum solvers & when to use them | Method |
| G6 | Verification strategy (cross-check hierarchy) | Method |

---

## H. Cryogenic RF Engineering (Principles) { #h-cryo-rf }

> Physics of cryogenic microwave measurement chains. For instrument SOPs, see How-to.

| ID | Topic | Node Type |
|----|-------|-----------|
| H1 | RF chain architecture (attenuators, isolators, circulators, filters) | Model |
| H2 | Calibration (power, gain, noise temperature, S-parameter cal) | Method |
| H3 | Signal generation & digitization (AWG, ADC, IQ mixing) | Model |
| H4 | DSP for experiments (downconversion, filtering, decimation) | Method |
| H5 | Stability & grounding & shielding | Principle |

---

## I. Experiments & Protocols (Principles) { #i-experiments }

> Physical principles behind experimental protocols. For measurement SOPs, see How-to.

| ID | Topic | Node Type |
|----|-------|-----------|
| I1 | Resonator characterization | Method |
| I2 | Qubit spectroscopy / time-domain (Rabi, T1, T2, Ramsey, Echo) | Method |
| I3 | Readout optimization (SNR, measurement-induced dephasing) | Method |
| I4 | Amplifier characterization (gain, bandwidth, compression, noise) | Method |

---

## Related

- [How-to Guides](../../how-to/index.md) — Tool operations, data ingestion, CLI steps
- [Tutorials](../../tutorials/index.md) — End-to-end learning workflows
- [Reference](../../reference/index.md) — CLI specs, data formats
- [Notebooks](../../notebooks/) — Research notes and early drafts
