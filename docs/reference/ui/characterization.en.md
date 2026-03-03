---
aliases:
- Characterization UI
- Characterization Interface
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /characterization contract for Source Scope, Run Analysis, trace selection, and unified Result View
version: v0.5.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Characterization

This page defines the formal `/characterization` UI contract.

## Core Data Model

`/characterization` must use:

- `DatasetRecord` as the container
- `ResultBundleRecord` as one run/import/analysis batch boundary
- `DataRecord` as trace-level payload
- `ResultArtifact` as the unified render contract for Result View

## Result Artifact Contract

After each analysis run, the UI must render from an artifact manifest instead of
directly coupling to `DerivedParameter` naming details.

Minimum `ResultArtifact` fields:

- `artifact_id` (unique key, e.g. `admittance.mode_vs_ljun`)
- `analysis_id` (source analysis, e.g. `admittance_extraction`)
- `category` (e.g. `resonance`, `fit`, `summary`, `qa`)
- `view_kind` (`matrix_table`, `series_plot`, `scalar_cards`, `record_table`, ...)
- `title` / `subtitle`
- `query_spec` (lazy query contract: paging/sorting/filtering/source)
- `meta` (units, axis labels, row/column counts, sweep flags)

!!! important "UI boundary"
    The Result View UI must consume artifacts only and must not parse `DerivedParameter.name` strings directly.

## Page Sections

1. `Source Scope`
2. `Run Analysis`
3. `Result View`

## Source Scope Contract

- user can switch between `All Dataset Records` and one specific `Result Bundle`
- scope summary must show at least: `Trace Records`, `Result Bundles`
- scope switch changes analysis source only; it must not rerun analysis

## Run Analysis Contract

`Run Analysis` uses a centralized execution model:

- one analysis selector
- analysis-specific configuration controls
- one `Run Selected Analysis` button
- execution log/status in the same panel

## Trace Selection Contract

Before each run, users must be able to choose which traces will be analyzed.

### Minimum Requirements

- use `ui.table` with row-click selection
- support pagination
- support sorting
- support filtering

### Trace Mode Semantics

- `Base`: fundamental/signal traces (no sideband tuple suffix in parameter name)
- `Sideband`: traces carrying non-zero mode tuple suffixes (for example `[...] [om=(...), im=(...)]`)
- default selection strategy must prioritize `Base`; full sideband preselection is not allowed

!!! note "Signal maps to Base"
    In Characterization trace filtering semantics, `Signal` is treated as `Base`.

### Interaction Performance Requirements

- row-click selection toggles must not trigger full page rerender
- Trace Selection must refresh locally (`table + counters + run state`) only
- only Scope/Analysis changes may trigger full compatibility recomputation
- compatibility metadata should be cached by scope key to avoid repeated full scans

!!! important "Sideband explosion control"
    Large multi-pump/sideband datasets must not default to full selection.
    The UI should provide a `Base traces` quick-select path to avoid producing meaningless mode over-expansion.

### Data Boundary

- trace table loads metadata only (`id`, `data_type`, `parameter`, `representation`)
- analysis run receives selected trace ids only
- compatibility evaluation must use metadata index only (payload must not be loaded)
- `data_type` aliases must be normalized consistently (`y_params` ↔ `y_parameters`, `s_params` ↔ `s_parameters`)

## Result View Contract

`Result View` should be a unified and extensible surface:

- first layer: `Category Selector`
- second layer: `Tabs` within the selected category
- shared render area driven by `view_kind`

### Trace Mode Filter (Result View)

- Result View must expose a `Trace Mode Filter`
- allowed options are strictly `All`, `Base`, `Sideband` (`Signal` semantics must map into `Base`)
- `Unknown` must not be exposed as an option or rendered label
- artifact manifest and payload query must consume the same mode filter
- switching mode filter must refresh current artifact payload only; it must not rerun analysis

!!! important "Classification contract (no Unknown)"
    Trace mode classification is a closed set:
    - `Base`: base/signal traces (including parameter names without sideband tuple suffixes)
    - `Sideband`: traces with non-zero mode tuple sideband suffixes
    - `All`: union of `Base + Sideband`
    Non-conforming upstream values must be normalized or ignored in data/application layers; they must not appear as `Unknown` in UI.

