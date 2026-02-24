---
aliases:
- Symbol Glossary
tags:
- diataxis/reference
- audience/team
- topic/physics
status: draft
owner: docs-team
audience: team
scope: "Master symbol table for superconducting quantum circuit physics"
version: v0.1.0
last_updated: 2026-02-24
updated_by: team
---

# Symbol Glossary

This page consolidates all major symbols used across the Physics section. Each page should still define symbols at first use; this serves as a unified cross-page reference.

---

## Fundamental Constants & Quantities

| Symbol | Name | Unit | Notes |
|--------|------|------|-------|
| $f$ | Frequency | Hz | |
| $\omega = 2\pi f$ | Angular frequency | rad/s | |
| $\lambda$ | Wavelength | m | |
| $k = 2\pi/\lambda$ | Wavenumber | rad/m | |
| $T$ | Temperature | K | |
| $k_B$ | Boltzmann constant | J/K | $1.381 \times 10^{-23}$ |
| $\hbar$ | Reduced Planck constant | J·s | $1.055 \times 10^{-34}$ |
| $\Phi_0$ | Magnetic flux quantum | Wb | $h/(2e) \approx 2.068 \times 10^{-15}$ |
| $\varphi_0$ | Reduced flux quantum | Wb | $\Phi_0 / (2\pi)$ |

## Circuit Elements & Parameters

| Symbol | Name | Unit | Notes |
|--------|------|------|-------|
| $L$ | Inductance | H | |
| $C$ | Capacitance | F | |
| $R$ | Resistance | Ω | |
| $Z$ | Impedance | Ω | $Z = R + jX$ |
| $Y$ | Admittance | S | $Y = 1/Z$ |
| $Z_0$ | Characteristic impedance | Ω | Transmission line |
| $L_J$ | Josephson inductance | H | $L_J = \Phi_0 / (2\pi I_c)$ |
| $L_K$ | Kinetic inductance | H | |
| $E_J$ | Josephson energy | J | $E_J = \Phi_0 I_c / (2\pi)$ |
| $E_C$ | Charging energy | J | $E_C = e^2 / (2C)$ |
| $I_c$ | Critical current | A | Josephson junction |

## Resonators & Quality Factors

| Symbol | Name | Unit | Notes |
|--------|------|------|-------|
| $f_r$ | Resonance frequency | Hz | |
| $\omega_r$ | Resonance angular frequency | rad/s | $\omega_r = 2\pi f_r$ |
| $Q_l$ | Loaded quality factor | — | $1/Q_l = 1/Q_i + 1/Q_c$ |
| $Q_i$ | Internal quality factor | — | Material & radiation losses |
| $Q_c$ | Coupling quality factor | — | Energy leakage to external ports |
| $\kappa$ | Linewidth / decay rate | rad/s | $\kappa = \omega_r / Q_l$ |
| $\tau$ | Electrical delay | s | |

## Scattering Parameters

| Symbol | Name | Unit | Notes |
|--------|------|------|-------|
| $S_{ij}$ | Scattering parameter | — | Port $j$ → Port $i$ |
| $S_{21}$ | Transmission coefficient | — | Forward transmission |
| $S_{11}$ | Reflection coefficient | — | Input reflection |

## Quantum Circuits

| Symbol | Name | Unit | Notes |
|--------|------|------|-------|
| $\hat{a}$, $\hat{a}^\dagger$ | Annihilation / creation operators | — | |
| $\chi$ | Dispersive shift | Hz | |
| $g$ | Coupling strength | Hz | Qubit-resonator |
| $\Delta$ | Detuning | Hz | $\Delta = \omega_q - \omega_r$ |
| $T_1$ | Energy relaxation time | s | |
| $T_2$ | Decoherence time | s | |
| $\Gamma_1 = 1/T_1$ | Relaxation rate | Hz | |
| $\Gamma_\varphi$ | Pure dephasing rate | Hz | $1/T_2 = 1/(2T_1) + \Gamma_\varphi$ |

---

> This table will be updated as the Physics section expands. If symbol conflicts are found, annotate the applicable scope in both the relevant page and this table.
