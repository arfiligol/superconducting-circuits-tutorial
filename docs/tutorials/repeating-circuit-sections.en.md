---
aliases:
  - Repeating Circuit Sections
  - Repeat Blocks in Netlists
tags:
  - diataxis/tutorial
  - audience/user
  - topic/netlist
status: stable
owner: docs-team
audience: user
scope: How to use repeat blocks in Source Form for maintainable circuit definitions
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Repeating Circuit Sections

This page shows how to use `repeat` blocks in Source Form for reusable topology/components.

## Suggested Flow

1. Start from one explicit section that runs correctly.
2. Extract repetition into `repeat` with `count`, `start`, and `emit`.
3. Verify expansion and indexing in Expanded Netlist Preview.
4. Persist Source Form only; expanded form is runtime-only.

## Related

- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.en.md)
- [Restricted Generators Rationale](../explanation/architecture/circuit-simulation/restricted-netlist-generators.en.md)
