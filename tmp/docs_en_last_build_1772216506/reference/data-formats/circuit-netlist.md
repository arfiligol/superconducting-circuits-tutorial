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
version: v1.1.0
last_updated: 2026-02-27
updated_by: docs-team
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

!!! note "Case handling"
    Unit parsing is currently case-insensitive (for example `ohm` and `Ohm` both work), but examples should use canonical forms from this table.

!!! note "Ground node"
    `0`, `gnd`, and `GND` are all treated as ground nodes.

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

## Related

- [Simulation Python API](../../how-to/simulation/python-api.md)
- [Data Formats Overview](index.md)
