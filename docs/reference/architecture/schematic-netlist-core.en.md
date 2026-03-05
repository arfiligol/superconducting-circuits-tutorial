---
aliases:
  - Circuit Netlist Core
  - Netlist Core Contract
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
  - topic/netlist
status: stable
owner: docs-team
audience: team
scope: Core contract for Circuit Netlist source-to-expanded pipeline and validation
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Circuit Netlist Core

This page defines the architecture contract for Circuit Netlist in the application.

## Core Contract

- **Source Form**: persisted in DB and may include `repeat`.
- **Expanded Form**: runtime compiled output for preview and simulation.
- **Single Pipeline**: Schema Preview and Simulation Configuration share one expansion path.

## Validation Highlights

- Ground token must be `"0"` only.
- `components[*]` requires `name` and `unit`, plus exactly one of `default` / `value_ref`.
- `topology` rows must reference an existing component or a valid port index.
- Expanded output after `repeat` must pass full netlist validation.

## Related

- [Circuit Netlist Format](../data-formats/circuit-netlist.en.md)
- [Restricted Netlist Generators](../../explanation/architecture/circuit-simulation/restricted-netlist-generators.en.md)
