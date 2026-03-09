---
aliases:
  - Data Storage Architecture
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/data
status: stable
owner: docs-team
audience: team
scope: Design/Trace/TraceStore mental model and storage responsibility split
version: v1.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Data Storage

This page explains:

- why the system needs `DesignRecord`
- why traces must be the shared analysis unit
- why the metadata DB and numeric TraceStore must be separated

## Core Mental Model

The project follows a **Design-centric + Trace-first + external TraceStore** architecture:

- `DesignRecord` is the root container
- `TraceRecord` is the trace authority
- `TraceBatchRecord` is the setup / provenance / lineage boundary
- `AnalysisRunRecord` is the characterization execution boundary
- `DerivedParameterRecord` stores extracted physics outputs
- `TraceStore` (`Zarr`) stores ND numeric payload

```mermaid
flowchart TB
    Design["DesignRecord"]
    Asset["DesignAssetRecord"]
    Batch["TraceBatchRecord"]
    Trace["TraceRecord"]
    Store["TraceStore (Zarr)"]
    Analysis["AnalysisRunRecord"]
    Derived["DerivedParameterRecord"]

    Design --> Asset
    Design --> Batch
    Design --> Trace
    Design --> Analysis
    Design --> Derived
    Batch --> Trace
    Trace --> Store
    Analysis --> Trace
    Analysis --> Derived
```

## Why Design-centric

The product wants to answer questions such as:

- what is the difference between layout and circuit results?
- what is the difference between measurement and simulation?
- for one design, which traces from which source can be characterized together?

So the top-level container should be:

- one design scope
- containing multiple source families of traces

## Why Trace-first

The shared Characterization input is not:

- a circuit-only model
- a layout-only model
- a measurement-only model

It is:

- **compatible S/Y/Z matrix traces**

That is why UI, plotting, compare, and analysis should all use `TraceRecord` as the standard unit.

## Why TraceBatchRecord exists

If you only store `TraceRecord`, you still do not know:

- whether the trace came from layout import or circuit simulation
- what sweep/setup was used
- what post-processing steps were applied
- which upstream raw batch it came from

That is the job of `TraceBatchRecord`:

- generalized setup
- source kind
- stage kind
- lineage
- status

## Why AnalysisRunRecord must stay separate from TraceBatchRecord

`TraceBatchRecord` answers:

- where the traces came from, under which setup, and across which lineage boundary

`AnalysisRunRecord` answers:

- which Characterization analysis was executed
- which input traces / input batches were used
- which run configuration was used
- what status and summary the run produced

The minimal phase-2 landing is:

- logical contract = `AnalysisRunRecord`
- physical persistence = metadata DB rows backed by `TraceBatchRecord(bundle_type="characterization", role="analysis_run")`
- repository boundary = `uow.result_bundles.analysis_runs`
- Characterization history / result navigation should read and write the analysis-run contract instead of falling back to generic batch labels

This preserves:

- `TraceBatchRecord` as the provenance boundary for trace-producing flows
- `AnalysisRunRecord` as the characterization execution boundary
- the no-migration constraint for the current phase

It does not mean:

- numeric trace payload can move back into the metadata DB
- point-per-record becomes the canonical `TraceRecord`
- Characterization history/provenance can collapse back into generic batch semantics

## Why metadata DB and TraceStore must split

If large numeric payload stays inside SQLite/PostgreSQL JSON/BLOB:

- sweep payload grows the DB too quickly
- slice reads are poor
- object-storage extension becomes awkward
- UI/analysis tends to become full-read then slice

After the split:

- the metadata DB handles queries, indexes, lineage, and setup
- the TraceStore handles chunked ND arrays

## Why canonical TraceRecord should stay ND

The natural meaning of a trace is:

- one observable over axes

Examples:

- `Imag(Y_dm_dm)` over `frequency`
- `Imag(Y_dm_dm)` over `(frequency, L_jun)`

Splitting every sweep point into its own canonical record may feel intuitive, but it causes:

- metadata explosion
- fragmented provenance
- regrouping overhead before Characterization can work

Recommended split:

- canonical = ND `TraceRecord`
- point/slice materialization = projection/cache/export

## Local first, extension later

