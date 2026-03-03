---
aliases:
- Raw Data Browser UI
- Raw Data Browser Interface
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /raw-data page contract for dataset browsing, preview tables, and large-data UX boundaries
version: v0.2.0
last_updated: 2026-03-03
updated_by: docs-team
---

# Raw Data Browser

This page defines the formal UI/UX contract for `/raw-data`, with emphasis on large-data stability.

## Page Sections

1. `Dataset List`
2. `Dataset Preview`
3. `Visualization Preview`

!!! note "Layout"
    `Dataset List` and `Dataset Preview` should be stacked vertically in full width
    instead of side-by-side columns, so long names and large tables remain readable.

## Dataset List Contract

`Dataset List` must provide:

- pagination
- column sorting via clickable table headers
- text filtering/search
- row-click dataset selection

!!! tip "Live-search interaction"
    Live search is allowed, but typing must not lose focus due to input re-mounting.

!!! important "Data query boundary"
    Dataset list queries must use summary-only fields (for example `id`, `name`, `created_at`).
    Do not load DataRecord waveform payloads in list queries.

## Dataset Preview Contract

After selecting a dataset, the Data Record table in `Dataset Preview` must provide:

- pagination
- column sorting via clickable table headers
- column filtering (at minimum `data_type`, `representation`)
- row-click record selection

!!! note "Sorting controls"
    If header-click sorting is available in the table, do not add extra `Sort By` / `Order` selectors.

!!! warning "No bulk payload preload"
    Preview tables should only render metadata (`id`, `data_type`, `parameter`, `representation`).
    Do not send full `axes` / `values` payloads to the frontend in one batch.

## Visualization Preview Contract

- Detailed record payload should be loaded only after the user clicks one row.
- Switching dataset or page should not automatically reload all plot payloads.

!!! tip "Lazy detail fetch"
    Keep two query paths:
    - list path: metadata only
    - detail path: by selected record id

## Interaction Rules

- `Analyze This Dataset` should depend only on selected dataset id.
- Switching dataset should reset selected-record state.
- If selected record is no longer visible in current table page, behavior must be deterministic (clear or keep, but not random).

## Performance SLO (UI Layer)

- default table page size should be `20` (adjustable)
- one render cycle must not include multi-thousand full payload records
- UI should avoid websocket disconnect risk caused by oversized one-shot messages
