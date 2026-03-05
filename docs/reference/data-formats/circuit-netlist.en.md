---
aliases:
  - "Circuit Netlist Schema"
  - "電路 Netlist 規格"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/simulation
status: stable
owner: docs-team
audience: team
scope: "CircuitDefinition netlist format: components-first, topology, optional parameters"
version: v1.3.0
last_updated: 2026-03-06
updated_by: codex
---

# Circuit Netlist Schema

`CircuitDefinition` is the shared netlist format used by the UI Schema Editor and simulation flow.
The project currently uses a **components-first** model: `components` is the primary authoring block, while `parameters` is an optional advanced block.

## Structure

- `name: str`
- `components: list[ComponentSpec]`
- `topology: list[(element_name, node1, node2, component_name_or_port_index)]`
- `parameters: list[ParameterSpec]` (optional)

`ComponentSpec`:

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | ✅ | Unique component name |
| `unit` | `str` | ✅ | Unit string |
| `default` | `float` | one-of | Fixed-value component |
| `value_ref` | `str` | one-of | Parameter-linked component |

`default` and `value_ref` are mutually exclusive and exactly one must be present.

`ParameterSpec` (only needed when `value_ref` is used):

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | ✅ | Parameter name referenced by `value_ref` |
| `default` | `float` | ✅ | Default parameter value |
| `unit` | `str` | ✅ | Unit string |

---

## Core Rules (Normative)

1. `components` and `topology` are required; `parameters` is optional.
2. Every `components[*]` must include `name`, `unit`, and exactly one of `default` / `value_ref`.
3. If a component uses `value_ref`, `parameters` must include matching `name`, with the same `unit`.
4. Port elements (`P*`) must use an integer port index in topology position 4.
5. Non-port, non-`K*` rows must use an existing component name in topology position 4.
6. `K*` mutual coupling rows must use inductor element names (not nodes) in positions 2/3.
7. `K*` mutual coupling rows must use an existing coupling component name in position 4.
8. Node tokens must be numeric strings only, and ground token must be `"0"`.

---

## Topology Item Format

`(element_name, node1, node2, component_name_or_port_index)`

| Position | Type | Description |
|---|---|---|
| `element_name` | `str` | Element name (symbol inferred by prefix) |
| `node1` | `str` | Endpoint node 1 |
| `node2` | `str` | Endpoint node 2 |
| `component_name_or_port_index` | `int \| str` | Integer for ports; component name for non-port rows (for example `C1`, `Lj1`) |

---

## Component and Unit Rules

| Component | Name Prefix | Allowed Units | Example | Notes |
|---|---|---|---|---|
| Port | `P*` | `-` | `("P1", "1", "0", 1)` | Uses integer port index |
| Resistor | `R*` | `Ohm`, `kOhm`, `MOhm` | `("R1", "1", "0", "R1")` | One shunt resistor per port is recommended (commonly `50 Ohm`) |
| Inductor | `L*` | `H`, `mH`, `uH`, `nH`, `pH` | `("L1", "1", "2", "L1")` | `Lj*` is treated as Josephson Junction |
| Capacitor | `C*` | `F`, `mF`, `uF`, `nF`, `pF`, `fF` | `("C1", "1", "2", "C1")` | Shared parameter behavior uses `value_ref`, not direct topology parameter references |
| Josephson Junction | `Lj*` | `H`, `mH`, `uH`, `nH`, `pH` | `("Lj1", "2", "0", "Lj1")` | Rendered as junction symbol in preview |
| Mutual Coupling | `K*` | Project convention (commonly `H`) | `("K1", "L1", "L2", "K1")` | Positions 2/3 are inductor element names; position 4 is coupling component name |

!!! note "Case handling"
    Unit parsing is currently case-insensitive (for example `ohm` and `Ohm` both work), but examples should use canonical forms from this table.

!!! note "Ground node"
    The only supported ground token is string `0`. `gnd` / `GND` are not supported.

---

## Minimal Runnable Example (components-only, no parameters)

