---
aliases:
- Circuit Simulation UI
- Circuit Simulation Interface
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /simulation contract for expanded netlist display, setup boundary, load-or-run execution, and result views
version: v0.14.0
last_updated: 2026-03-07
updated_by: codex
---

# Circuit Simulation

This page defines the formal `/simulation` UI contract.

## Page Sections

1. `Active Circuit`
2. `Netlist Configuration`
3. `Simulation Setup`
4. `Logs`
5. `Simulation Results`
6. `Post Processing`
7. `Post Processing Results`

## Result View Interaction Contract (Raw vs Post-Processed)

`Simulation Results` and `Post Processing Results` must remain separate sections, while sharing equivalent interaction capabilities.

| Section | Data source | Required shared interactions | Section-specific difference |
|---|---|---|---|
| `Simulation Results` | latest successful `Run Simulation` raw result bundle | `family tabs`, `metric selector`, `Add Trace`, trace cards, one shared plot | keeps raw-result semantics and `Save Raw Simulation Results` |
| `Post Processing Results` | latest successful `Run Post Processing` output node | `family tabs`, `metric selector`, `Add Trace`, trace cards, one shared plot | data comes from pipeline output; save action is `Save Post-Processed Results` |

!!! important "Keep sections separate"
    `Raw Simulation Results` and `Post Processing Results` must keep separate rendering and state.
    They must not be merged into a single result card.

!!! note "Result-view interactions must not rerun execution"
    Changes inside the result view (family/metric switches, adding or removing trace cards,
    trace selector edits) must only update the shared plot and must not rerun solver or post-processing.

### Result-view title and axis synchronization contract

After any `family` / `metric` / `trace` change, the chart must update in sync:

- `figure title`
- `y-axis title` (including unit)

!!! important "No stale labels"
    The chart must not keep y-axis/title text from the previously selected family/metric.
    At minimum, the `Y -> Z -> Y` switching loop must restore the correct y-axis label each time.

Minimum requirement for `Impedance (Z)` and `Admittance (Y)`:

- `Z + Real/Imaginary/Magnitude` -> `Real (Ohm)` / `Imaginary (Ohm)` / `Magnitude (Ohm)`
- `Y + Real/Imaginary/Magnitude` -> `Real (S)` / `Imaginary (S)` / `Magnitude (S)`

### Raw Simulation Results family semantics (normative)

- `S`: must always show solver-native raw `S`; Port Termination Compensation (PTC) must not be applied
- `Y`: must provide `Raw Y` / `PTC Y` source switching
- `Z`: must provide `Raw Z` / `PTC Z` source switching

!!! important "PTC scope in Raw View"
    In `Simulation Results`, PTC may affect only the `Y/Z` paths.
    `S` must remain raw to preserve solver-native semantics.

!!! note "Y-domain first"
    PTC is defined as `Y_clean = Y_raw - diag(1/R_i)`.
    `PTC Z` must be derived from compensated `Y`; direct `S` compensation is not allowed.

### Post-Processed naming consistency contract

!!! note "Current behavior (2026-03-04)"
    Some views may still fall back to index-only names (for example `Z11`) that do not match
    Trace Card `Output Port` / `Input Port` labels.

!!! important "Contract"
    In `Post-Processed Result View`, title / legend / trace labels (including hover-visible labels)
    must use names consistent with Trace Card selections:
    `<MatrixSymbol>_<OutputPortLabel>_<InputPortLabel>`.

!!! warning "No index-only fallback in transformed basis"
    In transformed-basis cases (for example `dm(1,2)`, `cm(1,2)`), do not render index-only names
    like `Z11`, `Y21`, `S12`.
    Index-only naming is acceptable only when output/input are purely numeric raw ports and no
    basis transformation is active.

## Netlist Configuration

!!! note "Live Preview"
    Schemdraw Live Preview remains disabled and must not be restored here.

`Netlist Configuration` must show the expanded form actually sent to the simulator:

- expanded `components`
- expanded `topology`
- expanded `parameters` (if present)

!!! important "Single expansion pipeline"
    `/simulation` `Netlist Configuration` and `/schemas/{id}` `Expanded Netlist Preview`
    must use the same parse/validate/expand pipeline.

### Display vs Persistence Boundary

- DB stores source-form `Circuit Definition` only
- this card displays read-only expanded form
- solver input must match this card exactly

## Simulation Setup

