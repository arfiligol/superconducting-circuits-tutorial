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
scope: Design/Trace/TraceStore architecture implementation plan and multi-agent execution split
version: v0.1.0
last_updated: 2026-03-08
updated_by: codex
---

# Trace Platform Implementation Plan

This page is not a migration plan.  
It is the **execution plan** for the architecture reset, so Integrators and Contributors can resume work cleanly after context compaction.

## Goal

Move the implementation away from `Dataset/DataRecord/ResultBundle + SQLite large payload` and toward:

- `DesignRecord`
- `TraceRecord`
- `TraceBatchRecord`
- `AnalysisRunRecord`
- `TraceStore` (`Zarr`)

while keeping these workflows working end-to-end:

- Simulation
- Post-Processing
- Characterization
- official JosephsonCircuits.jl examples

## Non-Goals

- no historical-data migration
- no long-term dual-write compatibility
- no PostgreSQL deployment work yet
- no full layout/measurement ingest rewrite first

## Success Criteria

1. official JosephsonCircuits.jl examples can write the new metadata schema and Zarr TraceStore
2. Simulation Result View can read raw sweep results from `TraceRecord + TraceStore`
3. Post-Processing can write a new `TraceBatchRecord(stage=postprocess)` and post-processed traces
4. Characterization can consume the new `TraceRecord` path, at least for current circuit-simulation-derived examples
5. tests no longer treat the old `DataRecord/ResultBundle` naming model as the only SoT for new functionality

## Workstreams

### Workstream A: Metadata Schema Rename + Contracts

Goal:

- `DatasetRecord -> DesignRecord`
- `DataRecord -> TraceRecord`
- `ResultBundleRecord -> TraceBatchRecord`
- explicitly introduce `AnalysisRunRecord`

Focus:

- repository/UoW/contracts alignment
- naming and responsibility cleanup

### Workstream B: TraceStore (Zarr) Abstraction

Goal:

- implement local `Zarr` as the baseline
- introduce `TraceStoreRef`
- prevent UI/service code from depending on backend-specific path logic

Focus:

- chunked ND trace writes
- slice-first reads
- local backend first
- keep contract ready for S3-compatible extension

### Workstream C: Circuit Simulation Write Path

Goal:

- raw simulation / sweep writes `TraceBatchRecord + TraceRecord + TraceStore`
- post-processed outputs follow the same architecture

Focus:

- preserve sweep metadata
- keep raw vs postprocess lineage explicit
- make examples pass

### Workstream D: Result Views

Goal:

- both `Simulation Results`
- and `Post Processing Results`

must read correctly from the new `TraceRecord + TraceStore` architecture.

Focus:

- no full-read then slice
- slice reads go through the TraceStore
- preserve current compare interaction

### Workstream E: Characterization

Goal:

- Characterization consumes the new `TraceRecord` path directly
- keep trace-first semantics
- verify against circuit-derived examples first

Focus:

- remove dependence on old storage-shape assumptions
- make the `2D Freq x L_jun` path work first

## Recommended Multi-Agent Split

### 1. Metadata Contract Agent

Allowed Files:

- persistence models
- repository contracts
- repository tests
- data-format docs

### 2. TraceStore Agent

Allowed Files:

- persistence database/store abstractions
- new TraceStore modules
- storage tests
- data-handling / tech-stack docs

### 3. Simulation Write Path Agent

Allowed Files:

- simulation page/service/application save path
- post-processing save path
- simulation tests / josephson E2E

### 4. Result View Agent

Allowed Files:

- simulation result-view code
- result-view tests / josephson E2E

### 5. Characterization Agent

Allowed Files:

- characterization page/services
- analysis-run integration
- characterization tests / E2E

## Integration Order

1. metadata contracts
2. TraceStore abstraction
3. simulation write path
4. result views
5. characterization

## Required Regression Set

At minimum:

1. `uv run ruff check .`
2. `uv run pytest`
3. app flows derived from official JosephsonCircuits.jl examples
4. at least one post-processing sweep save + characterization regression

## Acceptance Notes for Integrator

- check contract docs before checking code
- if contributors keep using old names for new features, treat convergence as incomplete
- if UI read paths still do full-read then slice, treat the TraceStore task as incomplete
- if examples cannot emit complete traces under the new schema, treat the write path as incomplete
