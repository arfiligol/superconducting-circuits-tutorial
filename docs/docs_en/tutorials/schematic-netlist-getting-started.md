---
aliases:
  - Schematic Netlist Getting Started
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
  - topic/visualization
status: draft
owner: docs-team
audience: user
scope: Build the first valid Schematic Netlist in the WebUI Code Editor and run the first simulation
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Schematic Netlist Getting Started

This tutorial has one goal:

> Write your first valid `Schematic Netlist` in the WebUI Code Editor, see a working `Live Preview`, and run a simulation successfully.

After finishing this page, you should be able to retype a one-port LC circuit without copying and pasting.

## What You Will Learn

- How to use the WebUI Code Editor in `/schemas/new`
- How to write a minimal `Schematic Netlist v0.1`
- How to use `Format` and `Save Schema`
- How to run the first simulation in `/simulation`

## Prerequisites

- The app is running
- You can open the `Schemas` and `Simulation` pages
- You do not need JPA or JTWPA knowledge yet

Reference pages:

- [Schematic Netlist Core](../reference/architecture/schematic-netlist-core.md)
- [Schematic Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Schema Editor](../reference/ui/schema-editor.md)

## Step 1. Enter the first netlist

Use the same minimal `SmokeStableSeriesLC` schema from the zh-TW tutorial.

```python
{
    "schema_version": "0.1",
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
        "L_main": {"default": 10.0, "unit": "nH"},
        "C_main": {"default": 1.0, "unit": "pF"},
    },
    "ports": [
        {
            "id": "P1",
            "node": "1",
            "ground": "gnd",
            "index": 1,
            "role": "signal",
            "side": "left",
        }
    ],
    "instances": [
        {
            "id": "R1",
            "kind": "resistor",
            "pins": ["1", "gnd"],
            "value_ref": "R_port",
            "role": "termination",
        },
        {
            "id": "L1",
            "kind": "inductor",
            "pins": ["1", "2"],
            "value_ref": "L_main",
            "role": "signal",
        },
        {
            "id": "C1",
            "kind": "capacitor",
            "pins": ["2", "gnd"],
            "value_ref": "C_main",
            "role": "shunt",
        },
    ],
    "layout": {"direction": "lr", "profile": "generic"},
}
```

## Step 2. Understand the minimum model

- `schema_version`: must be `"0.1"`
- `parameters`: all values referenced by `value_ref`
- `ports`: external network ports
- `instances`: actual components
- `layout`: high-level preview hints

## Step 3. Format and preview

Press `Format`.

You should see:

- stable indentation
- a valid `Live Preview`
- no loss of the preview state

## Step 4. Save and re-open

Press `Save Schema`.

For `v0.1` schemas, the app stores the exact editor text. If you formatted it first, the saved schema keeps that same style.

## Step 5. Run the first simulation

Open `/simulation`, select the saved schema, keep the default linear settings, and press `Run Simulation`.

You should see:

- success logs
- at least one `S11` result plot

## Self-check

You pass this tutorial only if you can explain:

1. what `ports` means
2. what `instances` means
3. why `value_ref` must match an existing parameter key

## Next

- [Understand Live Preview: make Schemdraw produce the structure you expect](schematic-netlist-live-preview.md)
