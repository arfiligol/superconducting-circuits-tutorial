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
scope: Design/Trace/TraceStore architecture phase-4 execution plan and multi-agent execution split
version: v0.4.0
last_updated: 2026-03-09
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

### Phase 3 Completed

The following phase-3 workstreams are now complete and integrated into `main`:

- the first complete cross-source product workflow layer
- local-only TraceStore operational boundary
- major legacy cleanup needed to unblock phase 4
- slice-first cache/read paths and incremental sweep persistence baseline

### Phase 4 Active

The next phase is not another terminology rewrite. It is the shift to persisted orchestration:

- `Simulation` no longer depends on live session result state
- `Post Processing` no longer depends on page-local latest raw result
- UI and CLI both create persisted execution boundaries
- backend workers execute only from persisted metadata DB + TraceStore state
- cache hit remains an optimization and never defines workflow authority

## Goal

Make the system reach the following steady state:

- `DesignRecord` is the unified root container
- `TraceRecord` is the unified analysis unit for layout / circuit / measurement
- `TraceBatchRecord` is the shared provenance boundary for import / simulation / preprocess / postprocess
- `TraceStore` moves beyond contract-ready and reaches server/object-storage operational readiness
- `Characterization` remains source-agnostic and depends only on trace compatibility
- users can reliably compare layout / circuit / measurement traces inside the same `Design` scope
- `Simulation` / `Post Processing` / `Characterization` can all be launched from UI or CLI through the same persisted execution contract

## Non-Goals

- no historical-data migration; physical schema convergence should use a direct cutover to the new schema
- no full UI hierarchy rewrite
- no point-per-record replacement of canonical ND `TraceRecord`
- no regression that pushes large numeric payloads back into the metadata DB for convenience
- no move that places numeric authority back into the metadata DB instead of TraceStore

## Success Criteria

1. `Simulation` / `Post Processing` / `Characterization` can all be launched from persisted run boundaries instead of page-local live state
2. saved raw simulation batches can re-enter post-processing without any live simulation session
3. cache hit only shortens execution and never changes workflow capability
4. UI and CLI share the same persisted execution semantics
5. examples-driven regression covers circuit / layout / measurement saved-trace reuse paths rather than only one source path

## Phase 4 Workstreams

### Workstream A: Persisted Orchestration for Trace-Producing Flows (Active)

Goal:

- move `Simulation` / `Post Processing` away from page-local live-session orchestration
- let UI and CLI both create persisted execution boundaries, then let backend workers execute

Focus:

- `TraceBatchRecord(status=running/completed/failed)` as the execution boundary for trace-producing flows
- `setup_payload` / `provenance_payload` explicitly represent input batches, source refs, and progress
- saved raw batches can re-enter post-processing directly
- cache hit never becomes the only authority path

Minimum completion standard:

- `Run Simulation` creates a persisted raw batch and writes sweep points incrementally into TraceStore
- `Run Post Processing` selects a persisted raw input batch instead of `latest_simulation_result`
- after UI disconnect/reconnect, persisted run state remains queryable and authoritative

Immediate TODO for this workstream:

- when the design selection changes, `/simulation` should resolve persisted raw and persisted postprocess batches first
- `Simulation Results` and `Post Processing Results` should prefer persisted batch authority over page-local runtime state
- rerunning post-processing from saved raw or saved postprocessed designs must no longer depend on page-local `latest_*`
- live session state may remain as a short-lived preview bridge, but it must not remain the only workflow authority

### Workstream B: Persisted Orchestration for Analysis Flows (Planned)

Goal:

- align `Characterization` with fully sessionless persisted execution semantics

Focus:

- keep `AnalysisRunRecord` and `TraceBatchRecord` responsibilities clear
- let UI and CLI share the same persisted analysis-run semantics
- avoid page-local state as the source of truth for run history / rerun / result navigation

### Workstream C: Platform Acceptance Matrix (Active)

Goal:

