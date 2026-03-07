---
aliases:
  - "Data Handling Rules"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Data handling rules: raw-data immutability, metadata DB vs TraceStore split, Unit of Work, and Zarr backend boundaries"
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Data Handling

Data handling and storage rules.

## Directory Structure

```text
data/
├── raw/                        # raw source data (read-only)
│   ├── measurement/
│   ├── circuit_simulation/
│   └── layout_simulation/
├── trace_store/               # Zarr TraceStore (local backend)
└── database.db                # metadata DB (SQLite for now; PostgreSQL later)
```

## Rules

### 1. Raw Data is Read-Only

Everything under `data/raw/` is immutable:

- do not modify raw files
- do not delete raw files
- ingest / import / simulation / post-processing outputs must not be written back into the raw tree

### 2. Metadata vs Numeric Payload

Storage responsibility must stay explicit:

- **Metadata DB**
  - `DesignRecord`
  - `TraceRecord`
  - `TraceBatchRecord`
  - `AnalysisRunRecord`
  - `DerivedParameterRecord`
- **TraceStore**
  - trace numeric payload
  - axes arrays
  - sweep ND arrays

!!! important "No large numeric payload in the metadata DB"
    Large trace values must not use SQLite/PostgreSQL JSON/BLOB as the primary payload path.
    The metadata DB handles indexing, lineage, setup, and queries; numeric payload belongs in the `Zarr` TraceStore.

### 3. Use Path / Store Helpers

Do not hardcode metadata DB or TraceStore paths.

- metadata DB paths must come from persistence helpers
- TraceStore backend choice (local / S3-compatible) must go through an abstraction

### 4. Database Access (Unit of Work)

All metadata DB access must use Unit of Work:

```python
from core.shared.persistence import get_unit_of_work

with get_unit_of_work() as uow:
    design = uow.designs.get_by_name("PF6FQ_Q0")
    uow.traces.add(new_trace)
    uow.commit()
```

### 5. TraceStore Access

Trace numeric payload must be read and written through a TraceStore abstraction, not by letting UI/CLI code talk directly to backend-specific storage details.

Allowed backend direction:

- local filesystem `Zarr`
- S3-compatible `Zarr` (for example MinIO / S3 endpoints)

### 6. Canonical Trace Contract

- `TraceRecord` is the canonical unit for **one logical observable over axes**
- it may be 1D / 2D / ND
- a sweep point must not automatically become its own canonical trace record
- point/slice materialization is only a projection / cache / export contract

### 7. Output Locations

| Type | Target |
|------|--------|
| metadata records | metadata DB |
| trace numeric payload | TraceStore (`Zarr`) |
| reports / exports | `data/processed/reports/` or another explicit export path |

## Related

- [Design / Trace Schema](../../data-formats/dataset-record.en.md)
- [Raw Data Layout](../../data-formats/raw-data-layout.en.md)
- [Data Storage](../../../explanation/architecture/data-storage.en.md)

---

## Agent Rule { #agent-rule }

```markdown
## Data Handling
- **Immutable**: `data/raw/` is READ-ONLY.
- **Storage split**:
    - metadata goes to the metadata DB
    - numeric trace payload goes to the TraceStore (`Zarr`)
- **Paths**: NEVER hardcode metadata DB or TraceStore paths/backends.
- **Database**:
    - MUST use Unit of Work for metadata DB operations.
    - NEVER access Session directly in CLI/UI code.
    - MUST call `uow.commit()` explicitly.
- **TraceStore**:
    - MUST go through a TraceStore abstraction.
    - MUST support local `Zarr` as the baseline direction.
    - MUST keep S3-compatible `Zarr` as an extension-safe target.
- **Canonical trace contract**:
    - `TraceRecord` is one logical observable over axes.
    - ND traces are allowed and preferred over point-fragmented canonical storage.
    - point/slice materialization is projection/cache/export, not the only SoT.
- **Flow**:
    - Raw -> Import/Simulation/Post-Processing -> metadata DB + TraceStore -> Characterization / Reports
- **Legacy**:
    - Do not create new JSON-only numeric pipelines.
    - Do not treat SQLite/PostgreSQL JSON/BLOB as the long-term primary numeric trace store.
```
