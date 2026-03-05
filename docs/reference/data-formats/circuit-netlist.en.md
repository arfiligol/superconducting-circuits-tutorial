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
scope: "CircuitDefinition netlist format: value_ref, parameters, and sweep override rules"
version: v1.2.0
last_updated: 2026-03-05
updated_by: codex
---

# Circuit Netlist Schema

`CircuitDefinition` is the shared netlist format used by the UI Schema Editor and simulation flow.

## Structure

- `name: str`
- `parameters: dict[str, ParameterSpec]`
- `topology: list[(element_name, node1, node2, value_ref_or_port_index)]`

`ParameterSpec`:

| Key | Type | Required | Description |
|---|---|---|---|
| `default` | `float` | ✅ | Default numeric value (used when no sweep override exists) |
| `unit` | `str` | ✅ | Unit string |
| `sweepable` | `bool` | ❌ | Whether this parameter is selectable by sweep UI (default `true`) |

---

## Core Rules (Normative)

1. Port elements (`P*`) must use an integer port index in topology position 4 (for example `1`).
2. Non-port elements must use `value_ref: str` in topology position 4.
3. Every non-port `value_ref` must exist in `parameters`.
4. Every `parameters[value_ref]` must include `default` and `unit`.
5. Sweep only overrides execution values in `parameters[*].default`; topology connectivity must not change.
6. `K*` mutual coupling rows must use inductor element names (not nodes) in positions 2/3.
7. `K*` mutual coupling rows must use an existing coupling component reference in position 4.

---

## Topology Item Format

`(element_name, node1, node2, value_ref_or_port_index)`

| Position | Type | Description |
|---|---|---|
| `element_name` | `str` | Element name (symbol inferred by prefix) |
| `node1` | `str` | Endpoint node 1 |
| `node2` | `str` | Endpoint node 2 |
| `value_ref_or_port_index` | `int \| str` | Integer for ports; parameter key for non-port elements |

---

## Component and Unit Rules

| Component | Name Prefix | Allowed Units | Example | Notes |
|---|---|---|---|---|
| Port | `P*` | `-` | `("P1", "1", "0", 1)` | Uses integer port index; no `parameters` entry required |
| Resistor | `R*` | `Ohm`, `kOhm`, `MOhm` | `("R1", "1", "0", "R_port")` | A shunt resistor per port is strongly recommended (commonly `50 Ohm`) |
| Inductor | `L*` | `H`, `mH`, `uH`, `nH`, `pH` | `("L1", "1", "2", "Lj")` | `Lj*` is treated as Josephson Junction |
| Capacitor | `C*` | `F`, `mF`, `uF`, `nF`, `pF`, `fF` | `("C1", "1", "2", "Cc")` | Multiple elements can share one `value_ref` |
| Josephson Junction | `Lj*` | `H`, `mH`, `uH`, `nH`, `pH` | `("Lj1", "2", "0", "Lj")` | Rendered as junction symbol in preview |
| Mutual Coupling | `K*` | `-` (recommended dimensionless) | `("K1", "L1", "L2", "Kc")` | Positions 2/3 are inductor element names; position 4 references a coupling component |

!!! note "Case handling"
    Unit parsing is currently case-insensitive (for example `ohm` and `Ohm` both work), but examples should use canonical forms from this table.

!!! note "Ground node"
    The only supported ground token is string `0`. `gnd` / `GND` are not supported.

---

## Minimal Runnable Example

```python
{
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
        "Lj": {"default": 1000.0, "unit": "pH"},
        "Cc": {"default": 100.0, "unit": "fF"},
        "Cj": {"default": 1000.0, "unit": "fF"}
    },
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R_port"),
        ("C1", "1", "2", "Cc"),
        ("Lj1", "2", "0", "Lj"),
        ("C2", "2", "0", "Cj")
    ]
}
```

---

## Sweep Rules

- Sweep is designed to override parameter values, not topology.
- Single-parameter sweep: value sequence for one `value_ref`.
- Multi-parameter sweep: Cartesian product (or paired scan) over multiple `value_ref` keys.
- Parameters without sweep override use `parameters[*].default`.

!!! note "Bias/source sweep boundary"
    Source-side bias sweep targets (for example `sources[1].current_amp`) belong to
    the `Simulation Setup` contract, not to the netlist format itself.
    This page specifies only netlist-parameter sweep semantics.

---

## Live Preview Binding Rule

Live Preview must resolve displayed values via topology position 4 (`value_ref`) to `parameters[value_ref]`.

Example:

- `("C2", "2", "0", "Cj")` must show `C2` with the default value from `Cj`
- It must not resolve by `element_name == C2` and lookup `parameters["C2"]`

---

## Common Error Mapping

| Message fragment | Likely cause | Recommendation |
|---|---|---|
| `topology references undefined parameter` | `value_ref` in topology is missing in `parameters` | Add `parameters[value_ref]` |
| `non-port topology entries must use string value_ref` | A non-port element used non-string value_ref | Change it to a string parameter key |
| `parameter default missing` | `parameters[*].default` is missing | Add a default value |
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
3. non-`P*` rows must use parameter reference (`value_ref`) at position 4
4. `K*` rows must use inductor names at positions 2/3 and coupling component at position 4

### Failure Modes

- undefined parameter reference
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
4. runtime error messages map to this spec instead of hidden legacy compatibility paths

## Related

- [Simulation Python API](../../how-to/simulation/python-api.md)
- [Data Formats Overview](index.md)
