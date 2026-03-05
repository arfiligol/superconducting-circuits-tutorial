---
aliases:
  - Designing Custom Circuits
  - Custom Circuit Authoring
tags:
  - diataxis/tutorial
  - audience/user
  - topic/circuit-design
status: stable
owner: docs-team
audience: user
scope: Guidance for designing custom circuits from source netlist to runnable setup
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Designing Custom Circuits

This page focuses on practical checks when building custom circuits.

## Checklist

1. Define reusable parameter interfaces in `components` (`default`/`value_ref`).
2. Keep `topology` for connectivity only.
3. Prefer `repeat` to reduce expanded-form maintenance cost.
4. Use Expanded Netlist Preview as deterministic validation.
5. Validate base mode first in Simulation, then sideband/post-processing.

## Related

- [Circuit Netlist](../reference/data-formats/circuit-netlist.en.md)
- [Schema Editor UI](../reference/ui/schema-editor.en.md)
- [Simulation Workflow](simulation-workflow.en.md)
