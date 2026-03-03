---
aliases:
- Designing Custom Circuits
- Custom Circuit Design Tutorial
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# Designing Custom Circuits

The current product focus is stable translation from requirements into a simulatable **Circuit Netlist**.

## Design order

1. write the requirement in plain language
2. define the component instances first (`components`)
3. decide which components should use fixed `default` values
4. add `parameters` only when a value should become sweepable or shared
5. list the node numbers (numeric strings only; ground is always `0`)
6. decide which rows stay explicit and which should use `repeat`
7. move to `/simulation` and configure sources plus sweep settings

## Example A: explicit form (short circuit)

```python
{
    "name": "FloatingBranch",
    "components": [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "Lq", "default": 10.0, "unit": "nH"},
        {"name": "Cq", "default": 1.0, "unit": "pF"},
        {"name": "Cg", "default": 0.1, "unit": "pF"},
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R1"),
        ("Lq", "1", "2", "Lq"),
        ("Cq", "1", "2", "Cq"),
        ("Cg", "2", "0", "Cg"),
    ],
}
```

## Example B: generated form (long chain, fixed values)

```python
{
    "name": "RepeatedLadder",
    "components": [
        {"name": "Rleft", "default": 50.0, "unit": "Ohm"},
        {"name": "Rright", "default": 50.0, "unit": "Ohm"},
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 1, "step": 1},
                    "n2": {"base": 2, "step": 1}
                },
                "emit": [
                    {"name": "L${n}_${n2}", "default": 80e-12, "unit": "H"},
                    {"name": "C${n2}_0", "default": 40e-15, "unit": "F"}
                ]
            }
        }
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "Rleft"),
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 1, "step": 1},
                    "n2": {"base": 2, "step": 1}
                },
                "emit": [
                    ("L${n}_${n2}", "${n}", "${n2}", "L${n}_${n2}"),
                    ("C${n2}_0", "${n2}", "0", "C${n2}_0")
                ]
            }
        },
        ("R5", "5", "0", "Rright"),
        ("P2", "5", "0", 2),
    ],
}
```

## Example C: generated form (sweepable values)

```python
{
    "name": "TunableLadder",
    "parameters": [
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "series": {
                    "csh": {"base": 40e-15, "step": 5e-15}
                },
                "emit": [
                    {"name": "Csh${index}", "default": "${csh}", "unit": "F"}
                ]
            }
        }
    ],
    "components": [
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 2, "step": 1}
                },
                "emit": [
                    {"name": "C${n}_0", "value_ref": "Csh${index}", "unit": "F"}
                ]
            }
        }
    ],
    "topology": [
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 2, "step": 1}
                },
                "emit": [
                    ("C${n}_0", "${n}", "0", "C${n}_0")
                ]
            }
        }
    ],
}
```

## When to switch to `repeat`

!!! tip "Rule of thumb"
    If you are repeatedly copying the same component or topology rows, and only changing suffixes, node numbers, or linear numeric values, switch to `repeat`.

If every section is actually different, keep the netlist explicit.

## When to add `parameters`

!!! note "Only in these cases"
    - a value should be swept in the Simulation UI
    - multiple components should share one tunable value
    - repeated cells need independently tunable values

If none of these apply, `components.default` is the simplest option.

## What not to do

!!! danger "Do not treat the editor as a script environment"
    - do not expect arbitrary `for`
    - do not expect `if`
    - do not place source / pump / hbsolve settings inside the netlist

Those are outside the scope of the current Code Editor syntax.

## Self-check

After this page, you should be able to explain:

- which circuits should stay explicit
- which circuits should be split into prelude / repeated body / epilogue
- which values should stay in `components.default`
- which values should be promoted to `parameters + value_ref`

## Related

- [Repeating Circuit Sections](../repeating-circuit-sections.md)
- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.md)
