---
aliases:
  - Circuit Netlist Getting Started
  - Netlist Basics
tags:
  - diataxis/tutorial
  - audience/user
  - topic/netlist
status: stable
owner: docs-team
audience: user
scope: Minimal onboarding path for Circuit Netlist Source Form
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Circuit Netlist Getting Started

This page gives a minimal onboarding path for Circuit Netlist Source Form.

## Quick Start

1. In Schema Editor, define `name`, `components`, and `topology`.
2. Use `"0"` as the only ground token.
3. Each component must pick exactly one of `default` or `value_ref`.
4. Use Expanded Netlist Preview to verify compiled output.

## Related

- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.en.md)
- [Schema Editor UI](../reference/ui/schema-editor.en.md)
- [From Netlist to Simulation](schematic-netlist-simulation.en.md)
