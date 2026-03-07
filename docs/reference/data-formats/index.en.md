---
aliases:
  - Data Formats Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: Design/Trace/TraceBatch metadata schema, TraceStore contracts, and analysis-output data contracts
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Data Formats

This section is the new data-format SoT built around:

- `DesignRecord` as the design-scoped container
- `TraceRecord` as the analyzable trace unit
- `TraceBatchRecord` as the setup / provenance / lineage boundary
- `TraceStore` (`Zarr`) as the numeric ND payload store

!!! important "Design baseline (2026-03-08)"
    - Characterization always operates on compatible S/Y/Z matrix traces.
    - `layout_simulation`, `circuit_simulation`, and `measurement` differ by source, not by a different analysis model.
    - metadata DB and numeric TraceStore must remain separate.
    - canonical traces may be 1D / 2D / ND; a sweep point is not the only canonical record unit.

## Topics

| Topic | Description |
|---|---|
| [Design / Trace Schema](dataset-record.en.md) | `DesignRecord`, `TraceRecord`, `TraceBatchRecord`, `TraceStoreRef` |
| [Circuit Netlist](circuit-netlist.en.md) | Circuit Definition source / expanded contract |
| [Raw Data Layout](raw-data-layout.en.md) | raw-source and ingest/import boundaries |
| [Analysis Result](analysis-result.en.md) | `AnalysisRunRecord` / `DerivedParameter` related contracts |
| [Query Indexing Strategy](query-indexing-strategy.en.md) | metadata DB queries and TraceStore slice-read performance strategy |

## Quick Lookup

| Question | Read this first |
|---|---|
| Can one design contain circuit, layout, and measurement data at the same time? | [Design / Trace Schema](dataset-record.en.md) |
| Are sweep traces stored as ND traces or one record per point? | [Design / Trace Schema](dataset-record.en.md) |
| Where do large trace values live? | [Design / Trace Schema](dataset-record.en.md) + [Data Storage](../../explanation/architecture/data-storage.en.md) |
| How do local and S3/MinIO backends coexist? | [Design / Trace Schema](dataset-record.en.md) + [Data Storage](../../explanation/architecture/data-storage.en.md) |
| What role does Circuit Definition play in this architecture? | [Circuit Netlist](circuit-netlist.en.md) |
| Should performance work focus on the DB or the TraceStore? | [Query Indexing Strategy](query-indexing-strategy.en.md) |

## Current Implementation Direction (2026-03-08)

!!! note "Docs first"
    This section defines the target architecture direction.
    Implementation should now converge toward it rather than keep layering patches on top of the old `Dataset/DataRecord/ResultBundle` naming model.

## Related

- [Data Storage](../../explanation/architecture/data-storage.en.md)
- [Project Overview Guardrail](../guardrails/project-basics/project-overview.en.md)
- [Data Handling Guardrail](../guardrails/code-quality/data-handling.en.md)