- turn the current validation baseline into a phase-4 acceptance matrix
- prove saved-batch reuse and persisted execution semantics, not only the old live-session path

Focus:

- circuit simulation -> save/read -> characterize
- saved raw batch -> post-process rerun
- layout ingest -> save/read -> characterize
- measurement ingest -> save/read -> characterize
- cross-source compare inside one `Design`
- persisted execution state after reconnect / cache hit

| Scenario | Current status | Minimum verification focus | Extension point |
|---|---|---|---|
| circuit simulation -> save/read -> characterize | implemented | saved traces can be re-read, re-characterized, and still preserve provenance | add more JosephsonCircuits example families and sweep variants |
| saved raw batch -> post-process rerun | active | post-processing can run from persisted raw batches without any live session result | extend to CLI/shared command coverage |
| postprocess -> save/read -> characterize | implemented | post-processed traces can be saved, re-read, and reused in characterization / result navigation | expand to more pipeline steps and matrix families |
| layout ingest -> save/read -> characterize | implemented | layout traces persist through the trace-store path and can be consumed by characterization | add full browser/E2E coverage |
| measurement ingest -> save/read -> characterize | implemented | measurement traces persist through the trace-store path and can be consumed by characterization | add broader matrix-family coverage |
| cross-source compare within one design | implemented | multiple source traces can be browsed with source summary / provenance / compatibility gating inside the same design scope | add richer source-difference UX and compare assertions |
| persisted execution after reconnect/cache hit | active | cache hit and reconnect preserve capability, not just status messaging | extend to longer-running sweep cases |

Constraints:

- do not let the validation matrix regress back to “only prove circuit simulation runs”
- do not replace real cross-source reuse paths with fake fixtures
- prioritize proving that saved raw batches can be reused by post-processing and that saved traces can be reused by characterization

## Recommended Multi-Agent Split

Phase 4 should default back to the **3 fixed Contributor Agents** model, with the Integrator defining exact `Allowed Files` and bridge scope per round.

### 1. Platform Agent

Primary ownership:

- persistence contracts
- TraceStore backend
- ingest write paths
- lineage / query / metadata convergence
- persisted execution boundaries
- cross-cutting architecture docs when needed

### 2. Simulation Agent

Primary ownership:

- simulation page
- post-processing page
- result views
- simulation-oriented UX/performance/lifecycle
- Josephson example E2E
- persisted orchestration UI/CLI bridge

### 3. Characterization Agent

Primary ownership:

- characterization page
- analysis services
- trace scope / trace compatibility
- characterization regressions
- cross-source compare behaviors when they center on analysis consumption
- persisted analysis-run semantics

If a round contains a large docs-only, validation-only, or infra-only task, the Integrator may temporarily add a specialist contributor, but that should supplement rather than replace the 3 fixed contributors model.

## Integration Order

1. persisted trace-producing orchestration
2. persisted analysis orchestration
3. platform acceptance matrix expansion

## Required Regression Set

At minimum:

1. `uv run ruff check .`
2. targeted `pytest` for the touched architecture slices
3. JosephsonCircuits.jl app flows
4. saved raw batch -> post-process rerun regression
5. layout / measurement saved-trace reuse regressions
6. characterization over saved traces regression
7. cross-source compare / scope regression whenever touched
8. TraceStore backend-boundary regression (local is mandatory)

## Acceptance Notes for Integrator

- do not reopen completed phase-1 / phase-2 / phase-3 work unless phase 4 explicitly expands that contract
- reject contributor diffs that introduce new legacy naming or new dual-path persistence patterns
- if ingest, UI, or characterization still primarily depend on inline metadata-DB payload instead of TraceStore authority, treat the work as architecturally incomplete
- if UI/app code directly touches backend-specific TraceStore paths, treat the backend boundary as incomplete
- if `Simulation` / `Post Processing` still depend on page-local latest-result state instead of persisted input batches, treat phase 4 as incomplete
