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
scope: Circuit Simulation architecture index for schema editing, live preview semantics, and editor formatting strategy
version: v0.2.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Circuit Simulation

## Topics

- [Circuit Schema Live Preview](../design-decisions/circuit-schema-live-preview.md)
- [Schema Editor Formatting](../design-decisions/schema-editor-formatting.md)
  Why formatting is treated as an architecture decision, and how it stays bounded by source-form SoT and the shared expansion pipeline.
- [Live Preview Domain Semantics Profiles](../design-decisions/live-preview-domain-semantics.md)
- [Simulation Result Views](simulation-result-views.md)
  Why raw, post-processed, and sweep results are separate nodes while still sharing one interaction model.
