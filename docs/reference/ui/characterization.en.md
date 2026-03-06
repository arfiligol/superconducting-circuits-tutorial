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
version: v0.10.0
last_updated: 2026-03-07
updated_by: codex
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

!!! note "Current behavior (2026-03-04)"
    Older UI builds exposed a `Result Bundle` selector and let users directly scope
    Characterization runs to one bundle.

!!! important "Contract (Dataset-centric)"
    Users should operate on `Dataset` only. The `Source Scope` surface must not expose
    "choose a characterization bundle then rerun" as a primary interaction.
    Run Analysis trace candidates default to dataset-level trace index, with trace-first compatibility.

!!! note "Internal provenance"
    The system may still persist bundle-level provenance (for example `input_bundle_id`)
    internally, but UI must not require users to understand or manipulate bundle internals.

## Dataset Profile Contract

`dataset_profile` is a Characterization summary/recommendation source:

- storage path: `DatasetRecord.source_meta.dataset_profile`
- versioned schema:
  - `schema_version`: currently `1.0`
  - `device_type`: `unspecified` / `single_junction` / `squid` / `traveling_wave` / `resonator` / `other`
  - `capabilities`: string list (canonical capability keys)
  - `source`: `inferred` / `template` / `manual_override`

!!! note "Current implementation (2026-03-04)"
    The UI still renders profile-derived recommendation labels and hints,
    and keeps `required_capabilities` / `excluded_capabilities` as hint signals.

!!! important "Contract (Trace-first authority)"
    Analysis executability must be decided by trace compatibility, and run input must include
    selected trace ids. `dataset_profile.capabilities` must not be the only hard-block condition.

!!! warning "Backward compatibility"
    Legacy datasets without `dataset_profile` must fall back to an `inferred` profile,
    derived from existing record metadata, so existing workflows do not suddenly become unavailable.

## Run Analysis Contract

`Run Analysis` uses a centralized execution model:

- one analysis selector
- analysis-specific configuration controls
- one `Run Selected Analysis` button
- execution log/status in the same panel

!!! note "Current behavior (2026-03-04)"
    Availability information may be duplicated across multiple surfaces
    (headline text + status row + summary table).

!!! important "Contract (Single availability render)"
    Availability must have one primary UI surface (for example chip/label + reason line),
    driven by a single `availability state`: `state` + `reason` + `severity`.
    Debug reasons may remain available, but duplicate rendering of the same information is not allowed.

## Analysis Gating Contract (by capabilities)

Analysis registry must support:

- `required_capabilities`
- `excluded_capabilities`
- `recommended_for` (device_type list)

Run Analysis UI must expose one of the following trace-first states per analysis:

- `Recommended`: compatible traces exist, and profile/recommended-for hints match
- `Available`: compatible traces exist, without recommendation or with profile warnings
- `Unavailable`: compatible traces = 0 (the only hard block)

Reasons must be machine-composable and include at least:

- `No compatible traces in current scope`
- `Select at least one trace to run.`

Optional profile hints (non-blocking):

- `Profile hint: missing capability <capability_key>`
- `Profile hint: excluded capability <capability_key>`

!!! note "Single-page dynamic behavior"
    Characterization stays on one page; analysis status, reasons, and run interactions must be rendered dynamically in that single surface.

!!! warning "De-dup requirement"
    If an analysis summary table is kept for diagnostics, it must not duplicate the same
    availability information shown by the primary status render.

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

## Parameter Sweep Support Boundary (Current vs Target)

!!! note "Current behavior (2026-03-07)"
    `/characterization` is still trace-first and dataset-centric.
    It operates on selectable `DataRecord` traces, not on raw/post-processed sweep bundles as the primary input object.

Current support boundary:

- `Supported`:
  documented analyses such as `admittance_zero_crossing`, `squid_fitting`, and `y11_fit`
  may run when sweep-origin data has already been materialized into compatible selectable `DataRecord` traces.
- `Partial support`:
  those analyses may run on sweep-origin traces, but there is no formal sweep-native UI contract yet for
  axis-slice selectors, N-D sweep summary artifacts, or direct cross-point browsing from canonical bundle payloads.
- `Blocked`:
  using `ResultBundleRecord(bundle_type=circuit_simulation|simulation_postprocess, run_kind=parameter_sweep)`
  as the primary `/characterization` input object, or requiring analyses to traverse canonical sweep payloads
  without trace selection, is not contracted today.

!!! important "Target contract"
    Any future sweep support in Characterization must still preserve:
    - trace-first authority as the run gate
    - `dataset_profile` as hint only, never as hard gate
    - raw/post-processed sweep bundles as provenance and reconstruction sources, not replacements for selected trace ids

