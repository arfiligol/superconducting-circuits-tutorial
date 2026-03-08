---
aliases:
  - Trace Platform Implementation Plan
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/implementation
status: draft
owner: docs-team
audience: team
scope: Design/Trace/TraceStore architecture phase-3 execution plan and multi-agent execution split
version: v0.3.0
last_updated: 2026-03-08
updated_by: codex
---

# Trace Platform Implementation Plan

This page is not a migration plan.  
It is the **active execution plan for the next phase**, so Integrators and Contributors can resume work cleanly after context compaction.

!!! important "Current active decisions"
    - `TraceStore` currently has only one active backend: local `Zarr`.
    - `s3_zarr` / MinIO / S3 is a deferred extension, not a blocker for the current phase.
    - when physical schema convergence begins, the project will cut directly to the new schema instead of building a historical-data migration path.

## Phase Status

### Phase 1 Completed

The following foundation work is already complete and integrated into `main`:

- SoT docs, guardrails, and architecture terminology now use `DesignRecord / TraceRecord / TraceBatchRecord / TraceStore`
- persistence contracts expose canonical naming while keeping legacy aliases
- the local `Zarr` TraceStore baseline is in place
- the circuit simulation write path can persist numeric payloads into the local TraceStore
- simulation result views can read from `TraceRecord + TraceStore` authority
- characterization consumers accept the new `TraceRecord`-like contract
- JosephsonCircuits.jl examples now cover the core write/read path regressions

This plan no longer lists those completed workstreams as active work.

### Phase 2 Completed

The following phase-2 workstreams are now complete and integrated into `main`:

- the main user-facing language in `Raw Data` and `Characterization` now converges on `Design / Trace / Trace Batch`
- layout ingest and measurement ingest now write through `TraceBatchRecord + TraceRecord + TraceStore`
- `TraceStoreRef` now exposes a local-first backend contract while keeping an extension-safe `s3_zarr` shape
- `AnalysisRunRecord` now exists as a logical persistence boundary
- the examples-driven validation matrix now has a formal phase-2 skeleton

### Phase 3 Active

The next phase is not a second schema rewrite. It is the push from “new architecture is usable” to:

- full cross-source product workflows
- cleaner legacy retirement
- deployable backend and storage boundaries
- stronger examples-driven acceptance baselines

## Goal

Make the system reach the following steady state:

- `DesignRecord` is the unified root container
- `TraceRecord` is the unified analysis unit for layout / circuit / measurement
- `TraceBatchRecord` is the shared provenance boundary for import / simulation / preprocess / postprocess
- `TraceStore` moves beyond contract-ready and reaches server/object-storage operational readiness
- `Characterization` remains source-agnostic and depends only on trace compatibility
- users can reliably compare layout / circuit / measurement traces inside the same `Design` scope

## Non-Goals

- no historical-data migration; physical schema convergence should use a direct cutover to the new schema
- no full UI hierarchy rewrite
- no point-per-record replacement of canonical ND `TraceRecord`
- no regression that pushes large numeric payloads back into the metadata DB for convenience

## Success Criteria

1. the `Design` scope supports stable cross-source browsing and compare workflows over layout / circuit / measurement traces
2. the remaining phase-2 compatibility layers now have explicit retirement or containment rules instead of open-ended dual paths
3. the `TraceStore` boundary is operationally ready for the local `Zarr` path, and future storage-extension work no longer blocks the current phase
4. examples-driven regression covers circuit / layout / measurement saved-trace reuse paths rather than only one source path
5. after phase-3 acceptance, the Integrator can clearly identify which legacy names and compatibility paths still exist and why

## Phase 3 Workstreams

### Workstream A: Cross-Source Product Workflow (Completed)

Goal:

- move from semantic convergence to a complete product workflow inside one `Design`
- let users understand and operate:
  - circuit traces
  - layout traces
  - measurement traces
  - characterization outputs

Focus:

- `Raw Data`
- `Characterization`
- trace selection and result navigation
- source compare / source summary / provenance visibility
- no large page-layout rewrite, but the cross-source compare experience must become complete

Completed now:

- `Raw Data` surfaces design-scoped source summary, compare readiness, and trace provenance
- `Simulation` / `Post Processing` clearly distinguish inspect-only surfaces from save-then-compare workflows
- `Characterization` now shows source coverage, provenance, and analysis-run history inside one design scope

Deferred expansion:

- if the product later needs richer per-source side-by-side compare UI, open a dedicated follow-up product workstream

### Workstream B: Legacy Cleanup and Persistence Convergence (Completed)

Goal:

- converge the compatibility layers intentionally kept during phase 2
- decide which dual-write / dual-read / legacy aliases can now be retired
- make persistence, query, characterization, and result-view flows rely on the same canonical path whenever possible

Focus:

