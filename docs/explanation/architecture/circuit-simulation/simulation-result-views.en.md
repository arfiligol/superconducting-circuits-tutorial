---
aliases:
- Simulation Result Views
- 模擬結果視圖
tags:
- diataxis/explanation
- audience/team
- topic/architecture
- topic/simulation
status: draft
owner: docs-team
audience: team
scope: Simulation Result multi-view contract, selectors, and the current single-port S11-derived path
version: v0.1.0
last_updated: 2026-03-01
updated_by: docs-team
---

> **Note**: This page is intentionally concise. See the [Traditional Chinese version](simulation-result-views.md) for the primary text.

# Simulation Result Views

The Simulation Result card should not be locked to a single plot. Even though the current Julia bridge still returns only single-port `S11`, the UI must expose a multi-view shell that can grow into a matrix-capable result browser.

## Current Contract

The current bridge returns:

- `S11` real
- `S11` imaginary

All current views are derived from that single complex trace.

## Current View Families

- `S`
- `Gain`
- `Impedance (Z)`
- `Admittance (Y)`
- `Complex Plane`

## Current Selectors

- `View Family`
- `Metric`
- `Trace`
- `Output Port` / `Input Port` (currently fixed to `1`)
- `Z0 (Ohm)` for `Z` / `Y` derived views

## Current Limits

The current UI is intentionally structured so it can later expand to:

- multi-port `Sij` / `Zij` / `Yij`
- idler families
- quantum efficiency (`QE`)
- commutation diagnostics (`CM`)

Those appear in JosephsonCircuits examples, but the current bridge does not yet return those datasets.

## Related

- [Circuit Simulation](index.md)
