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

## Local to Server to Object Storage

This model scales naturally:

1. current
   - metadata: `SQLite`
   - numeric: local `Zarr`
2. future server
   - metadata: `PostgreSQL`
   - numeric: local or shared `Zarr`
3. storage extension
   - metadata: `PostgreSQL`
   - numeric: `S3-compatible Zarr` (MinIO / S3)

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

## Related

- [Design / Trace Schema](../../reference/data-formats/dataset-record.en.md)
- [Query Indexing Strategy](../../reference/data-formats/query-indexing-strategy.en.md)
