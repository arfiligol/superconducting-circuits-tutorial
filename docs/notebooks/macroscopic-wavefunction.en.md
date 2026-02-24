---
aliases:
- Macroscopic Wavefunction of Superconductors
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: Explain why a superconductor can be described by a single macroscopic wavefunction
version: v0.1.0
last_updated: 2026-02-24
updated_by: team
---

# The Macroscopic Wavefunction of Superconductors

## Chapter Summary

One of the most remarkable properties of a superconductor is that a vast number of electrons in the material can be described by a **single wavefunction**. This is not a single-particle wavefunction but a macroscopic quantum state — its existence is the starting point for all superconducting quantum circuit physics that follows.

## Prerequisites

- **Quantum mechanics**: Wavefunction $\Psi$, Schrödinger equation, concept of Bose–Einstein condensation
- **Statistical mechanics**: Phase transitions, order parameter
- **Solid-state physics**: Fermi surface, electron–phonon interaction (qualitative understanding sufficient)

## Symbol Definitions

| Symbol | Name | Definition / Description |
|--------|------|--------------------------|
| $\Psi(\mathbf{r})$ | Macroscopic wavefunction | Order parameter describing the superconducting condensate; also called the Ginzburg–Landau order parameter |
| $\|\Psi(\mathbf{r})\|^2$ | Superfluid density | Density of the Cooper pair condensate, proportional to the Cooper pair number density $n_s$ |
| $\theta(\mathbf{r})$ | Macroscopic phase | Phase of the order parameter; plays the role of the central dynamical variable in superconducting circuits |
| $n_s$ | Cooper pair number density | Number of Cooper pairs per unit volume |
| $\Delta$ | Superconducting gap | Binding energy of a Cooper pair, related to the pairing strength |
| $T_c$ | Critical temperature | Temperature threshold for the superconducting phase transition |
| $\xi$ | Coherence length | Characteristic length scale over which the order parameter varies significantly |

## Physical Narrative

### 1. Electrons in a Normal Metal

In a normal metal, conduction electrons are fermions obeying the Pauli exclusion principle. Each electron occupies a distinct quantum state, filling up to the Fermi energy $E_F$. These electrons cannot be described by a single shared wavefunction — their behavior is fundamentally "many-body" and "independent."

### 2. Cooper Pairing: How Electrons Form Pairs

In 1956, Cooper showed that even a weak attractive interaction between electrons (for example, mediated indirectly by lattice vibrations — phonons) can cause two electrons near the Fermi surface to form a bound state (Cooper, 1956). This bound state is called a **Cooper pair**.

Key properties of a Cooper pair:

- Composed of two electrons with opposite momenta and opposite spins: $(\mathbf{k}\uparrow, -\mathbf{k}\downarrow)$
- Total spin is zero → the pair behaves as a **boson**
- The pairing gap $\Delta$ prevents the pair from being easily broken apart

!!! note "Why is a Cooper pair a boson?"
    A composite particle made of two fermions (half-integer spin) has integer total spin (here, 0), and therefore obeys Bose–Einstein statistics. This is the physical basis for Cooper pair condensation.

### 3. From Pairing to Condensation: The BCS Ground State

In 1957, Bardeen, Cooper, and Schrieffer constructed a complete microscopic theory (the BCS theory), proving that below the critical temperature $T_c$, all pairable electrons near the Fermi surface simultaneously form Cooper pairs occupying **the same quantum state** (Bardeen et al., 1957).

This is the **analogue of Bose–Einstein condensation**: a macroscopic number of Cooper pairs condense into the same quantum ground state, forming a macroscopic quantum condensate.

!!! tip "Historical Context"
    After its publication in 1957, BCS theory successfully explained the superconducting gap, the Meissner effect, and the isotope effect, among other experimental phenomena. Bardeen, Cooper, and Schrieffer were awarded the 1972 Nobel Prize in Physics.

### 4. The Order Parameter: Mathematical Description of the Condensate

Since all Cooper pairs occupy the same quantum state, we can describe the entire condensate with a **single field** $\Psi(\mathbf{r})$. This is the order parameter introduced phenomenologically by Ginzburg and Landau in 1950 (Ginzburg & Landau, 1950), later shown by Gor'kov (1959) to be rigorously derivable from BCS theory.

