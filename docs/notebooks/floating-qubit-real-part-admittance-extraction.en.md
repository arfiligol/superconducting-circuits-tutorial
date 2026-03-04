---
aliases:
  - "Floating Qubit Real Part Admittance Extraction"
  - "提取 Floating Qubit 看出去的 Real Part Admittance"
tags:
  - diataxis/reference
  - audience/team
  - topic/physics
  - topic/simulation
  - status/draft
status: draft
owner: docs-team
audience: team
scope: Workflow for extracting floating-qubit differential driving-point admittance (PTC -> CT -> Kron)
version: v0.3.0
last_updated: 2026-03-05
updated_by: docs-team
---

# Floating Qubit Real Part Admittance Extraction

!!! note "Research Notebook (work in progress)"
    This page records the currently reproducible WebUI workflow that is aligned with
    formal Reference contracts. The topic is extracting floating-qubit `Re(Y_in)` from
    the differential mode as an input quantity for later `T1` analysis.

## Goal (Contract-aligned)

Extract differential driving-point admittance:

`Y_in,dm(omega)`

while explicitly controlling whether loading from other ports (for example Port 3 `50 Ohm`)
is retained.

## Contract Sources (Required Reading)

This notebook does not define new semantics. It follows:

- [Circuit Simulation Reference (Post Processing / CT / Kron / PTC / HFSS Comparable)](../reference/ui/circuit-simulation/)
- [Schur Complement and Kron Reduction (Explanation)](../explanation/physics/schur-complement-kron-reduction/)
- [Analysis Result Data Format (HFSS comparable fields)](../reference/data-formats/analysis-result/)
- [Physics Symbol Glossary](../explanation/physics/symbol-glossary/)

Core operation contract used on this page:

1. `Y` domain as the only transform domain
2. Coordinate Transformation: `Y_m = A^{-T} Y A^{-1}`
3. Kron Reduction: Schur complement
4. Read target-mode `Y_in` after reduction

## Strict Flow: PTC -> CT -> Kron

### Step 0: Raw multi-port admittance

Solver provides:

`I = Y_raw(omega) V`

3-port example:

- Port 1: Pad 1
- Port 2: Pad 2
- Port 3: XY / drive line

### Step 1: Port Termination Compensation (remove solver-artificial terminations only)

To keep Port 3 physical loading while removing Port 1/2 solver port-definition resistors:

```text
Y_ptc = Y_raw - diag(1/50, 1/50, 0)
```

!!! important "Physical meaning"
    This is a port-definition correction, not a physical-mode transform.
    Skipping this step leaks artificial Port 1/2 `50 Ohm` dissipation into `dm`.

### Step 2: Post Processing input must be `PTC Y`

If Post Processing starts from `Raw Y`, the transformed `dm` mode includes artificial loss channels.

### Step 3: Coordinate Transformation (port basis -> physical mode basis)

cm/dm definitions:

- `V_cm = alpha V1 + beta V2`
- `V_dm = V1 - V2`
- constraint: `alpha + beta = 1`

Auto weights (Electrical Centroid):

- `w1 = Σ C(node1 <-> 0)`
- `w2 = Σ C(node2 <-> 0)`
- `alpha = w1 / (w1 + w2)`
- `beta  = w2 / (w1 + w2)`

!!! note "Auto alpha/beta source of truth"
    The official extraction rule is defined in `Circuit Simulation Reference`.
    This notebook only references it.

### Step 4: Kron Reduction (keep only `dm`)

In `(cm, dm, 3)` basis, remove unobserved degrees of freedom (typically `cm` and `3`) using Schur complement:

```text
Y_red = Y_bb - Y_bi * Y_ii^{-1} * Y_ib
```

For `b = {dm}`:

`Y_in,dm = Y_red(dm,dm)`

## Why this order cannot be swapped

1. `CT` before `PTC`: artificial `50 Ohm` contaminates `Re(Y_dm)`
2. `Kron` before `CT`: removes original ports, not physical modes
3. no `Kron`: gives multi-port representation, not driving-point admittance

So the required order is:

`PTC -> CT -> Kron`

## UI Reproduction Cases

### Case A: include Port 3 `50 Ohm` loading

1. In `Port Termination Compensation`, select Port 1 and Port 2 only (exclude Port 3)
2. Set Post Processing `Input Y Source` to `PTC Y`
3. Add `Coordinate Transformation` (1,2 -> cm/dm)
4. Add `Kron Reduction`, keep only `dm`
5. Read the real part of `Y_dm_dm` in Post-Processed Result View (`Real(Y)`)

### Case B: inspect closer-to-intrinsic response (remove all selected port shunts)

1. Select all target ports in `Port Termination Compensation`
2. Set `Input Y Source` to `PTC Y`
3. Apply CT + Kron and extract `Re(Y_dm_dm)`

!!! warning "Raw S / PTC boundary (Reference contract)"
    `S` in `Simulation Results` is solver-native raw `S`.
    PTC switching in Raw View applies only to `Y/Z` families.

## HFSS Comparison (current contract)

`HFSS Comparable` in Post-Processed Results is typically satisfied only when:

1. PTC is enabled
2. `Input Y Source = PTC Y`
3. at least one enabled `Coordinate Transformation` step exists

- [HFSS Comparable semantics](../reference/ui/circuit-simulation/#hfss-comparable)
- [Analysis Result fields (`hfss_comparable` / reason)](../reference/data-formats/analysis-result/)

---

## Current limitations (2026-03-05)

1. Differential normalization convention (`v_dm` scaling) is not finalized
2. HFSS alignment rules for `Zref` / port references are not finalized
3. No direct `Y_in` calculator in UI yet (keep/drop/load-condition inputs)

## TODOs

- [ ] Lock down differential normalization convention (for example scaling of `v_dm`)
- [ ] Lock down HFSS alignment rules for `Zref`/port references
- [ ] Add direct `Y_in` calculator in UI with explicit load-condition inputs
- [ ] Turn `Re(Y_in)` to `T1` workflow into reusable Characterization analysis
