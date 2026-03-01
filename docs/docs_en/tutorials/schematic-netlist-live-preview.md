---
aliases:
  - Understand Live Preview
tags:
  - diataxis/tutorial
  - audience/user
  - topic/visualization
  - topic/simulation
status: draft
owner: docs-team
audience: user
scope: Learn how to write Schematic Netlist structures that produce predictable Live Preview output
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Understand Live Preview: make Schemdraw produce the structure you expect

This tutorial teaches the core rule of the current system:

> `Live Preview` is only as good as the structural semantics you provide.

## What You Will Learn

- how to distinguish `series` vs `shunt`
- how to model a parallel branch correctly
- why `role` and `layout.profile` matter
- how to debug a preview that is valid but visually wrong

## Prerequisites

- Finish [Schematic Netlist Getting Started](schematic-netlist-getting-started.md)

Background pages:

- [Schematic Netlist Live Preview](../explanation/architecture/design-decisions/circuit-schema-live-preview.md)
- [LayoutPlan and Renderer Boundaries](../explanation/architecture/circuit-simulation/layout-plan-and-renderer-boundaries.md)

## Core model

The preview pipeline is:

1. Parse
2. Validate
3. Build `CircuitIR`
4. Build `LayoutPlan`
5. Render with `Schemdraw`

`Schemdraw` is not the layout engine. Your structure drives the layout.

## Step 1. Learn the difference between series and shunt

- non-ground to non-ground usually means a series-path element
- signal-node to ground usually means a shunt branch

## Step 2. Build a predictable parallel branch

Use a qubit-like branch where `Lq` and `Cq` share the same pin pair `("1", "2")`, while a separate capacitor connects `"2"` to `"gnd"`.

The key is not the names. The key is:

- `pins`
- `role`
- `layout.profile`

## Step 3. Intentionally break it once

Change one of the parallel branch elements so it connects to ground instead of the same node pair.

You should see the preview change into a different topology.

That is the main lesson: the renderer follows the structure you wrote, not the topology you intended mentally.

## Step 4. Use `layout.profile`

Use:

- `generic` for simple LC structures
- `qubit_readout` for floating-island / qubit-like structures
- `jpa` for amplifier-like nonlinear cores
- `jtwpa` for ladder / transmission-line structures

## Self-check

You pass this page only if you can:

1. write a parallel branch between two non-ground nodes
2. explain why moving one pin to ground changes the visual structure
3. choose between `generic` and `qubit_readout` for a qubit-like circuit

## Next

- [From Preview to Simulation: configure ports, sources, modes, and result views](schematic-netlist-simulation.md)