This model scales naturally, but the only active path right now is local `Zarr`:

1. current
   - metadata: `SQLite`
   - numeric: local `Zarr`
2. future server
   - metadata: `PostgreSQL`
   - numeric: local or shared `Zarr`
3. storage extension (deferred)
   - metadata: `PostgreSQL`
   - numeric: `S3-compatible Zarr` (MinIO / S3)

!!! important "Current phase is local-only"
    `s3_zarr` / MinIO / S3 is not the active implementation target right now.
    The current phase only requires the local `Zarr` path to be stable, testable, and able to support the examples and app flows.

## No DB migration in the current program

There is no historical-data migration plan for the current program.

Why:

- the current data volume is still small
- there is no production data set that must be preserved yet
- instead of carrying a legacy-to-new migration path, the project should cut directly to the new schema when physical schema convergence begins

This means:

- the current phase may keep necessary logical compatibility layers while the refactor lands
- but once physical schema convergence begins, the preferred path is a **direct cutover to the new schema**
- migration cost must not be treated as a reason to delay schema convergence

## What this means for current features

### Simulation
- creates `TraceBatchRecord(source_kind=circuit_simulation, stage_kind=raw)`
- materializes `TraceRecord`
- writes numeric payload into the TraceStore

### Post-Processing
- derives a new `TraceBatchRecord` from an upstream simulation batch
- creates new post-processed traces
- does not overwrite raw traces

### Characterization
- does not branch by source kind
- only checks trace compatibility and selected traces
- produces `AnalysisRunRecord + DerivedParameterRecord`
- `AnalysisRunRecord` may persist run config, input trace ids, input batch ids, status, and summary
- numeric trace payload still belongs in the TraceStore; Characterization history must not regress into batch-only semantics

## Persisted orchestration strategy

UI must not treat live session state as run authority.

The correct long-term model is:

- UI / CLI only create persisted run boundaries
- backend workers execute against the metadata DB + TraceStore
- execution progress / status / outputs are written back to persisted records
- read paths depend only on persisted state, not on `latest_*` runtime variables

### Trace-producing flows

For `simulation` / `post-processing` / `layout ingest` / `measurement ingest`:

- execution boundary = `TraceBatchRecord`
- `status=running/completed/failed`
- `setup_payload` = execution request contract
- `provenance_payload` = source batch ids / source trace ids / source asset ids
- numeric output = TraceStore slices / chunks

So:

- `TraceBatchRecord` does not only answer “what traces came out”
- it also answers “what trace-producing run is currently in progress”

For UI surfaces such as `/simulation` and `/post-processing`, this also means:

- active design selection should resolve persisted input/output batches first
- result views should prefer persisted batches + TraceStore as the authority
- live-session `latest_*` state may exist, but only as a short-lived preview / just-finished bridge
- persisted workflows must not lose authority because the UI refreshed, reconnected, or navigated away

### Analysis flows

For `Characterization`:

- execution boundary = `AnalysisRunRecord`
- input authority = selected trace ids / input batch ids
- output authority = `DerivedParameterRecord` + analysis artifacts

### Why this matters

If `Simulation` / `Post-Processing` still depend on live session state:

- UI refresh / reconnect / stale client lifecycle interferes with workflow continuity
- CLI and UI drift into different execution contracts
- saved raw batches cannot naturally re-enter post-processing
- cache hit / cache miss becomes a page-local state issue instead of a persisted execution-state issue

Persisted orchestration makes this explicit:

- UI is only one interaction surface
- CLI is another interaction surface
- backend execution always depends on persisted records

### Current vs target

- `Current`
  - trace numeric payload already lives in TraceStore
  - result views are mostly slice-first
  - but `/simulation` run / post-processing still retain some live-session orchestration
- `Target`
  - `Run Simulation` creates or updates a persisted raw `TraceBatchRecord`
  - `Run Post Processing` selects a persisted raw input batch directly
  - cache hit only shortens execution and never becomes the sole authority for post-processing / Characterization
  - UI and CLI no longer require “the latest live result in this page”

## Related

- [Design / Trace Schema](../../reference/data-formats/dataset-record.en.md)
- [Query Indexing Strategy](../../reference/data-formats/query-indexing-strategy.en.md)
