---
aliases:
- Schema Editor
- Circuit Netlist Editor
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /schemas/{id} contract for source-form editing, expanded preview, and validation feedback
version: v0.2.0
last_updated: 2026-03-03
updated_by: docs-team
---

# Schema Editor

This page defines the formal UI contract for `/schemas/{id}`.

## Page Sections

1. `Circuit Definition`
2. `Expanded Netlist Preview`
3. `Component & Unit Reference`

## Circuit Definition

- editing format: Circuit Netlist v0.3 (generator-enabled, component-first)
- required fields: `name`, `components`, `topology`
- optional field: `parameters`
- supports `repeat`, `symbols`, `series`, and restricted template interpolation

!!! info "The editor is not a script runtime"
    Arbitrary Python execution, nested `repeat`, and arbitrary function calls are not supported.

### Format / Save Contract

- `Format` formats source form only and does not expand `repeat`
- `Save Schema` stores source form only and does not store expanded output

## Expanded Netlist Preview

`Expanded Netlist Preview` is a read-only compiled view:

- show expanded `components`
- show expanded `topology`
- when present, show expanded `parameters`

!!! important "SoT boundary"
    Source of Truth remains `Circuit Definition` (may include `repeat`).
    Expanded preview is for debugging and pre-run validation only and is not persisted.

## Validation Feedback

The UI must expose parse/validation/expansion errors, including at least:

- missing component `unit`
- invalid `default` / `value_ref` rule
- unresolved `value_ref`
- non-numeric node tokens
- ground token not equal to `"0"`
- invalid references after expansion (for example `K*` referencing missing inductors)

## Simulation Handoff

`/simulation` `Netlist Configuration` must use the same expansion pipeline
and show the same expanded netlist as this preview.
