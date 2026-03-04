---
aliases:
  - "Floating Qubit Real Part Admittance Extraction"
  - "提取 Floating Qubit 看出去的 Real Part Admittance"
tags:
  - diataxis/reference
  - status/draft
---

# Floating Qubit Real Part Admittance Extraction

!!! note "Research Notebook (work in progress)"
    This page records the currently reproducible WebUI workflow as a staging note for
    later qubit `T1` analysis. The contract is not final yet.

## Goal

Extract `Re(Y_in)` seen from the floating-qubit differential port, while controlling whether
shunt termination effects from other ports (for example readout/drive ports) are retained.

## Problem Statement (current working model)

Given a post-processed multi-port admittance matrix `Y(omega)`, derive one-port equivalent input:

- target port: `dm` (constructed from Port 1/2 by Coordinate Transformation)
- other ports: optionally eliminated by Kron reduction
- `Re(Y_in)`: key quantity for later loss / `T1` estimation

## Current Recommended UI Flow

### A. Keep Port 3 shunt effect in `dm`

1. In `Port Termination Compensation`, select Port 1 and Port 2 only (exclude Port 3)
2. Set Post Processing `Input Y Source` to `PTC Y`
3. Add `Coordinate Transformation` (1,2 -> cm/dm)
4. Add `Kron Reduction`, keep only `dm`
5. Read the real part of `Y_dm_dm` in Post-Processed Result View (`Real(Y)`)

### B. Remove all port shunts for intrinsic inspection

1. Select all target ports in `Port Termination Compensation`
2. Set `Input Y Source` to `PTC Y`
3. Apply CT + Kron and extract `Re(Y_dm_dm)`

!!! warning "Semantic reminder"
    `S` in `Simulation Result View` is raw solver-native `S` and is not PTC-modified.
    Raw/compensated switching applies to `Y/Z` families.

## Mathematical Form (for extension)

To compute one-port input admittance with explicit load assumptions on other ports, use
Schur complement in `Y` domain:

```text
Y_in = Y_ii - Y_i,o * (Y_o,o + Y_L)^(-1) * Y_o,i
```

- `i`: target port (typically `dm`)
- `o`: all other ports
- `Y_L`: load admittance on the other ports (for 50 Ohm, `1/50` S)

## HFSS Comparison (current convention)

Post-Processed Result View exposes `HFSS Comparable` status.
Typically it expects:

1. PTC enabled
2. `Input Y Source = PTC Y`
3. Coordinate Transformation step present

!!! note "Current limitation"
    The `HFSS Comparable` marker currently tracks flow-level conditions. It does not yet
    strictly validate whether compensated port selection exactly matches your intended
    comparison setup.

## Open TODOs

- [ ] Lock down differential normalization convention (for example scaling of `v_dm`)
- [ ] Lock down HFSS alignment rules for `Zref`/port references
- [ ] Add direct `Y_in` calculator in UI with explicit load-condition inputs
- [ ] Turn `Re(Y_in)` to `T1` workflow into reusable Characterization analysis
