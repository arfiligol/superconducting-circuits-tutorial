---
aliases:
- Why Magnetic Flux Is Quantized
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: Derive flux quantization in superconducting loops from gauge invariance and wavefunction single-valuedness
version: v0.2.0
last_updated: 2026-02-24
updated_by: team
---

# Why Is Magnetic Flux Quantized?

## Chapter Summary

In a superconducting closed loop, the allowed magnetic flux is not a continuous quantity but comes in integer multiples of the flux quantum $\Phi_0 = h/2e$. This result follows directly from the **single-valuedness** of the macroscopic wavefunction and the **gauge invariance** of electromagnetism. This chapter derives the flux quantization condition step by step from these two principles.

## Prerequisites

- **Quantum mechanics**: Single-valuedness of wavefunctions, phase
- **Electromagnetism**: Vector potential $\mathbf{A}$, definition of magnetic flux, Stokes' theorem
- **Prior reading**: [The Macroscopic Wavefunction of Superconductors](macroscopic-wavefunction.md) — physical meaning of the order parameter $\Psi(\mathbf{r}) = |\Psi| e^{i\theta}$

??? info "Need background? Read first"
    - [The Macroscopic Wavefunction of Superconductors](macroscopic-wavefunction.md): understand why a superconductor can be described by a single wavefunction

## Symbol Definitions

| Symbol | Name | Definition / Description |
|--------|------|--------------------------|
| $\Psi(\mathbf{r})$ | Macroscopic wavefunction | Superconducting order parameter, $\Psi = \|\Psi\| e^{i\theta}$ |
| $\theta(\mathbf{r})$ | Macroscopic phase | Phase of the order parameter |
| $\mathbf{A}(\mathbf{r})$ | Magnetic vector potential | Satisfies $\mathbf{B} = \nabla \times \mathbf{A}$ |
| $\mathbf{B}$ | Magnetic field | Magnetic flux density |
| $\Phi$ | Magnetic flux | Total flux through the area enclosed by a loop, $\Phi = \oint \mathbf{A} \cdot d\mathbf{l}$ |
| $\Phi_0$ | Flux quantum | $\Phi_0 = h / 2e \approx 2.068 \times 10^{-15}\;\mathrm{Wb}$ |
| $e^* = 2e$ | Cooper pair charge | Charge carriers in a superconductor are Cooper pairs |
| $\hbar$ | Reduced Planck constant | $\hbar = h / 2\pi$ |
| $n$ | Quantum number | Integer, $n \in \mathbb{Z}$ |
| $C$ | Closed path | A closed integration contour inside the superconductor bulk |

## Physical Narrative

### 1. Starting from the Macroscopic Wavefunction

As described in the previous chapter, the superconducting condensate is described by an order parameter (Tinkham, 2004, Ch. 4):

$$
\Psi(\mathbf{r}) = |\Psi(\mathbf{r})|\, e^{i\theta(\mathbf{r})}
$$

This wavefunction is **continuous and single-valued** throughout the superconductor — traversing any closed path and returning to the starting point, the wavefunction must return to its original value. This is a fundamental requirement of quantum mechanics.

### 2. What Is Gauge Invariance?

In electromagnetism, the physically observable quantities (electric field $\mathbf{E}$, magnetic field $\mathbf{B}$) are determined by Maxwell's equations. However, the vector potential $\mathbf{A}$ and scalar potential $\phi$ are not unique — the following **gauge transformation** leaves the physics invariant (Jackson, 1999, Ch. 6):

$$
\mathbf{A} \to \mathbf{A}' = \mathbf{A} + \nabla\chi, \qquad
\phi \to \phi' = \phi - \frac{\partial \chi}{\partial t}
$$

where $\chi(\mathbf{r}, t)$ is an arbitrary smooth function.

!!! note "Physical meaning of gauge invariance"
    Gauge invariance means that **potentials themselves are not physical observables** — only specific combinations of potentials (such as $\mathbf{B} = \nabla \times \mathbf{A}$) correspond to measurable quantities. Therefore, any physical expression involving $\mathbf{A}$ must appear in a gauge-invariant form.

### 3. Minimal Coupling and the Gauge-Invariant Phase Gradient

In quantum mechanics, the coupling of a charged particle to an electromagnetic field is implemented through **minimal coupling**: the momentum operator $\hat{\mathbf{p}}$ is replaced by

$$
\hat{\mathbf{p}} \to \hat{\mathbf{p}} - e^*\mathbf{A}
$$

This is known as the Peierls substitution. For Cooper pairs ($e^* = 2e$), the corresponding phase gradient in the supercurrent density is not simply $\nabla\theta$ but the **gauge-invariant phase gradient** (Tinkham, 2004, Ch. 4):

$$
\boldsymbol{\gamma}(\mathbf{r}) \equiv \nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A}
$$

!!! tip "Why is this combination gauge-invariant?"
    Under a gauge transformation $\mathbf{A} \to \mathbf{A} + \nabla\chi$, the wavefunction phase also transforms: $\theta \to \theta + (2\pi / \Phi_0)\chi$ (a standard result of quantum mechanics). The two changes cancel exactly:

    $$
    \nabla\theta' - \frac{2\pi}{\Phi_0}\mathbf{A}' = \left(\nabla\theta + \frac{2\pi}{\Phi_0}\nabla\chi\right) - \frac{2\pi}{\Phi_0}\left(\mathbf{A} + \nabla\chi\right) = \nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A} = \boldsymbol{\gamma}
    $$

    Therefore $\boldsymbol{\gamma}$ is invariant under gauge transformations and is a genuine physical quantity.

