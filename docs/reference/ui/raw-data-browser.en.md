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
scope: /raw-data page contract for design browsing, trace preview, and large-data UX boundaries
version: v0.3.0
last_updated: 2026-03-08
updated_by: codex
---

# Raw Data Browser

This page defines the formal UI/UX contract for `/raw-data`, with emphasis on large-data stability.

## Page Sections

1. `Design List`
2. `Design Summary + Trace Preview`
3. `Visualization Preview`
4. `Design Summary (Read-only)`

!!! note "Layout"
    `Design List` and `Design Summary + Trace Preview` should be stacked vertically in full width
    instead of side-by-side columns, so long names and large tables remain readable.

## Design List Contract

`Design List` must provide:

- pagination
- column sorting via clickable table headers
- text filtering/search
- row-click design selection

!!! tip "Live-search interaction"
    Live search is allowed, but typing must not lose focus due to input re-mounting.

!!! important "Data query boundary"
    Design list queries must use summary-only fields (for example `id`, `name`, `created_at`).
    Do not load trace waveform payloads in list queries.

## Design Summary + Trace Preview Contract

After selecting a design, the `Trace Preview` table must provide:

- pagination
- column sorting via clickable table headers
- column filtering (at minimum `data_type`, `representation`)
- row-click trace selection
- design-scope source context (at minimum `source_kind`, `stage_kind`, and `trace batch`)

!!! note "Sorting controls"
    If header-click sorting is available in the table, do not add extra `Sort By` / `Order` selectors.

!!! warning "No bulk payload preload"
    Preview tables should only render metadata (`id`, `data_type`, `parameter`, `representation`).
    Do not send full `axes` / `values` payloads to the frontend in one batch.

!!! important "Cross-source browse contract"
    If one `Design` contains circuit, layout, and measurement traces at the same time,
    this page must clearly distinguish each trace by `source_kind`, `stage_kind`,
    and the owning `TraceBatchRecord` provenance boundary.
    These fields must come from the trace-first / TraceBatch metadata path,
    not from inline numeric payloads or backend-specific store locators.

## Design Summary Contract

!!! note "Current behavior (2026-03-04)"
    Older `/raw-data` builds exposed editable metadata controls
    (`Device Type`, `Capabilities`, `Auto Suggest`, `Save Metadata`).

!!! important "Contract (Dashboard-only edit entry)"
    `/raw-data` must not expose any metadata write path.
    This page may only display a design-level read-only summary;
    the current phase-2 compatibility layer still reads from `source_meta.dataset_profile`.

!!! warning "No write interactions"
    Raw Data Browser must not render `Auto Suggest`, `Save Metadata`, or equivalent write controls.

### Cross-source Workflow Summary

`Design Summary` must additionally expose:

- `Current Design Scope`
- `Trace source summary` (trace and batch counts per source)
- `Latest provenance summary` (latest batch source and stage)
- `Compare readiness`

!!! important "Compare readiness"
    Compare readiness must use an explicit state:
    - `Ready`: at least two source kinds exist in the same design scope
    - `Inspect only`: only one source is currently available, or provenance is visible but compare is not appropriate yet
    - `Blocked`: the design scope is still missing the minimum trace-first compare inputs

!!! warning "Do not hide the state"
    If compare is not fully exposed yet, the page must show a clear empty-state / blocked-state
    instead of silently omitting the cross-source section.

## Visualization Preview Contract

- Detailed trace payload should be loaded only after the user clicks one row.
- Switching design or page should not automatically reload all plot payloads.

!!! tip "Lazy detail fetch"
    Keep two query paths:
    - list path: metadata only
    - detail path: by selected trace id

## Interaction Rules

- `Analyze This Design` should depend only on selected design id.
- Switching design should reset selected-trace state.
- If selected trace is no longer visible in current table page, behavior must be deterministic (clear or keep, but not random).
- Metadata save success must be reflected in the current session immediately (no app restart required).

!!! important "Relation to Characterization"
    Characterization analysis availability consumes the design-level profile summary.
    Metadata writes must happen on Dashboard; Raw Data only presents summary state.

!!! important "Compare authority"
    Compare-ready / inspect-only state on this page must rely on design-scoped trace metadata,
    `TraceBatchRecord` provenance, and trace-first compatibility only.
    Do not treat large numeric payload in the metadata DB or point-per-record projections as the authority.

## Performance SLO (UI Layer)

- default table page size should be `20` (adjustable)
- one render cycle must not include multi-thousand full trace payloads
- UI should avoid websocket disconnect risk caused by oversized one-shot trace messages
