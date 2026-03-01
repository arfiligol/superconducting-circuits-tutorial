---
aliases:
- Circuit Simulation Architecture
- 電路模擬架構
tags:
- diataxis/explanation
- audience/team
- topic/architecture
- topic/simulation
status: draft
owner: docs-team
audience: team
scope: Why Circuit Simulation now centers on Schematic Netlist, shared SoT, and staged preview/simulation compilation
version: v0.3.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Circuit Simulation

Circuit Simulation now centers on `Schematic Netlist`, not the old tuple-style topology format.

This section explains:

1. why a new source language is required
2. why Live Preview and Simulation must share one SoT
3. why `Schemdraw` must remain a renderer rather than a layout engine

## Topics

- [LayoutPlan and Renderer Boundaries](layout-plan-and-renderer-boundaries.md)
- [Schematic Netlist Live Preview](../design-decisions/circuit-schema-live-preview.md)
- [Schema Editor Formatting](../design-decisions/schema-editor-formatting.md)
- [Live Preview Domain Semantics Profiles](../design-decisions/live-preview-domain-semantics.md)
- [Simulation Result Views](simulation-result-views.md)

## Related

- [Architecture Reference / Schematic Netlist Core](../../../reference/architecture/schematic-netlist-core.md)
- [Architecture](../index.md)
- [Pipeline](../pipeline/index.md)