!!! important "Boundary"
    Source Port, Source Mode, pump frequency, harmonics, and hbsolve options are Simulation Setup,
    not Circuit Netlist syntax.

### Three-layer card structure contract

`Simulation Setup` must use three levels:

1. Level 1: root `Simulation Setup` container card
2. Level 2: fixed sections (order is normative)
   - `Signal Frequency Sweep Range`
   - `Parameter Sweeps`
   - `HB Solve Setting`
   - `Sources`
   - `Port Termination Compensation`
   - `Advanced hbsolve Options`
3. Level 3: add/remove child cards
   - `Parameter Sweeps`: add/remove axis cards
   - `Sources`: add/remove source cards

### Setup Persistence Contract (Dialog-based Manager)

`Simulation Setup` must keep the existing `Saved Setup` dropdown and add a `Manage Setups` entry (dialog).

The `Manage Setups` dialog must support at least:

1. `Add New` (create from current form state)
2. `Rename` (rename an existing setup)
3. `Delete` (remove an existing setup)
4. `Load` (load selected setup into the form)
5. `Save As` (store current form state under a new name)

!!! important "Visible feedback"
    Every CRUD action must show user-visible success/failure feedback.

!!! warning "Compatibility boundary"
    Existing `Saved Setup` dropdown load behavior must stay unchanged.
    `Manage Setups` is an additional entry point only and must not alter schema+setup execution semantics.

### Parameter Sweep (Multi-Axis MVP)

Sweep axis targets must cover at least:

- expanded netlist `components[*].value_ref` (deduplicated)
- bias/pump-related continuous source fields already configured in Simulation Setup
  (for example `sources[1].current_amp`, `sources[1].pump_freq_ghz`)

!!! note "Target key namespace"
    Sweep target keys can mix netlist and source namespaces.
    Recommended key format:
    - netlist: `<value_ref>` (for example `Lj`)
    - source: `sources[<1-based index>].<field>` (for example `sources[1].current_amp`)

- only components with `value_ref` are selectable as netlist sweep targets
- components with inline `default` only are not netlist sweep targets
- Supports multi-axis sweep
- Execution mode must support `cartesian` first (`paired` field may exist as reserved)
- when sweep is disabled, `Run Simulation` behavior must remain identical to single-run

Minimum sweep setup fields:

- `enabled: bool`
- `mode: "cartesian"` (default)
- `axes[]`
  - `target_value_ref: str` (target key; may be a value_ref or a source target)
  - `start / stop / points`
  - `unit` (from parameter-spec hints or source-field semantics)

!!! note "Legacy payload compatibility"
    Legacy single-axis setup payloads (for example `axis_1`) must still decode and normalize into `axes[]`.

### Sweep Cache / Provenance Contract

When sweep is enabled:

1. normalized simulation setup must include a `sweep` block
2. `sweep_setup_hash` must be computed from that normalized sweep block
3. result-cache identity remains `schema_source_hash + simulation_setup_hash`, and `simulation_setup_hash` must include the sweep block
4. `source_meta` and `config_snapshot` must persist `sweep_setup_hash` and sweep-axis summary
   (including target key)

### Sweep Logs Contract

`Logs` must additionally show:

- sweep dimensions (MVP = 1)
- total sweep points
- per-point progress (for example `point 3/11`)

### Sweep Result Structure Contract (for downstream pipeline/analysis)

After a successful sweep run, bundle `result_payload` must include:

- `run_kind = "parameter_sweep"`
- `sweep_axes` metadata (target, unit, values, point_count)
- `sweep_mode` (at least `cartesian` for now)
- `points[]` (each point includes at least `axis_indices`, `axis_values`, and point-level simulation result)
- `representative_point_index` (for Result View quick inspect)

When exporting to `DataRecord`, sweep-axis metadata must be explicit in `axes` so sweep traces remain distinguishable from single-run traces.

!!! important "Current vs Target (2026-03-07)"
    - `Current`: the canonical raw parameter-sweep authority is already the full `circuit_simulation` bundle `result_payload`.
    - `Target`: `representative_point_index` is quick-inspect projection only and must never replace the full sweep payload as SoT.

### Sweep Result View Contract (inside Simulation Results)

When the latest successful run is `run_kind=parameter_sweep`, `Simulation Results` must render an additional `Sweep Result View`:

- section header must show:
  - sweep dimension count
  - total point count
  - current view-axis and fixed-axis slice summary
