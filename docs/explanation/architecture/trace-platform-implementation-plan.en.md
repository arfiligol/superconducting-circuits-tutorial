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
scope: Design/Trace/TraceStore architecture phase-2 execution plan and multi-agent execution split
version: v0.2.0
last_updated: 2026-03-08
updated_by: codex
---

# Trace Platform Implementation Plan

This page is not a migration plan.  
It is the **active execution plan for the next phase**, so Integrators and Contributors can resume work cleanly after context compaction.

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

### Phase 2 Active

The next phase extends the new circuit-simulation architecture into the full platform model.

## Goal

Make the system reach the following steady state:

- `DesignRecord` is the unified root container
- `TraceRecord` is the unified analysis unit for layout / circuit / measurement
- `TraceBatchRecord` is the shared provenance boundary for import / simulation / preprocess / postprocess
- `TraceStore` stays local-first while exposing a backend abstraction that is ready for future `S3 / MinIO`
- `Characterization` remains source-agnostic and depends only on trace compatibility

## Non-Goals

- no historical-data migration
- no physical DB table rename / migration yet
- no live S3/MinIO integration yet
- no full UI hierarchy rewrite
- no point-per-record replacement of canonical ND `TraceRecord`

## Success Criteria

1. the main user-facing language in `Raw Data`, `Characterization`, and related flows converges on `Design / Trace / Trace Batch`
2. layout and measurement ingest can also emit `TraceBatchRecord + TraceRecord + TraceStore`
3. Characterization uses the same trace-first model for layout, circuit, and measurement sources
4. the TraceStore backend abstraction has an explicit contract for both local and `s3_zarr`
5. examples-driven regression extends beyond circuit simulation and includes ingest + characterize paths

## Active Workstreams

### Workstream A: Product Vocabulary and UI Semantics

Goal:

- converge user-facing language away from `Dataset/DataRecord/ResultBundle`
- move toward:
  - `Design`
  - `Trace`
  - `Trace Batch`

Focus:

- `Raw Data`
- `Characterization`
- trace selection and result navigation
- semantic cleanup only, without a large page-layout rewrite

### Workstream B: Layout and Measurement Ingest

Goal:

- layout simulation ingest
- measurement ingest

must both produce:

- `TraceBatchRecord`
- `TraceRecord`
- `TraceStore` payload

Focus:

- generalized import contracts
- trace-first materialization
- compatibility with the same characterization path used for circuit simulation

### Workstream C: TraceStore Backend Boundary

Goal:

- evolve the current local `Zarr` baseline into a formal backend abstraction
- make the contract explicitly support:
  - `local_zarr`
  - `s3_zarr`

Focus:

- stable `TraceStoreRef` contract
- no backend-specific path logic leaking into UI/app code
- equivalent semantics for local filesystem and object storage layouts

### Workstream D: Analysis Run Persistence Decision

Goal:

- decide whether `AnalysisRunRecord` remains contract-only
- or becomes a formal persistence object

Focus:

- characterization history
- run provenance
- result navigation
- responsibility split versus `TraceBatchRecord`

### Workstream E: Examples-Driven Validation Matrix

Goal:

- define the formal regression matrix for the next phase

It must cover at least:

- circuit simulation examples
- post-process save/read
- characterization over saved traces
- layout/measurement ingest paths once they land

## Recommended Multi-Agent Split

### 1. Design Semantics Agent

Allowed Files:

- raw-data / characterization UI
- trace scope / selection services
- related docs and tests

### 2. Layout Ingest Agent

Allowed Files:

- layout import / preprocess services
- persistence write path
- ingest tests

### 3. Measurement Ingest Agent

Allowed Files:

- measurement import / preprocess services
- persistence write path
- ingest tests

### 4. TraceStore Backend Agent

Allowed Files:

- TraceStore abstraction
- storage contracts
- backend tests
- data-handling / tech-stack docs if needed

### 5. Analysis Run Contract Agent

Allowed Files:

- characterization persistence contracts
- analysis-run repositories / docs / tests

### 6. Validation Matrix Agent

Allowed Files:

- examples-driven E2E / integration tests
- supporting fixtures only

## Integration Order

1. product vocabulary / UI semantics
2. TraceStore backend boundary
3. layout ingest
4. measurement ingest
5. analysis-run persistence decision
6. validation matrix expansion

## Required Regression Set

At minimum:

1. `uv run ruff check .`
2. targeted `pytest` for the touched architecture slices
3. JosephsonCircuits.jl app flows
4. trace write/read regressions for each newly added ingest path
5. characterization over saved traces regression

## Acceptance Notes for Integrator

- do not reopen completed phase-1 work unless the new phase explicitly expands its contract
- first reject contributor diffs that introduce new legacy naming into phase-2 work
- if an ingest path still stores large numeric payloads primarily in the metadata DB, treat it as architecturally incomplete
- if UI/app code directly touches backend-specific TraceStore paths, treat the backend boundary as incomplete
- if validation still proves only “circuit simulation works” and does not cover the cross-source trace model, treat phase-2 as incomplete
