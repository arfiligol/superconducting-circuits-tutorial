---
aliases:
- Schemas UI
- Circuit Schemas Interface
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /schemas page contract for listing, search/sort/pagination, and large-list interaction
version: v0.2.0
last_updated: 2026-03-03
updated_by: docs-team
---

# Schemas

This page defines the formal UI/UX contract for `/schemas`.

## Page Sections

1. `Header Actions` (including `New Circuit`)
2. `Schema List`

## Schema List Contract

`Schema List` must provide:

- search (by schema name)
- sorting (at minimum `name`, `created_at`)
- pagination
- per-schema `Edit` / `Delete` actions

!!! note "Presentation form"
    Table or card-list are both allowed.
    If using card-list, it must still provide table-equivalent search/sort/pagination behavior.

!!! important "Card-list density and alignment"
    For card-list mode, default to one full-width card per row.
    Keep table-like alignment across rows: name area, `Created` area, and right-side `Edit/Delete` action area must align consistently.

!!! tip "Search input UX"
    Live search is allowed, but list refreshes must not steal focus from the search field.

## Data Loading Boundary

Schema list queries should load summary-only fields (`id`, `name`, `created_at`).

!!! warning "No definition preload on list page"
    `definition_json` is a large field and should only be loaded in `/schemas/{id}` or on explicit demand.

## Delete Action Contract

- `Delete` must provide explicit success/failure feedback
- successful deletion should refresh the current list page
- if deletion makes the current page out of range, move back to the last valid page

## Performance SLO (UI Layer)

- default page size should be `12` (card list) or `20` (table)
- page switches should render only current-page rows/cards
- with hundreds of schemas, interaction should remain responsive (no full-list render on each update)