- minimum `selectors`:
  - `View Axis` selector (x-axis)
  - `Fixed Axis` selectors for N-1 axes
  - `family`
  - `metric`
  - `Add Trace` and multiple trace cards
  - `Output Port` / `Input Port`
  - `Output Mode` / `Input Mode`
  - `Frequency`
- minimum `outputs`:
  - `Table`: per-point `axis value` + `point index` + per-trace metric columns for the active slice
  - `Plot`: `metric vs view axis` for the active slice, with multi-trace overlay

!!! important "Trace-first"
    Sweep selectors must follow the existing trace-first design.
    Do not hardcode one trace path (for example `S11` only).

!!! note "Save consistency"
    For sweep runs, `Save Raw Simulation Results` must persist full sweep payload and provenance
    (including `sweep_setup_hash` and `sweep_axes`) so the run is replayable.

### Sweep Result View Failure Modes (minimum)

- missing sweep payload: show empty state, no crash
- selector incompatible with current payload: auto-fallback to valid defaults and keep warning logs
- partial point data missing (trace or representation): render `NaN`/`N/A` for that point while keeping the view usable
- cartesian point count over threshold: show explicit warning and block `Run Simulation`
- invalid target after schema/setup change: fallback to a valid target or block run with a clear warning

### Flux-Pumped JPA Bias Sweep (reproducible flow)

Use this flow to reproduce official `Flux-pumped JPA` bias-sweep semantics (bias axis):

1. choose `Flux-pumped Josephson Parametric Amplifier (JPA)` (or equivalent schema)
2. enable `Enable Sweep` in `Simulation Setup`
3. set `Sweep Target` to a bias-correlated source parameter
   (recommended `sources[1].current_amp`; if represented as equivalent netlist parameter, `Lj` is acceptable)
4. add at least one sweep axis in `Parameter Sweeps` and set `Sweep Start / Stop / Points`
   (optionally add a second axis for slice analysis)
5. run `Run Simulation`
6. in `Simulation Results` -> `Sweep Result View`, pick `View Axis`, fix the remaining axes, then pick trace/metric/frequency selectors
7. verify `Table` and `Plot` stay synchronized as `metric vs view axis` for the active slice

### Port Termination Compensation (optional)

`Simulation Setup` must expose a `Port Termination Compensation` section that is separate from hbsolve options.

The mode set is fixed to:

1. `Auto (Schema infer)`
2. `Manual` (default `R=50 Ohm` per selected port)

Compensation rule (normative):

- execute in Y-domain before any Post Processing step
- apply on selected ports as: `Y_clean = Y_meas - diag(1/R_i)`
- selected ports must be multi-selectable
- when disabled, behavior must remain identical to current flow

!!! important "Port-Level only"
    Termination compensation applies to port-level matrices only; no nodal/internal-node flow is allowed.

!!! warning "Nodal out of scope"
    Internal-node elimination or nodal topology compensation is out of scope on this page.

#### Auto (Schema infer) contract

- infer each port shunt resistor from expanded netlist (`R*` from port signal node to ground)
- inferred values must be visible/debuggable in UI (value + source)
- if a port cannot be inferred reliably, UI must show fallback and warning explicitly

#### Manual contract

- `R_i` per selected port must be editable
- default for new/manual-selected ports must be `50 Ohm`
- UI must provide a quick reset-to-default action

#### Execution and cache contract

- this compensation is solver post-processing and must not trigger a Julia rerun
- compensation settings must not pollute hbsolve advanced options
- result-cache identity remains schema + solver setup; termination compensation setup is managed separately

!!! note "No Julia rerun"
    Changing termination compensation (`enabled/mode/ports/R`) must only update Python-side result flow and must not resubmit Julia `hbsolve`.

## `Run Simulation` Contract (Load-or-Run)

Formal `Run Simulation` semantics:

1. build snapshot/hash from source-form schema
2. build snapshot/hash from normalized simulation setup
3. lookup cache by exact schema+setup identity
4. run Julia solver only on cache miss

## Logs Contract

`Logs` must include at least:

- schema load
- setup normalization summary
- cache lookup (hit/miss)
- solver start
- long-running heartbeat/progress
- success/failure summary

!!! note "Long-running solves"
    For multi-pump or high-harmonic cases, logs must continue to show still-running progress messages.

## Save Results to Dataset

`Save Results to Dataset` is manual export, not result-cache identity.

Expected model:

