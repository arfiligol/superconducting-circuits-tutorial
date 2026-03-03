---
aliases:
- Schema Editor
- Circuit Netlist Editor
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# Schema Editor

This page describes the target UI contract for the next `/schemas/{id}` iteration.

!!! warning "Docs-first"
    This page describes the target behavior after the next code migration.
    Until that migration is complete, the current app may still support only a simpler netlist subset.

## Page Sections

1. `Circuit Definition`
2. `Expanded Netlist Preview`
3. `Component & Unit Reference`

## Circuit Definition

### Editor Model

- Input format: **Circuit Netlist v0.3 (Generator-enabled, Component-first)**
- Required fields: `name`, `components`, `topology`
- Optional field: `parameters`
- Allowed text style: Python literals (including tuples and trailing commas)

### Supported Block Items

- `components`: explicit rows or `repeat`
- `topology`: explicit tuples or `repeat`
- `parameters`: explicit rows or `repeat` (advanced, optional)

!!! info "The editor is not a script runtime"
    The editor accepts `repeat`, `symbols`, `series`, and restricted template interpolation, but it does not execute arbitrary Python.

### Format

- `Format` uses Ruff WebAssembly (`@astral-sh/ruff-wasm`)
- `Format` does not expand `repeat`
- `Format` does not rewrite the netlist into a different equivalent structure

### Save Schema

- `Save Schema` preserves the current editor text
- `Save Schema` does not auto-expand `repeat`
- `Save Schema` does not inject hidden fields

## Expanded Netlist Preview

`Expanded Netlist Preview` is a **compiled-result preview**, not a new source of truth.

Its target behavior is:

- show the final netlist after expanding `repeat`
- use the exact same expansion pipeline that runs before Simulation
- remain read-only

!!! important "Source vs Compiled"
    - `Circuit Definition`: the source text you edit and save (may contain `repeat`)
    - `Expanded Netlist Preview`: the expanded result that will actually be sent to the simulator

### Displayed Content

- always show expanded `components`
- always show expanded `topology`
- if `parameters` are used, also show expanded `parameters`

### Purpose

- verify that `repeat` expands correctly
- verify node numbering, component names, and `K*` references
- inspect the final simulation input before leaving the editor

!!! note "Persistence"
    The database still stores only the source `Circuit Definition`.
    `Expanded Netlist Preview` is a read-only compiled view, not a stored format.

## Validation Feedback

### Parse errors

- invalid syntax
- incomplete tuple delimiters
- malformed `repeat` blocks

### Validation errors

- missing required fields (`name`, `components`, `topology`)
- wrong row types inside `components`, `topology`, or `parameters`
- a component is missing `unit`
- a component either lacks both `default` and `value_ref`, or includes both
- unresolved `value_ref`
- non-numeric node tokens
- use of `gnd` instead of `0`
- unsupported template expressions

### Expansion errors

- expanded `repeat` output produces invalid rows
- a `K*` row references an inductor name that does not exist after expansion
- generated component names and generated topology references do not match

!!! tip "Recommended authoring pattern"
    If the circuit has different boundary conditions at the beginning and end:

    1. write the prelude explicitly
    2. express the regular middle section through `repeat`
    3. write the epilogue explicitly

    Do not try to force conditional logic into `repeat`.

## Handoff to Simulation

- The Simulation UI expands any supported `repeat` blocks before execution
- `Netlist Configuration` should display the result from the same expansion pipeline as `Expanded Netlist Preview`
- Sources, pumps, and harmonics remain part of Simulation Setup

!!! note "Live Preview"
    Live Preview remains disabled and is not shown in the Schema Editor.
