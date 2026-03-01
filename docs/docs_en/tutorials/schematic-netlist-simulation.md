---
aliases:
  - Schematic Netlist Simulation Tutorial
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
status: draft
owner: docs-team
audience: user
scope: Learn the Simulation page model, including Port vs Source vs Mode, and how to read result views
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# From Preview to Simulation: configure ports, sources, modes, and result views

This tutorial resolves the most common confusion in the Simulation page:

> A circuit port is not the same thing as an applied source.

## What You Will Learn

- the difference between `Port` and `Source`
- the difference between `Source Port` and `Source Mode`
- how to reason about single-pump, `DC + pump`, and double-pump setups
- how to read the main result view families

## Prerequisites

- Finish the first two tutorials

Useful references:

- [Circuit Simulation](../reference/ui/circuit-simulation.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [Simulation Result Views](../explanation/architecture/circuit-simulation/simulation-result-views.md)

## Step 1. Understand the boundary

- `Port`: defined in `ports`; a network boundary for the circuit
- `Source`: configured in `Applied Sources`; an actual drive used by `hbsolve`

A port can exist without any active source. That is normal.

## Step 2. Understand `Source Port` vs `Source Mode`

- `Source Port`: which physical port receives the source
- `Source Mode`: which harmonic-balance drive channel the source belongs to

Examples:

- `0` = DC
- `1` = first pump
- `1,0` = first pump in a double-pump configuration
- `0,1` = second pump in a double-pump configuration

## Step 3. Run a simple linear case

Use `SmokeStableSeriesLC` with:

- `Source Port = 1`
- `Source Current Ip = 0`
- `Source Mode = 1`

Run the simulation and confirm the result plot renders.

## Step 4. Understand `DC + pump` on the same port

In SNAIL-like or flux-driven examples, two sources may both target the same physical port:

- one DC source
- one pump source

This is valid because they are different drive channels.

## Step 5. Learn result views

Start with:

- `S`
- `Gain`
- `Impedance (Z)`

Then move to:

- `Admittance (Y)`
- `Quantum Efficiency (QE)`
- `Commutation (CM)`

## Self-check

You pass this page only if you can explain:

1. why a port can exist without a source
2. why two sources can share the same `Source Port`
3. why `Source Port` and `Source Mode` are different dimensions

## Next

- [Design your own circuit: from requirements to a working Schematic Netlist](designing-custom-circuits.md)