### Result View Controls Layout Contract

- Result View controls must include `Trace Mode Filter` and `Category Selector`
- on desktop (`lg` and above), both controls must stay in the same row
- on mobile, wrapping is allowed but still within one shared controls row block
- do not use arbitrary margin hacks; use existing spacing tokens (`gap-*`, `p-*`, `mb-*`)

!!! note "State consistency"
    `Available for current scope`, selectable traces, and analysis run enable/disable state must be driven by the same mode-filtered compatibility result; no split evaluators are allowed.

## Fitting Analyses UI Contract

### SQUID Fitting

- Run Analysis must expose actionable parameter inputs (at least model / bounds / fit window)
- execution flow: `Run Selected Analysis` must write status/log entries (start, success, failure)
- Result View must render `SQUID Fitting` outputs via artifact manifest under `fit` category

Input contract (minimum):
- `fit_model`: `NO_LS` / `WITH_LS` / `FIXED_C`
- `fit_min_ghz`, `fit_max_ghz`
- `ls_min_nh`, `ls_max_nh`, `c_min_pf`, `c_max_pf`
- `fixed_c_pf` (required only for `FIXED_C`)

Output contract (minimum):
- per-mode fitted parameters (for example `Ls_nH`, `C_eff_pF`) and quality metrics (for example `RMSE`)
- at least one inspectable artifact (`record_table` or `scalar_cards`)

### Y11 Response Fit

- Run Analysis must expose actionable parameter inputs (at least initial guesses and upper bound)
- execution flow must write status/log entries and surface failures
- Result View must render `Y11 Response Fit` outputs via artifact manifest under `fit` category

Input contract (minimum):
- `ls1_init_nh`, `ls2_init_nh`, `c_init_pf`
- `c_max_pf`

Output contract (minimum):
- fitted parameters (`Ls1_nH`, `Ls2_nH`, `C_pF`) and `RMSE`
- at least one inspectable artifact (recommended `scalar_cards`)

!!! tip "Result View hosting"
    Both `squid_fitting` and `y11_fit` belong to `fit` category.
    Artifacts are separated with tabs under the category; tab/filter switching refreshes payload only and must not rerun solver.

!!! note "Extensibility rule"
    When analyses grow from A..D to A..K, add or regroup views through registry/artifact mapping.
    Do not rewrite the core renderer flow.

!!! note "Overlap with /simulation"
    `/simulation` quick-inspect result view may remain.
    `/characterization` is the formal analysis + provenance workbench.

## Availability Contract

Analysis availability must be based on compatible traces in current scope.

!!! warning "compatible traces = 0"
    Availability must show `Unavailable for current scope`, and `Run Selected Analysis` must be disabled.
    Run execution must be guarded and rejected in this state.

!!! important "compatible traces > 0 and selected traces = 0"
    Availability may still show as available (or explicitly available with no selection),
    but the Run button must remain disabled until at least one trace is selected.
    The UI must show a clear hint: `Select at least one trace to run.`.

!!! tip "compatible traces > 0 and selected traces > 0"
    Availability should show `Available for current scope`, and the Run button may be enabled.

!!! note "No split-brain checks"
    Availability text, run-button enabled state, and pre-run guard must be driven by one shared compatibility evaluator.

## Performance SLO (Result View)

- first paint loads artifact manifest only (no full payload)
- category/tab switch loads only the selected artifact payload
- `ui.table` must use server-side pagination/sorting/filtering
- large sideband-heavy datasets must not be fully pushed to frontend in one shot

## Provenance Contract

Each completed run must create a new `ResultBundleRecord`:

- `bundle_type=characterization`
- `role=analysis_run`
- `config_snapshot` includes analysis config and selected trace ids

## Admittance Output Replacement Rule

Each `admittance_zero_crossing` run must delete prior outputs of the same method in the same dataset before writing new derived parameters, to prevent stale sideband/sweep rows from inflating mode tables.
