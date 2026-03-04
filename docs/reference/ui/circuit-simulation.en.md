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
version: v0.5.0
last_updated: 2026-03-04
updated_by: docs-team
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

## Post Processing Results Node Semantics

`Post Processing Results` is a separate section that renders the latest successful post-processing output node:

- before Post Processing run: show waiting state
- after successful run: use the same Result Family Explorer interaction pattern as `Simulation Results` (family/metric/trace cards/shared plot)
- after pipeline-step parameter changes: invalidate previous output and require rerun
