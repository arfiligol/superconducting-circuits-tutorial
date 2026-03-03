---
aliases:
- From Netlist to Simulation
- Netlist to Simulation
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# From Netlist to Simulation

This tutorial focuses on the `/simulation` page: understanding `Port`, `Applied Sources`, and `HB Mode`, then reading the result views.

!!! note "Keep two views separate"
    Before entering Simulation, keep this model clear:

    - Schema Editor `Circuit Definition`: the source form (may contain `repeat`)
    - Schema Editor `Expanded Netlist Preview`: the expanded result
    - Simulation `Netlist Configuration`: the expanded result from the same expansion pipeline

## Core mental model

!!! important "Port is not Source"
    - `P1`, `P2`, and so on are the circuit's network ports
    - `Applied Sources` are the actual hbsolve drives applied in this run

That means:

- a circuit can have two ports and still use only one source
- the same port can host multiple sources

## `Source Port` vs `Source Mode`

!!! note "These are different dimensions"
    - `Source Port`: which physical port receives the drive
    - `Source Mode`: which HB mode slot the source belongs to (for example `0` = DC, `1` = first pump)

### Common mappings

- `0` -> `mode=(0,)`
- `1` -> `mode=(1,)`
- `1, 0` -> `mode=(1, 0)`
- `0, 1` -> `mode=(0, 1)`

## What `Netlist Configuration` shows

!!! info "Important"
    `Netlist Configuration` in `/simulation` is not just a copy of the editor text.

Its target behavior is:

- always show expanded `components`
- always show expanded `topology`
- if the schema uses `parameters`, also show expanded `parameters`

In other words, you inspect the normalized netlist that is actually sent to the backend.

!!! important "It is not the stored format"
    `Netlist Configuration` is a read-only compiled view.  
    The database still stores the source `Circuit Definition`.

This is especially useful for debugging:

- generated component names
- node numbering after `repeat`
- which values are fixed and which are sweepable parameters

## Basic workflow

1. Select the active schema at the top
2. Inspect `Netlist Configuration`
3. Configure the sweep range
4. Configure `Applied Sources`
5. Click `Run Simulation`
6. Switch views in `Simulation Results`: `S / Gain / Z / Y / QE / CM`

## Common mistakes

!!! warning "`Source Mode` is not part of the netlist"
    `Source Mode` does not belong in the Code Editor.
    It belongs to Simulation Setup, not to the Circuit Netlist syntax.

!!! warning "A `repeat` mistake is not a Simulation Setup problem"
    If `repeat` expands incorrectly, fix the netlist in the Schema Editor first instead of adjusting source settings.

## Self-check

After this page, you should be able to explain:

- why `P1` can exist without any Applied Source
- why the same port can carry both `0` (DC) and `1` (pump)
- why `Netlist Configuration` is especially useful for debugging `repeat`
