---
aliases:
  - Restricted Netlist Generators
  - Constrained Netlist Expansion
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/netlist
status: stable
owner: docs-team
audience: team
scope: Why WebUI uses constrained repeat-based generation instead of arbitrary scripting
version: v0.1.1
last_updated: 2026-03-06
updated_by: codex
---

# Restricted Netlist Generators

This page explains why Circuit Netlist uses constrained generation (`repeat`, etc.) instead of arbitrary script execution.

!!! note "Boundary"
    This page explains why the Web UI uses constrained generators.
    Syntax and editor/save contracts live in Reference.

## Rationale

- **Deterministic** expansion from Source Form to Expanded Form
- **Debuggable** validation with concrete block-level errors
- **Minimal Surface Area** by avoiding an in-browser scripting runtime

## M1 Supported Scope

- `repeat`
- `count` / `start`
- `index` / `symbol` / `series`
- constrained template interpolation (`${index}`, `${symbol}`, and fixed offsets)

## Out of Scope

- arbitrary `for/if`
- nested `repeat`
- arbitrary function calls

## Related

- [Circuit Netlist Format](../../../reference/data-formats/circuit-netlist.en.md)
- [Schema Editor UI Reference](../../../reference/ui/schema-editor.en.md)
- [Circuit Simulation UI](../../../reference/ui/circuit-simulation.en.md)