!!! warning "Representative point is not analysis authority"
    If a sweep dataset exposes only a representative-point projection and no selected traces or sweep-aware contract,
    `/characterization` must not claim full sweep-analysis support.

## Result View Contract

`Result View` should be a unified and extensible surface:

- first layer: `Category Selector`
- second layer: `Tabs` within the selected category
- shared render area driven by `view_kind`

### Run Success Navigation Contract

After `Run Selected Analysis` completes successfully, Result View must immediately sync to the analysis that just ran:

- automatically switch to the completed `analysis_id`
- if that analysis has artifacts, select the first available artifact directly
- if that analysis has no artifacts, stay on that analysis and show a diagnosable empty state

!!! important "Do not stay on stale analysis"
    A successful run must not keep the previous Result View analysis/category/artifact selection,
    because that makes users think the new analysis produced no results.

!!! note "SQUID Fitting display requirement"
    After `SQUID Fitting` completes, Result View should land in the `fit` category
    and show the `Fit Parameters` tab when data exists.
    The UI must not remain on an older `Admittance Extraction / Mode vs L_jun` view.

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
- `fit_min_nh`, `fit_max_nh`
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

### Run -> Persistence -> Artifact Mapping (SQUID / Y11)

The following is the formal visibility contract for Result View:

- `squid_fitting`:
  - run entry: `CharacterizationFittingService.run_squid_fitting()`
  - persisted method: `lc_squid_fit`
  - minimum derived params: `Ls_nH`, `C_eff_pF` (`extra` includes `mode`, `rmse`, `trace_mode_group`)
  - Result View: `fit` category, with at least one `fit_parameters` artifact
- `y11_fit`:
  - run entry: `CharacterizationFittingService.run_y11_fitting()`
  - persisted method: `y11_fit`
  - minimum derived params: `Ls1_nH`, `Ls2_nH`, `C_pF`, `RMSE` (`extra.trace_mode_group` required)
  - Result View: `fit` category, with at least one `fit_parameters` artifact

!!! important "Method alignment rule"
    `analysis_registry.completed_methods` and persistence `DerivedParameter.method` must match exactly (for example `squid_fitting -> lc_squid_fit`).
    Any mismatch makes Result View tabs/artifacts invisible for that analysis.

### Empty Artifact Fallback Contract

When persisted data exists but artifact manifest is empty, UI must surface a diagnosable message:

- if persisted method groups exist for current analysis/trace mode but artifact builder returns empty:
  - show a warning-level message like `Persisted results found but no renderable artifacts...`
  - include method keys in the message for debugging
- if emptiness is caused by trace-mode filtering:
  - show a mode-scoped empty-state message (must not trigger rerun)

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

When selected traces come from a sweep dataset, `config_snapshot` should also preserve enough information to reconstruct the chosen sweep slice
(for example selected trace ids, selected trace mode group, and the sweep-axis metadata carried by those traces).

## Admittance Output Replacement Rule

Each `admittance_zero_crossing` run must delete prior outputs of the same method in the same dataset before writing new derived parameters, to prevent stale sideband/sweep rows from inflating mode tables.

## Runtime Contract Snapshot

### Input

- active `DatasetRecord` (dataset-centric)
- trace metadata index (scope-filtered)
- analysis config + selected trace ids

### Output

- new `ResultBundleRecord(bundle_type=characterization, role=analysis_run)`
- corresponding `DerivedParameter` / artifact payload (by analysis type)
- traceable status log (start / heartbeat / success / failure)

### Invariants

1. trace-first authority: `compatible traces + selected trace ids` is the only run gate
2. `dataset_profile` is recommendation only and must never hard-block execution
3. Result View renders from artifact contracts, not from derived-parameter naming strings

### Failure Modes

- `compatible traces = 0` -> `Unavailable for current scope`
- `selected trace ids = 0` -> Run disabled + `Select at least one trace to run.`
- persistence method key and registry `completed_methods` mismatch -> result tab/artifact invisible

## Code Reference Map

- page orchestration:
  - [`characterization/__init__.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/characterization/__init__.py)
- runtime state:
  - [`characterization/state.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/characterization/state.py)
- trace-scope query service:
  - [`characterization_trace_scope.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/services/characterization_trace_scope.py)
- analysis metadata/hints:
  - [`analysis_registry.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/services/analysis_registry.py)
  - [`analysis_capability_evaluator.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/services/analysis_capability_evaluator.py)

## Runtime Parity Checklist

Before release, verify:

1. availability label, run-enable state, and pre-run guard all use one shared evaluator
2. trace mode filter (`All/Base/Sideband`) semantics match between Run Analysis and Result View
3. `ResultBundleRecord.config_snapshot` includes selected trace ids and selected trace mode group
4. artifact manifest and payload queries are both driven by the same trace-scope filter result
