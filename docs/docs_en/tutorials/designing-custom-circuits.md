---
aliases:
  - Designing Custom Circuits
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
  - topic/visualization
status: draft
owner: docs-team
audience: user
scope: Build a custom Schematic Netlist from requirements and iterate it through preview and simulation
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Design your own circuit: from requirements to a working Schematic Netlist

This is the final tutorial in the series.

The goal is simple:

> Turn a circuit idea into a working `Schematic Netlist` that you can preview, simulate, and refine in the WebUI.

## What You Will Learn

- how to translate plain-language requirements into `ports`, `nodes`, `instances`, and `roles`
- how to choose `layout.profile`
- how to debug a wrong preview by fixing structure first

## Prerequisites

- Finish the first three tutorials

Keep these reference pages open:

- [Schematic Netlist Core](../reference/architecture/schematic-netlist-core.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [LayoutPlan and Renderer Boundaries](../explanation/architecture/circuit-simulation/layout-plan-and-renderer-boundaries.md)

## Step 1. Start from a requirement sentence

Write the intended circuit in plain language first.

Example:

> A one-port readout line with a 50 Ohm termination, a qubit-like parallel branch between two nodes, and a small shunt capacitor to ground.

## Step 2. Extract nodes

Start with nodes, not components.

For example:

- `1`: drive / readout node
- `2`: floating island
- `gnd`: ground reference

## Step 3. Define ports

Ports define external boundaries first. They are not components.

## Step 4. Define instances

Only now list components.

Use:

- `kind`
- `pins`
- `value_ref`
- `role`

If two components belong to the same branch, make sure they truly share the same pin pair.

## Step 5. Choose `layout.profile`

Use the smallest profile that matches the circuit semantics:

- `generic`
- `qubit_readout`
- `jpa`
- `jtwpa`

## Step 6. Iterate in the right order

The correct loop is:

1. `Format`
2. inspect `Live Preview`
3. fix structure first
4. run `Simulation`
5. refine values only after the structure is correct

## Final check

You should be able to do all of the following without copying a template:

1. build a one-port readout resonator
2. build a qubit-like parallel branch structure
3. configure a valid `DC + pump` simulation setup
4. decide whether a bad preview is a schema problem or a current renderer limitation

## Related

- [Schematic Netlist Getting Started](schematic-netlist-getting-started.md)
- [Understand Live Preview](schematic-netlist-live-preview.md)
- [From Preview to Simulation](schematic-netlist-simulation.md)