### 4. The Single-Valuedness Condition on a Closed Path

Now consider integrating $\boldsymbol{\gamma}$ along a closed contour $C$ inside the superconductor bulk:

$$
\oint_C \boldsymbol{\gamma} \cdot d\mathbf{l} = \oint_C \left(\nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A}\right) \cdot d\mathbf{l}
$$

The left-hand side splits into two parts:

**Part 1**: $\oint_C \nabla\theta \cdot d\mathbf{l}$

The integral of the phase gradient around a closed path equals the total change in phase after one traversal. Since the wavefunction $\Psi = |\Psi| e^{i\theta}$ must be single-valued, $e^{i\theta}$ must return to its original value after one full loop, requiring:

$$
\oint_C \nabla\theta \cdot d\mathbf{l} = 2\pi n, \quad n \in \mathbb{Z}
$$

**Part 2**: $\oint_C \mathbf{A} \cdot d\mathbf{l}$

By Stokes' theorem:

$$
\oint_C \mathbf{A} \cdot d\mathbf{l} = \int_S (\nabla \times \mathbf{A}) \cdot d\mathbf{S} = \int_S \mathbf{B} \cdot d\mathbf{S} = \Phi
$$

where $S$ is any surface bounded by $C$, and $\Phi$ is the total magnetic flux through that surface.

### 5. Flux Quantization

Combining the above results:

$$
\oint_C \boldsymbol{\gamma} \cdot d\mathbf{l} = 2\pi n - \frac{2\pi}{\Phi_0}\Phi
$$

Deep inside the superconductor bulk (outside the London penetration depth $\lambda_L$), the supercurrent density vanishes (a consequence of the Meissner effect). Since the supercurrent is proportional to $\boldsymbol{\gamma}$, this implies:

$$
\boldsymbol{\gamma} = 0 \quad \text{(deep inside the superconductor)}
$$

Therefore, for a path $C$ located deep within the superconductor bulk:

$$
0 = 2\pi n - \frac{2\pi}{\Phi_0}\Phi
$$

Rearranging yields the **flux quantization condition**:

$$
\boxed{\Phi = n\,\Phi_0, \quad n \in \mathbb{Z}}
$$

The magnetic flux through a superconducting closed loop can only be an integer multiple of the flux quantum $\Phi_0 = h/2e$.

!!! note "Historical Context"
    Flux quantization was first observed experimentally in 1961 by two independent groups: Deaver and Fairbank (1961) in the United States, and Doll and Näbauer (1961) in Germany. Their experiments simultaneously confirmed that the flux quantum has the value $h/2e$ (not $h/e$), thereby establishing that the charge carriers in a superconductor are **paired electrons** (Cooper pairs), not single electrons. This was one of the key experimental verifications of BCS theory.

!!! tip "From Experiment to Technology"
    Flux quantization turned "superconductivity is a macroscopic quantum state" into a directly measurable fact. It not only validated BCS theory but also laid the physical foundation for SQUID magnetometers, quantum interferometers, and the entire field of superconducting quantum circuit technology.

## Engineering Mapping

- $\Phi / \Phi_0$ directly determines the bias operating point of a SQUID loop — a core parameter in circuit design.
- The quantization condition constrains the phase in a loop, limiting the allowed dynamical branches.
- In loops containing Josephson junctions, the flux quantization condition is modified to include the junction phase differences (see [SQUID Controls Nonlinear Inductance](squid-controls-nonlinear-inductance.md)).

## Limitations and Approximations

- The derivation above assumes the path $C$ lies entirely deep within the superconductor bulk ($\boldsymbol{\gamma} = 0$). If the loop wall thickness is comparable to $\lambda_L$, corrections are needed.
- Clear quantization is observable only under appropriate coherence length $\xi$ and temperature conditions.
- Loops containing multiple Josephson junctions require incorporating the phase discontinuities at each junction.

## Cross-File Navigation

- Prior: [The Macroscopic Wavefunction of Superconductors](macroscopic-wavefunction.md)
- Next: [Why Does Nonlinearity Produce Unequal Level Spacings?](why-nonlinearity-makes-unequal-level-spacing.md)
- Task-oriented: [Flux Analysis Tutorial](../../tutorials/flux-analysis.md)

## References

- Tinkham, M. (2004). *Introduction to Superconductivity* (2nd ed.). Dover Publications. ISBN 978-0-486-43503-9.
- Jackson, J. D. (1999). *Classical Electrodynamics* (3rd ed.). Wiley. ISBN 978-0-471-30932-1.
- Deaver, B. S., & Fairbank, W. M. (1961). Experimental evidence for quantized flux in superconducting cylinders. *Physical Review Letters*, 7(2), 43–46. [DOI:10.1103/PhysRevLett.7.43](https://doi.org/10.1103/PhysRevLett.7.43)
- Doll, R., & Näbauer, M. (1961). Experimental proof of magnetic flux quantization in a superconducting ring. *Physical Review Letters*, 7(2), 51–52. [DOI:10.1103/PhysRevLett.7.51](https://doi.org/10.1103/PhysRevLett.7.51)
- Annett, J. F. (2004). *Superconductivity, Superfluids and Condensates*. Oxford University Press. ISBN 978-0-19-850756-7.
