---
aliases:
- Dashboard UI
- Pipeline Dashboard
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: Contract for Pipeline /dashboard data summary and single editable Dataset Metadata entry
version: v0.1.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Dashboard

This page defines the formal `/dashboard` UI contract.

## Page Sections

1. `Dataset Selector`
2. `Dataset Metadata`
3. `Tagged Core Metrics`

## Dataset Metadata Contract

!!! note "Current behavior (2026-03-04)"
    Metadata editing entry points previously existed in both `/raw-data` and `/simulation`.

!!! important "Contract (Single editable entry)"
    `/dashboard` is the only editable entry for `Dataset Metadata`.
    Minimum editable fields:
    - `Target Dataset` (or equivalent dataset selector)
    - `Device Type`
    - `Capabilities`
    - `Auto Suggest`
    - `Save Metadata`

!!! warning "Cross-page write boundary"
    `/raw-data` and `/simulation` must not expose metadata write interactions and must stay read-only.

!!! note "Source marker"
    After dashboard save, `source_meta.dataset_profile.source` should persist as `manual_override`.

## UX Feedback Contract

- disable + show loading on save actions while request is in flight
- show toast-equivalent feedback for save success/failure
- reflect saved profile in current session without app restart

## Related

- [Raw Data Browser](raw-data-browser.en.md)
- [Circuit Simulation](circuit-simulation.en.md)
- [Dataset Record Schema](../data-formats/dataset-record.en.md)
