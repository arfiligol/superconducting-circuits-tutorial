---
aliases:
  - Query Indexing Strategy
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: "metadata DB query strategy and TraceStore slice-read performance strategy"
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Query Indexing Strategy

This page defines the performance responsibility split for the target architecture:

1. the **metadata DB** handles queries, indexes, relationships, and lineage
2. the **TraceStore** (`Zarr`) handles ND numeric payload and slice reads
3. large trace-value performance must no longer be pushed back into SQLite/PostgreSQL JSON/BLOB payloads

## Metadata DB Hot Paths

### Design / Trace paths

| Repo API | Usage | Main filter/sort |
|---|---|---|
| `count_by_design(design_id)` | design scope summary | `design_id` |
| `list_trace_index_page(design_id, query=...)` | Raw Data / Characterization / compare trace selection | `design_id`, `family`, `parameter`, `representation`, `source_kind`, `stage_kind` |
| `list_distinct_trace_index(...)` | trace compatibility / UI filter options | `design_id`, `family/parameter/representation` |

### TraceBatch paths

| Repo API | Usage | Main filter/sort |
|---|---|---|
| `list_batches_by_design(design_id)` | provenance timeline | `design_id`, `source_kind`, `stage_kind`, `created_at` |
| `get_batch_lineage(batch_id)` | postprocess / analysis lineage | `parent_batch_id` |
| `list_traces_by_batch(batch_id)` | batch-scoped trace lookup | `trace_batch_id` |

### Analysis paths

| Repo API | Usage | Main filter/sort |
|---|---|---|
| `list_analysis_runs_by_design(design_id)` | Characterization history | `design_id`, `analysis_id`, `created_at` |
| `list_derived_parameters_by_design(design_id)` | result tables / dashboards | `design_id`, `analysis_run_id`, `name` |

## Metadata Index Direction

Priority index candidates:

1. `trace_records(design_id, family, parameter, representation)`
2. `trace_batch_records(design_id, source_kind, stage_kind, created_at)`
3. `trace_batch_records(parent_batch_id)`
4. `trace_batch_trace_links(trace_batch_id, trace_record_id)`
5. `analysis_run_records(design_id, analysis_id, created_at)`

## TraceStore Read Strategy

!!! important "Do not full-read then slice"
    If UI / Characterization only needs an ND slice, read that slice directly from `Zarr`.
    Do not load the entire array with `[:]` and then slice it in Python memory.

### Common access pattern

Simulation / Post-Processing UI often needs to:

- fix sweep coordinates
- keep `X = frequency`
- compare multiple traces across selected sweep values

Recommended chunking direction:

- small chunks on sweep dims
- contiguous chunks on the frequency dim

For a trace shaped as:

```text
(sweep_a, sweep_b, frequency)
```

reasonable chunk choices include:

```text
(1, 1, 4001)
```

or

```text
(1, 1, 512)
```

### Why canonical ND still scales

A canonical ND `TraceRecord` does not mean every read must load the full ND array.
If chunking and axis order follow real access patterns, only the required chunks are read.

## S3 / MinIO Direction

The same strategy applies when the TraceStore backend becomes S3-compatible:

- metadata filtering happens in the DB first
- numeric payload uses chunked slice reads
- app/service code must not depend on local-path-only logic

## Validation Direction

When implementing this architecture, prioritize verification that:

1. official JosephsonCircuits.jl examples can write `DesignRecord + TraceBatchRecord + TraceRecord + Zarr`
2. UI compare / Characterization paths read only the required slices instead of full arrays
3. raw and post-processed sweeps align under the same trace-first query model

## Related

- [Design / Trace Schema](dataset-record.en.md)
- [Data Storage](../../explanation/architecture/data-storage.en.md)