- legacy aliases vs canonical names
- trace-store authority vs inline fallback
- dual-path save/read behavior
- no physical table rename yet, but less logical duplication

Completed now:

- `store_key` is the canonical locator
- `store_uri` is explicitly reduced to an opaque compatibility/debug locator
- simulation write/read paths and targeted regressions no longer treat `store_uri` as the primary local path source

Deferred expansion:

- physical schema rename / migration is still intentionally deferred outside the current phase-3 scope

### Workstream C: TraceStore Operational Boundary (Completed)

Goal:

- move the current backend abstraction from contract-ready to deployment-ready
- make the local-development path and any future storage-extension boundary explicit

Focus:

- stable `TraceStoreRef` contract
- no backend-specific path logic leaking into UI/app code
- equivalent semantics for local filesystem and object storage layouts
- live `s3_zarr` / MinIO / S3 integration is not required in this phase
- the local backend must be the only active, verifiable, deployable path in this phase

Completed now:

- the `local_zarr` runtime path and backend binding are converged
- the rule that UI/app code must not parse backend-specific local path layout is now part of the guardrails

### Workstream D: Platform Acceptance Matrix (Active)

Goal:

- evolve the phase-2 validation skeleton into a phase-3 acceptance baseline
- prove the platform reuse paths, not only the original circuit-only path

Focus:

- circuit simulation -> save/read -> characterize
- layout ingest -> save/read -> characterize
- measurement ingest -> save/read -> characterize
- cross-source compare inside one `Design`
- TraceStore local vs backend-boundary readiness

| Scenario | Current status | Minimum verification focus | Extension point |
|---|---|---|---|
| circuit simulation -> save/read -> characterize | implemented | saved traces can be re-read, re-characterized, and still preserve provenance | add more JosephsonCircuits example families and sweep variants |
| postprocess -> save/read -> characterize | implemented | post-processed traces can be saved, re-read, and reused in characterization / result navigation | expand to more pipeline steps and matrix families |
| layout ingest -> save/read -> characterize | implemented | layout traces persist through the trace-store path and can be consumed by characterization | add full browser/E2E coverage |
| measurement ingest -> save/read -> characterize | implemented | measurement traces persist through the trace-store path and can be consumed by characterization | add broader matrix-family coverage |
| cross-source compare within one design | implemented | multiple source traces can be browsed with source summary / provenance / compatibility gating inside the same design scope | add richer source-difference UX and compare assertions |
| TraceStore backend readiness | implemented | the local backend path is stable, verifiable, and supports the app/examples | if object-storage work resumes later, add MinIO/S3 smoke coverage |

Constraints:

- do not let the validation matrix regress back to “only prove circuit simulation runs”
- do not replace real cross-source reuse paths with fake fixtures
- prioritize proving that saved traces can be reused by characterization, rather than re-running only the phase-1 simulation success path

## Recommended Multi-Agent Split

Phase 3 should default back to the **3 fixed Contributor Agents** model, with the Integrator defining exact `Allowed Files` and bridge scope per round.

### 1. Platform Agent

Primary ownership:

- persistence contracts
- TraceStore backend
- ingest write paths
- lineage / query / metadata convergence
- cross-cutting architecture docs when needed

### 2. Simulation Agent

Primary ownership:

- simulation page
- post-processing page
- result views
- simulation-oriented UX/performance/lifecycle
- Josephson example E2E

### 3. Characterization Agent

Primary ownership:

- characterization page
- analysis services
- trace scope / trace compatibility
- characterization regressions
- cross-source compare behaviors when they center on analysis consumption

If a round contains a large docs-only, validation-only, or infra-only task, the Integrator may temporarily add a specialist contributor, but that should supplement rather than replace the 3 fixed contributors model.

## Integration Order

1. legacy cleanup / canonical path convergence
2. TraceStore operational boundary
3. cross-source product workflow
4. platform acceptance matrix expansion

## Required Regression Set

At minimum:

1. `uv run ruff check .`
2. targeted `pytest` for the touched architecture slices
3. JosephsonCircuits.jl app flows
4. layout / measurement saved-trace reuse regressions
5. characterization over saved traces regression
6. cross-source compare / scope regression whenever touched
7. TraceStore backend-boundary regression (local is mandatory)

## Acceptance Notes for Integrator

- do not reopen completed phase-1 or phase-2 work unless phase 3 explicitly expands that contract
- reject contributor diffs that introduce new legacy naming or new dual-path persistence patterns
- if ingest, UI, or characterization still primarily depend on inline metadata-DB payload instead of TraceStore authority, treat the work as architecturally incomplete
- if UI/app code directly touches backend-specific TraceStore paths, treat the backend boundary as incomplete
- if validation still proves only a single source path rather than the cross-source trace model, treat phase 3 as incomplete