1. choose target `DatasetRecord`
2. create visible `ResultBundleRecord`
3. attach exported `DataRecord` rows to that bundle

## Simulation -> Characterization Bridge Contract

!!! note "Current implementation (2026-03-04)"
    Both `Save Raw Simulation Results` and `Save Post-Processed Results` create a
    `ResultBundleRecord` and link generated traces through `ResultBundleDataLink`.

!!! important "Contract"
    When Characterization `Source Scope` selects one specific bundle, only that bundle's linked
    traces are valid analysis input. `All Dataset Records` may mix multiple sources, but
    trace-first compatibility remains the run authority.

!!! important "Provenance"
    Simulation-created bundles must keep enough provenance in `source_meta` + `config_snapshot`
    to reconstruct upstream input (at minimum: `origin`, source bundle when present, and flow/setup snapshot).

## Dataset Metadata Boundary

!!! important "Dashboard-only"
    `/simulation` must not render a `Dataset Metadata Summary` card.
    Dataset metadata visibility/edit entry stays in `Pipeline Dashboard` only.

!!! warning "Boundary vs run behavior"
    Dataset metadata must not alter solver setup submission on this page.
    No metadata write button or form may exist in `/simulation`.

## Post Processing

`Post Processing` is a simulation-after pipeline. It must:

- not rerun the solver
- operate only on completed simulation matrices
- support multi-step flow composition (step chain)

!!! important "M1 boundary"
    Version 1 supports `Port-level` post-processing only.
    `Nodal-level` elimination over internal nodes is out of scope for M1.

!!! important "Compensation ordering"
    When enabled, `Port Termination Compensation` must be applied before the Post Processing pipeline starts.

### Pipeline layout contract

`Post Processing` uses a "parent card + chained step cards" layout:

- parent card: `Post Processing`
- fixed child cards:
  - `Input Node`
  - `Output Node`
- dynamic step cards:
  - users add steps via `Add Step`
  - each step card selects one type (M1: `Coordinate Transformation` / `Kron Reduction`)
  - steps can be removed/reset; execution order follows card order

!!! important "Step chaining semantics"
    Keep-label options in each Kron step must come from the output basis of its upstream step chain.
    For example, after cm/dm transform, downstream Kron keep options must show `cm(...)` and `dm(...)`,
    not raw port numbers.

!!! note "Kron keep-basis interaction"
    `Keep Basis Labels` must support continuous multi-select without closing after each click.
    A chip-toggle or top-nav style selector is acceptable, and it must provide `Select All` / `Clear` quick actions.

### Post-Processing input source contract

`Input Node` must expose `Input Y Source` with:

- `Raw Y`
- `PTC Y`

!!! important "Source visibility"
    `Post Processing Results` must clearly indicate whether output comes from `Raw Y` or `PTC Y`.
    The persisted flow snapshot must also carry this source field.

### Scope and Input Matrix

- post-processing uses port-space `Y(ω)` as the canonical input
- if source data provides only `Z(ω)`, convert first via `Y(ω)=Z(ω)^{-1}`
- `Mode Filter` defaults to `Base`; `Sideband` is optional advanced scope

!!! note "Relation between Z and Y"
    `Z ↔ Y` is a matrix inverse relation, not a simple `jω` scaling.

### Step Types (M1)

1. `Coordinate Transformation`
2. `Kron Reduction`

### Coordinate Transformation Contract

Port-basis transforms must use:

`Y_m = A^{-T} · Y · A^{-1}`

with:

- `V_m = A · V`
- `I_m = A^{-T} · I`

!!! warning "No direct S-domain CT"
    Coordinate Transformation and Kron Reduction are allowed only in the `Y/Z` domain.
    Direct coordinate transformation on `S` is forbidden.

#### cm/dm template and normalization

M1 must provide a `common/differential` template with:

- `Auto (Electrical Centroid)` for `α, β`
- `Manual` override for `α, β`

!!! important "Weight mode and editability"
    - `Auto`: `alpha` / `beta` fields must be disabled (read-only in UI)
    - `Manual`: `alpha` / `beta` fields must be editable
    - In `Auto` mode, execution must use schema C-to-ground derived weights and must not consume stale manual input values

cm/dm definitions:

- `V_cm = αV1 + βV2`
- `V_dm = V1 - V2`
- constraint: `α + β = 1`

!!! important "Normalization semantics"
    This normalization refers to electrical-centroid weighting (`α+β=1`),
    not the quantum matrix-element correction factor.

