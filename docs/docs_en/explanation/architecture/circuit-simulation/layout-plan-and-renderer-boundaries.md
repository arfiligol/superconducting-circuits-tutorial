---
aliases:
  - LayoutPlan and Renderer Boundaries
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/visualization
status: draft
owner: docs-team
audience: team
scope: Explain why users must provide correct structural semantics before the preview can become stable, and why that responsibility does not belong to Schemdraw
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# LayoutPlan and Renderer Boundaries

This page answers a recurring question:

> Why does a preview still look wrong even when every component exists in the schema?

Because `Schemdraw` is not the layout engine. `LayoutPlan` can only produce stable output from the structural semantics you actually wrote.

## Responsibility split

- `Schematic Netlist`: your intended circuit semantics
- `CircuitIR`: normalized internal structure
- `LayoutPlan`: backbone, branch grouping, label slots, draw order
- `Schemdraw`: command-based rendering

## What users can control

Users directly control:

1. `pins`
2. `role`
3. `layout.direction`
4. `layout.profile`

Those four inputs decide whether the preview can converge to a readable layout.

## What Schemdraw should not be expected to guess

- which components belong to the same parallel branch
- which line is the primary signal backbone
- which port is signal vs pump vs bias
- which visual grammar is appropriate for JPA, JTWPA, or qubit-like structures

## Why this matters for tutorials

This is why the tutorial series teaches:

- node relationships
- `series / shunt / parallel branch`
- `Port / Source / Mode`
- `layout.profile`

before expecting users to build larger circuits reliably.

## Related

- [Schematic Netlist Core](../../../reference/architecture/schematic-netlist-core.md)
- [Schematic Netlist Live Preview](../design-decisions/circuit-schema-live-preview.md)
- [Live Preview Domain Semantics Profiles](../design-decisions/live-preview-domain-semantics.md)
