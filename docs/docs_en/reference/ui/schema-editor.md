---
aliases:
  - Schema Editor
  - Schematic Netlist Editor
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/ui
  - topic/visualization
status: draft
owner: docs-team
audience: user
scope: UI contract for /schemas/{id}, including the Code Editor, Format, Save, Live Preview, and recovery behavior
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Schema Editor

This page defines the UI contract for `/schemas/{id}`.

## Sections

1. `Circuit Definition`
2. `Live Preview`
3. `Component & Unit Reference`

## Editor model

- Input format: `Schematic Netlist v0.1`
- Accepted syntax styles:
  - JSON style
  - Python literal style (including trailing commas)

## Format

- `Format` normalizes the current editor content
- Browser-side formatting is preferred when available
- Otherwise the backend formatter is used

## Save Schema

- For `v0.1` schemas, `Save Schema` stores the exact current editor text
- The app does not reformat `v0.1` schemas during save
- Legacy tuple schemas are reformatted only during migration

## Live Preview

- Pipeline: `Parse -> Validate -> CircuitIR -> LayoutPlan -> Schemdraw SVG`
- On parse or validation failure:
  - keep the last successful preview
  - show an error state
  - do not destroy the preview container

## Related

- [Circuit Simulation](circuit-simulation.md)
- [Schematic Netlist Core](../architecture/schematic-netlist-core.md)