```python
{
    "name": "SmokeStableSeriesLC",
    "components": [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "C1", "default": 100.0, "unit": "fF"},
        {"name": "Lj1", "default": 1000.0, "unit": "pH"},
        {"name": "C2", "default": 1000.0, "unit": "fF"}
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R1"),
        ("C1", "1", "2", "C1"),
        ("Lj1", "2", "0", "Lj1"),
        ("C2", "2", "0", "C2")
    ]
}
```

## Advanced Example (components + parameters)

```python
{
    "name": "SweepableSeriesLC",
    "parameters": [
        {"name": "Lj", "default": 1000.0, "unit": "pH"},
        {"name": "Cj", "default": 1000.0, "unit": "fF"}
    ],
    "components": [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "C1", "default": 100.0, "unit": "fF"},
        {"name": "Lj1", "value_ref": "Lj", "unit": "pH"},
        {"name": "C2", "value_ref": "Cj", "unit": "fF"}
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R1"),
        ("C1", "1", "2", "C1"),
        ("Lj1", "2", "0", "Lj1"),
        ("C2", "2", "0", "C2")
    ]
}
```

---

## Sweep Rules

- Netlist sweep targets come from deduplicated `components[*].value_ref`.
- Sweep overrides execution values bound to those `value_ref` targets, without changing topology.
- Components not overridden by sweep continue using `default` (or the linked parameter default).

!!! note "Bias/source sweep boundary"
    Source-side bias sweep targets (for example `sources[1].current_amp`) belong to
    the `Simulation Setup` contract, not to the netlist data format itself.

---

## Live Preview Binding Rule

Live Preview must resolve values through topology position 4 as a component reference first:

1. If the component is `default`-backed, display `default`.
2. If the component is `value_ref`-backed, display `parameters[name=value_ref].default`.

Example:

- `("C2", "2", "0", "C2")` with `C2.value_ref = "Cj"` must display the default from `Cj`.
- Topology position 4 must not be interpreted as a parameter key directly.

---

## Common Error Mapping

| Message fragment | Likely cause | Recommendation |
|---|---|---|
| `Circuit Definition must define 'components'.` | Missing `components` block | Add `components` |
| `Component 'X' must define exactly one of 'default' or 'value_ref'.` | Component has both (or neither) `default` / `value_ref` | Keep exactly one |
| `Component 'X' references undefined parameter 'Y'.` | `value_ref` does not exist in `parameters` | Add `parameters[name=Y]` |
| `Topology row 'X' references undefined component 'Y'.` | Topology position 4 points to unknown component | Use an existing component name |
| `Topology row 'X' must reference a component name.` | Non-port row uses non-string position 4 | Use a string component name |
| `Ports without resistors detected` | Port impedance is not defined | Add matching `R*` branch (commonly `R50`) |
| `SingularException` | Topology/value combination creates singular matrix | Check connectivity, values, and units |

## Runtime Contract Snapshot

### Input

- source-form netlist (saved from Schema Editor)
- optional Simulation Setup overrides (for example, sweep values)

### Output

- expanded/validated netlist (runtime-only view, never persisted back to DB)
- explicit validation failures mapped to concrete fields/rules

### Invariants

1. ground token must be string `0`
2. `P*` rows must use integer port index at position 4
3. non-`P*` / non-`K*` rows must use component name at position 4
4. `K*` rows must use inductor names at positions 2/3 and coupling component at position 4

### Failure Modes

- undefined component reference
- undefined parameter reference (from `value_ref`)
- invalid node token / invalid ground token
- `K*` references unknown inductor/component names
- singular matrix after topology lowering (numerical layer)

## Code Reference Map

- parser / validator:
  - [`circuit.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/simulation/domain/circuit.py)
- simulation page expanded preview:
  - [`simulation/__init__.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/simulation/__init__.py)
- schema editor source/preview binding:
  - [`schema_editor.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/schema_editor.py)

## Runtime Parity Checklist

Before release, verify:

1. Data format spec and parser rules are aligned (`P*` / `K*` / ground token)
2. Schema Editor Expanded Preview and Simulation Netlist Configuration share one expansion pipeline
3. DB stores source-form only, never expanded-form
4. Runtime error messages map to this spec instead of hidden legacy compatibility paths

## Related

- [Simulation Python API](../../how-to/simulation/python-api.md)
- [Data Formats Overview](index.md)