#### Auto αβ (Electrical Centroid) extraction rule

M1 default uses capacitive weighting:

- `w1 = Σ C(node1 ↔ reference_set)`
- `w2 = Σ C(node2 ↔ reference_set)`
- `α = w1 / (w1 + w2)`
- `β = w2 / (w1 + w2)`

M1 currently uses `reference_set={0}` (ground-only).
Custom reference sets (for example `{0, drive_line}`) are deferred.

### Kron Reduction Contract

Kron reduction must use Schur complement:

`Y_red = Y_bb - Y_bi · Y_ii^{-1} · Y_ib`

The public API should be keep-set driven; drop-set may be inferred by complement.

!!! warning "Numerical stability"
    Implementation must use `solve`, not explicit `inv`.
    If `Y_ii` is ill-conditioned, emit warnings in UI logs.

## Post Processing and Persistence

Post-processing outputs may be saved as a new bundle.

After `Run Post Processing` succeeds, UI must expose a `Save Post-Processed Results` action, and:

- the button must live in the `Post Processing Results` section (aligned with `Simulation Results` save placement)
- the button must not appear inside the `Post Processing` input section
- save button must stay disabled before any successful post-processing run
- when pipeline changes invalidate the output node, save must return to disabled state
- save button must show loading state during persistence
- both `Create New` and `Append to Existing` dataset modes must be supported

### Post-Processing Setup (flow setup persistence)

The `Post Processing` input node must provide setup persistence (parallel to `Simulation Setup`):

- `Post-Processing Setup` selector (load existing setup)
- `Save Setup` action (named save/update)
- `Delete Setup` action (remove selected setup)

Saved payload must include at least:

- `Mode Filter`
- `Mode`
- `Z0`
- step chain (type / enabled / params / order)

!!! important "Apply and invalidation rule"
    Loading a setup or changing pipeline parameters invalidates previous post-processed output.
    `Post Processing Results` must require a new `Run Post Processing` before save is enabled again.

Recommended model:

- `bundle_type=simulation_postprocess`
- `role=derived_from_simulation`
- `source_meta` stores source simulation bundle id
- `config_snapshot` stores flow spec (mode filter, A, keep/drop, step order)
- bundle must attach output `DataRecord` rows (at least `y_params` with `real/imaginary`)

### Post Processing over Parameter Sweep (Current Contract)

!!! important "Current contract (2026-03-07)"
    If `simulation_postprocess` consumes a parameter sweep:
    1. the canonical SoT must be a full post-processed sweep bundle payload, not the representative point
    2. `representative_point_index` is quick-inspect projection only
    3. `Post Processing Results` may start from representative-point or slice views, but those views must not be treated as the full sweep authority
    4. raw simulation and post-processed sweep must stay as two separate provenance nodes

### Minimum Persistence Contract for Post-Processed Sweep (Current)

When `bundle_type=simulation_postprocess` is saved from a `run_kind=parameter_sweep` source bundle, persistence must include at least:

- `source_meta.source_simulation_bundle_id`
- `source_meta.source_run_kind = "parameter_sweep"`
- `config_snapshot.input_y_source`
- full post-processing flow spec in `config_snapshot`
- `config_snapshot.sweep_setup_hash` (matching the source sweep)
- `result_payload.sweep_axes`
- `result_payload.point_count`
- `result_payload.points[]` (each point includes at least `source_point_index`, `axis_indices`, `axis_values`, and the post-processed point result or a stable handle to reconstruct it)
- `result_payload.representative_point_index`

!!! warning "Do not collapse to one point"
    If only one representative-point output is saved and sweep axes / point metadata are dropped,
    the bundle must not claim to be the full post-processed sweep authority.

!!! important "Post-processed sweep save semantics"
    When the source is a sweep run, `Save Post-Processed Results` currently guarantees
    provenance, replayability, and explorer-readable projections.
    The action itself does not promise that every post-processed sweep point is written
    to durable storage as a fully materialized processed-value snapshot.

!!! note "Future full snapshot is additive"
    If a self-contained snapshot/export artifact is later required, it should be approved
    as an additive contract or subtype rather than documented as implicit behavior of the
    current save action.

### HFSS Comparable semantic marker

`Post Processing Results` must expose an `HFSS Comparable` state marker (badge/label).

Conditions (all required):

1. `Port Termination Compensation` is enabled
2. At least one enabled `Coordinate Transformation` exists in the pipeline
3. `Input Y Source = PTC Y`

