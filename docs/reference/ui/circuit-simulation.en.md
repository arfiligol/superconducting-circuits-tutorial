---
aliases:
- Circuit Simulation UI
- 電路模擬介面
tags:
- diataxis/reference
- audience/team
- topic/ui
- topic/simulation
status: draft
owner: docs-team
audience: team
scope: Circuit Simulation UI controls, saved setups, and result-view behavior
version: v0.1.0
last_updated: 2026-03-01
updated_by: docs-team
---

> **Note**: This page is intentionally concise. See the [Traditional Chinese version](circuit-simulation.md).

# Circuit Simulation

This page documents the current `/simulation` UI surface.

## Current Sections

1. `Active Schema`
2. `Live Preview`
3. `Simulation Setup`
4. `Simulation Log`
5. `Simulation Results`

## Current Result Views

- `S`
- `Gain`
- `Impedance (Z)`
- `Admittance (Y)`
- `Complex Plane`

## Current Limit

The current Julia bridge still returns only single-port `S11`.

That means:

- `Output Port` / `Input Port` are currently fixed to `1`
- `Z11` / `Y11` are derived from `S11` and `Z0`
- `Gain` is currently return gain derived from `S11`