The order parameter in polar form:

$$
\Psi(\mathbf{r}) = |\Psi(\mathbf{r})|\, e^{i\theta(\mathbf{r})}
$$

This expression contains two physical quantities:

| Component | Physical Meaning | Notes |
|-----------|-----------------|-------|
| $\|\Psi(\mathbf{r})\|$ | Amplitude, proportional to $\sqrt{n_s}$ | Describes "how strong" the superconductivity is |
| $\theta(\mathbf{r})$ | Phase | Describes the quantum phase of the condensate; current flow, flux quantization, and other phenomena are all determined by it |

!!! warning "This is not a single-electron wavefunction"
    $\Psi(\mathbf{r})$ is not the quantum mechanical wavefunction of a single electron, but the **order parameter field** describing the Cooper pair condensate. Its square gives the Cooper pair number density, not a single-electron probability density.

### 5. Why Is the Phase $\theta$ So Important?

In the bulk of a superconductor, the amplitude $|\Psi|$ is typically uniform and stable (far from boundaries and vortex cores). Therefore, all interesting dynamics in a superconductor — current flow, magnetic field response, the Josephson effect — are driven by the phase $\theta(\mathbf{r})$.

The supercurrent density is related to the phase gradient by:

$$
\mathbf{J}_s = \frac{n_s e^*}{m^*}\left(\hbar\nabla\theta - e^*\mathbf{A}\right)
$$

where $e^* = 2e$ is the Cooper pair charge, $m^*$ is its effective mass, and $\mathbf{A}$ is the magnetic vector potential. This expression tells us directly: **the supercurrent is driven by spatial variations of the macroscopic phase**.

This is precisely why superconducting quantum circuits can exist — the phase $\theta$ is simultaneously macroscopically observable (it can drive currents) and quantum mechanical (it satisfies all properties of a wavefunction, such as single-valuedness).

## Engineering Mapping

- All superconducting quantum circuit designs are built upon the existence of the macroscopic wavefunction.
- The **node flux** $\Phi = (\hbar/2e)\,\theta$ in circuits is the engineering equivalent of the phase.
- The superconducting gap $\Delta$ determines the quasiparticle excitation threshold, affecting qubit decoherence.
- The coherence length $\xi$ sets the geometric lower bound for Josephson junctions.

## Limitations and Approximations

- The description above is most accurate at $T \ll T_c$; near $T_c$, fluctuations in the order parameter amplitude cannot be neglected.
- Ginzburg–Landau theory is a mean-field approximation; corrections are needed in low-dimensional systems or strong-fluctuation regimes.
- This page does not cover the full BCS derivation (e.g., the gap equation); the focus is on the physical meaning and notation of the order parameter.

## Cross-File Navigation

- Next: [Why Is Magnetic Flux Quantized?](why-flux-is-quantized.md) — derives flux quantization from the single-valuedness of the macroscopic wavefunction
- Task-oriented: [Flux Analysis Tutorial](../../tutorials/flux-analysis.md)

## References

- Bardeen, J., Cooper, L. N., & Schrieffer, J. R. (1957). Theory of superconductivity. *Physical Review*, 108(5), 1175–1204. [DOI:10.1103/PhysRev.108.1175](https://doi.org/10.1103/PhysRev.108.1175)
- Cooper, L. N. (1956). Bound electron pairs in a degenerate Fermi gas. *Physical Review*, 104(4), 1189–1190. [DOI:10.1103/PhysRev.104.1189](https://doi.org/10.1103/PhysRev.104.1189)
- Ginzburg, V. L., & Landau, L. D. (1950). On the theory of superconductivity. *Zhurnal Eksperimental'noi i Teoreticheskoi Fiziki*, 20, 1064–1082. (English translation in *Collected Papers of L. D. Landau*, Pergamon, 1965.)
- Gor'kov, L. P. (1959). Microscopic derivation of the Ginzburg–Landau equations in the theory of superconductivity. *Soviet Physics JETP*, 9(6), 1364–1367.
- Tinkham, M. (2004). *Introduction to Superconductivity* (2nd ed.). Dover Publications. ISBN 978-0-486-43503-9.
- Annett, J. F. (2004). *Superconductivity, Superfluids and Condensates*. Oxford University Press. ISBN 978-0-19-850756-7.