!!! warning "Reason is required when not comparable"
    If `HFSS Comparable` is false, UI must show an explicit reason,
    for example "PTC is disabled", "Coordinate Transformation missing", or
    "Input Y Source is not PTC Y".

## Normalization Domains (Avoid Mixing Terms)

This page only implements the first of two normalization contexts:

1. `Coordinate Transformation` weighting normalization (in scope here)
   - `V_cm = αV1 + βV2`
   - constraint `α + β = 1`
   - physical intent: electrical-centroid weighting to reduce cm/dm cross-coupling
2. Quantum matrix-element normalization in decay formulas (out of scope here)
   - for example matrix-element correction around `Γ1 = Re{Y}/C_Q`
   - common notation: `β_q = <0|n|1> / n_QHO^{01}`
   - belongs to `/characterization` and physics explanation, not `/simulation`

!!! note "Same word, different semantics"
    Both are called normalization in practice, but they are not interchangeable.

## Mapping to the 4-step Nodal Pipeline

The research pipeline is:

1. Raw Nodal `Y`
2. Topological Kron (internal-node elimination)
3. Coordinate Transformation
4. Modal Kron

M1 on this page implements only the `Port-level` form of steps 3/4.
Full nodal internal-node elimination (steps 1/2 UI flow) is explicitly out of M1 scope.

## Boundary with Characterization

`/simulation` Post Processing handles matrix transforms and reductions only.

`Physics Extraction` (for example `C_eff`, `T1`) belongs to `/characterization`, not this page.

## Simulation Results Node Semantics

`Simulation Results` renders the raw quick-inspect view from the latest successful `Run Simulation`:

- it becomes available immediately after solver success (no Post Processing required)
- it keeps the multi-family `S/Y/Z/QE/CM/Complex` tabs, metric selector, add-trace cards, and shared plot

!!! important "Raw S must never be rewritten by PTC"
    Even when PTC is enabled, `Simulation Results` `S` must remain solver-native raw `S`.
    In Raw View, PTC may affect only `Y/Z` families through explicit source switching.

## Post Processing Results Node Semantics

`Post Processing Results` is a separate section that renders the latest successful post-processing output node:

- before Post Processing run: show waiting state
- after successful run: use the same Result Family Explorer interaction pattern as `Simulation Results` (family/metric/trace cards/shared plot)
- after pipeline-step parameter changes: invalidate previous output and require rerun

!!! note "Processed S source"
    `Post Processing Results` `S` must be converted from post-processed `Y/Z`,
    not produced by direct S-domain transformation.

## Runtime Contract Snapshot

### Input

- active schema source-form definition (DB persisted)
- normalized simulation setup
- optional post-processing flow spec (steps + input Y source)

### Output

- simulation raw result cache/bundle (with raw `S/Y/Z` families)
- optional post-processed output node (readable by result-family explorer)
- optional post-processed sweep bundle (when input is a raw sweep, full sweep payload must remain canonical)
- traceable logs (cache hit/miss, solver run, post-processing run)

### Invariants

1. `Simulation Results` and `Post Processing Results` keep separate state while sharing aligned interaction patterns
2. raw `S` always remains solver-native and must not be rewritten by PTC
3. PTC is allowed only in Y-domain first, then `Z` (and optionally post-processed `S`) is derived from that source
4. coordinate transform and kron reduction run only in `Y/Z` domains

### Failure Modes

- schema parse/validation failure -> run rejected with field-level error
- solver long-running/timeout -> heartbeat + warning must be visible in logs
- invalid post-processing step chain (unavailable basis labels) -> run rejected
- HFSS-comparable conditions not met -> must show `Not comparable` with explainable reason

## Code Reference Map

- page orchestration + sections:
  - [`simulation/__init__.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/simulation/__init__.py)
- simulation runtime state:
  - [`simulation/state.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/simulation/state.py)
- post-processing application:
  - [`post_processing.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/simulation/application/post_processing.py)

## Runtime Parity Checklist

Before release, verify:

1. Schema Editor Expanded Preview and Simulation Netlist Configuration use the same expansion pipeline
2. `Simulation Results` family-source contract stays consistent (`S=raw only`, `Y/Z=raw|PTC`)
3. `Post Processing Results` naming, title, and y-axis labels match trace-card output/input labels
4. save-raw and save-postprocessed both persist bundle provenance (`origin`, `source`, `config snapshot`)
