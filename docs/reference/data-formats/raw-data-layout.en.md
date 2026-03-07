---
aliases:
  - Raw Data Layout
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: raw-source layout and Design/Trace ingest boundaries
version: v1.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Raw Data Layout

`data/raw/` only stores external source files.  
It is not the direct working format for UI or Characterization; the trace-first workflow must consume ingested `TraceRecord`s.

## Source Categories

```text
data/raw/
├── measurement/
├── layout_simulation/
└── imported/
```

!!! note "Circuit simulation is not a raw-file source"
    `circuit_simulation` normally produces `TraceBatchRecord + TraceRecord + TraceStore payload` directly inside the application,
    rather than writing into `data/raw/` and ingesting again later.

## Project-first / Design-first layout

External sources should be grouped by design/project:

```text
data/raw/
└── <design_name>/
    ├── layout/
    │   ├── *.csv
    │   └── *.txt
    └── measurement/
        ├── *.csv
        └── *.s2p
```

## Ingest Boundary

An ingest/import should create:

1. `DesignRecord`
2. `DesignAssetRecord`
3. `TraceBatchRecord`
4. `TraceRecord`
5. `TraceStore` numeric payload

!!! important "Raw file is provenance, not the working trace authority"
    Raw files preserve source integrity.
    Plotting / Characterization / compare flows should not depend on reparsing raw files live inside the UI.

## Related

- [Design / Trace Schema](dataset-record.en.md)
- [Data Storage](../../explanation/architecture/data-storage.en.md)
