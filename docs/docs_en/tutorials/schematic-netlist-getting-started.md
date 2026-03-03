---
aliases:
- Circuit Netlist Getting Started
- Circuit Netlist Intro
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# Circuit Netlist Getting Started

The goal of this tutorial is simple: write your first minimal **Circuit Netlist** in the WebUI and complete a successful simulation.

!!! tip "Success criteria"
    After this page, you should be able to retype a single-port LC circuit on your own instead of only copying it.

## Minimal working example (explicit form)

```python
{
    "name": "SmokeStableSeriesLC",
    "components": [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "L1", "default": 10.0, "unit": "nH"},
        {"name": "C1", "default": 1.0, "unit": "pF"},
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R1"),
        ("L1", "1", "2", "L1"),
        ("C1", "2", "0", "C1"),
    ],
}
```

## Understanding each field

### `components`

- the component instance list, and the main authoring layer
- each row requires: `name`, `unit`
- value source must be exactly one of:
  - `default`: fixed value
  - `value_ref`: a reference to a sweepable parameter

### `topology`

- the actual connection structure
- in the simplest case, each row is a four-tuple: `(element, node1, node2, value_ref)`
- standard elements use a component name in the last field
- `P*` entries represent ports and use an integer port index in the last field

### `parameters` (not needed yet)

- you do not need `parameters` for this first example
- add them later only when a value should become sweepable or shared

!!! note "Node rules"
    - nodes must be numeric strings
    - `0` is the only legal ground token
    - `gnd` is not accepted

## Workflow

1. Open `/schemas/new`
2. Paste the netlist above
3. Click `Format`
4. Click `Save Schema`
5. Go to `/simulation` and select this schema
6. Run a simulation with the default sweep

## What you do not need yet

!!! info "Next page"
    This tutorial only teaches the explicit form.

    If you hit long chains, repeated cells, or JTWPA-like structures, do not copy rows 100 times. Learn `repeat` on the next page.

## Common mistakes

!!! warning "Most common"
    Every `components[*]` row must have a resolvable value.

- missing both `default` and `value_ref`: wrong
- including both `default` and `value_ref`: also wrong

!!! warning "Another common mistake"
    In `topology`, standard elements point to component names, not raw numbers or parameter names.

- `("L1", "1", "2", "L1")`: correct, because `components` contains `L1`
- `("L1", "1", "2", 10.0)`: wrong, because `topology` does not carry raw values

## Self-check

After this page, you should be able to explain:

- why `components` are the main authoring layer
- why `P1` ends with the integer `1`
- why standard topology rows end with a component name

## Related

- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [Repeating Circuit Sections](../repeating-circuit-sections.md)
