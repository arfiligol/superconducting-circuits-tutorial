---
aliases:
  - Schema Editor Formatting
  - Schema Editor Formatting Strategy
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/ui
status: stable
owner: docs-team
audience: team
scope: Design rationale and boundaries for Schema Editor formatting behavior
version: v0.2.0
last_updated: 2026-03-06
updated_by: codex
---

# Schema Editor Formatting

This page answers only two questions: why formatting exists, and why its boundary is defined this way.
Exact button behavior and failure contracts live in Reference.

## Decision Context

The Schema Editor treats source form as the only persistent SoT.
Users repeatedly revise netlists, so a predictable formatter is part of keeping those edits reviewable and debuggable.

## Why This Is an Architecture Decision

- it affects source-form readability and error localization, not just visual polish
- it keeps the editor mental model aligned with the Simulation expansion pipeline
- it improves diff quality when multiple contributors edit the same circuit definition

## Design Boundaries

1. `Format` may change source-text layout only; it must not change expansion semantics
2. failures must preserve the original text
3. formatting must operate on the same editor-state model, without introducing a second text authority
4. `/schemas/{id}` and `/simulation` must read expanded netlists from the same parse/validate/expand pipeline

## Non-Goals

- the editor is not becoming a full IDE/LSP surface
- the formatter is not a schema-migration engine for upgrading legacy syntax

## Where the Formal Contract Lives

!!! important "Reference SoT"
    For field behavior, save semantics, and failure handling, see
    [Schema Editor UI Reference](../../../reference/ui/schema-editor.en.md)

## Related

- [Schema Editor UI Reference](../../../reference/ui/schema-editor.en.md)
- [Circuit Netlist Schema](../../../reference/data-formats/circuit-netlist.en.md)
- [Circuit Simulation UI Reference](../../../reference/ui/circuit-simulation.en.md)
