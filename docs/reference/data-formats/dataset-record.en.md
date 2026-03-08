---
aliases:
  - "Dataset Record Schema"
  - "Design / Trace Schema"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Target schema for DesignRecord / TraceRecord / TraceBatchRecord / TraceStoreRef"
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Design / Trace Schema

!!! note "Historical path"
    This file still uses the historical path `dataset-record.en.md`, but the SoT terminology now follows the
    `DesignRecord / TraceRecord / TraceBatchRecord` architecture.

## Core Model

```text
DesignRecord
├── DesignAssetRecord[]        # circuit definition / layout source / measurement source
├── TraceBatchRecord[]         # import / simulation / preprocess / postprocess batches
├── TraceRecord[]              # analyzable traces (1D / 2D / ND)
├── AnalysisRunRecord[]        # characterization / fitting runs
└── DerivedParameterRecord[]   # extracted physics parameters
```

## Design Principles

1. `DesignRecord` is the top-level container.
2. `TraceRecord` is the standard unit consumed by plotting, Characterization, and comparison flows.
3. `TraceBatchRecord` carries setup, source kind, lineage, and status.
4. metadata DB and numeric payload must remain separate.
5. numeric payload is stored in `TraceStore` (`Zarr`); the only active backend right now is local.

---

## DesignRecord

A `DesignRecord` represents one design/device/project scope and may contain:

- circuit simulation traces
- layout simulation traces
- measurement traces
- post-processed traces
- characterization outputs

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | primary key |
| `name` | str | ✅ | design identifier |
| `design_meta` | JSON | - | design-level metadata / tags / summary |
| `created_at` | datetime | Auto | creation time |

!!! important "Source mix is allowed"
    One design may contain `circuit_simulation`, `layout_simulation`, and `measurement` data together,
    or only any subset of them.

---

## DesignAssetRecord

Design-level source artifact.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | primary key |
| `design_id` | int | ✅ | owning DesignRecord |
| `asset_type` | str | ✅ | `circuit_definition` / `layout_source` / `measurement_source` |
| `version` | str | - | revision / import version |
| `content_payload` | JSON | ✅ | source-form document or import manifest |

!!! important "Circuit Definition stays document-first"
    The atomic unit for Circuit Definition remains a revisioned source document,
    not a decomposed set of component/topology relational rows.

---

## TraceRecord

`TraceRecord` means **one logical observable over axes**.

It may be:

- 1D: `Imag(Y_dm_dm)` over `frequency`
- 2D: `Imag(Y_dm_dm)` over `(frequency, L_jun)`
- ND: `Imag(Y_dm_dm)` over `(frequency, A, B, ...)`

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | primary key |
| `design_id` | int | ✅ | owning DesignRecord |
| `family` | str | ✅ | `s_matrix` / `y_matrix` / `z_matrix` / equivalent canonical family |
| `parameter` | str | ✅ | `Y11`, `Y_dm_dm`, `S21`, etc. |
| `representation` | str | ✅ | `real`, `imaginary`, `magnitude`, `phase` |
| `axes` | JSON | ✅ | axis definitions and order |
| `trace_meta` | JSON | - | units, basis labels, source annotations, etc. |
| `store_ref` | JSON | ✅ | locator for TraceStore payload |

### Axes Contract

```json
[
  {"name": "frequency", "unit": "GHz", "length": 4001},
  {"name": "L_jun", "unit": "nH", "length": 11}
]
```

### TraceStoreRef Contract

```json
{
  "backend": "local_zarr",
  "store_key": "designs/42/batches/105.zarr",
  "store_uri": "data/trace_store/designs/42/batches/105.zarr",
  "group_path": "/traces/9001",
  "array_path": "values",
  "dtype": "float64",
  "shape": [4001, 11],
  "chunk_shape": [4001, 1],
  "schema_version": "1.0"
}
```

`store_key` is the canonical locator. `store_uri` remains an opaque backend-owned compatibility/debug locator and must not be parsed by the UI or application layer to recover local path layout.

**Allowed direction for `backend`**

- `local_zarr`

!!! note "Object-storage extension is deferred"
    `s3_zarr` / MinIO / S3 is not the active implementation target right now.
    If object-storage extension work resumes later, it should return as an additive contract without changing the current local path.

!!! important "Canonical ND trace"
    A sweep point must not automatically become its own canonical `TraceRecord`.
    If UI / export / cache paths need point-level materialization, treat it as a projection contract.

---

## TraceBatchRecord

`TraceBatchRecord` is the setup and provenance boundary for one import / simulation / preprocess / postprocess run.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | primary key |
| `design_id` | int | ✅ | owning DesignRecord |
| `source_kind` | str | ✅ | `circuit_simulation` / `layout_simulation` / `measurement` |
| `stage_kind` | str | ✅ | `import` / `raw` / `preprocess` / `postprocess` |
| `parent_batch_id` | int | - | upstream batch lineage |
| `asset_record_id` | int | - | related source asset |
| `status` | str | ✅ | `running` / `completed` / `failed` |
| `setup_kind` | str | ✅ | for example `circuit_simulation.raw` |
| `setup_version` | str | ✅ | setup payload version |
| `setup_payload` | JSON | ✅ | source/setup/post-processing contract |
| `provenance_payload` | JSON | ✅ | lineage / source refs / summaries |
| `summary_payload` | JSON | - | optional UI summary |

!!! important "Generalized setup layer"
    `TraceBatchRecord` is the shared setup/provenance abstraction for circuit/layout/measurement.
    Differences belong in `source_kind + stage_kind + setup_payload`, not in parallel top-level models.

---

## TraceBatchTraceLink

Batch-to-trace membership.

| Field | Type | Required | Description |
|---|---|---|---|
| `trace_batch_id` | int | ✅ | owning TraceBatchRecord |
| `trace_record_id` | int | ✅ | linked TraceRecord |

---

## AnalysisRunRecord

Execution boundary for characterization / fitting / extraction.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | primary key |
| `design_id` | int | ✅ | owning DesignRecord |
| `analysis_id` | str | ✅ | for example `admittance_extraction` |
| `input_trace_ids` | JSON | ✅ | selected trace ids |
| `config_payload` | JSON | ✅ | analysis config |
| `status` | str | ✅ | `running` / `completed` / `failed` |
| `input_batch_ids` | JSON | - | optional source batch refs |

!!! important "Trace-first authority"
    Characterization consumes `TraceRecord` uniformly and does not branch into separate circuit/layout/measurement analysis models.

---

## DerivedParameterRecord

Physics extraction output.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | primary key |
| `design_id` | int | ✅ | owning DesignRecord |
| `analysis_run_id` | int | ✅ | source AnalysisRunRecord |
| `name` | str | ✅ | parameter name |
| `value` | float | ✅ | value |
| `unit` | str | - | unit |
| `extra` | JSON | - | sweep provenance / fit metadata |

---

## TraceStore Direction

`TraceStore` uses `Zarr` and keeps backend abstraction explicit:

- current baseline: local filesystem
- storage extension target (deferred): S3-compatible endpoints (for example MinIO / S3)

### Recommended Local Layout

```text
data/trace_store/
└── designs/
    └── <design_id>/
        └── batches/
            └── <batch_id>.zarr/
                └── traces/
                    └── <trace_id>/
                        └── values
```

### Deferred Object-Storage Direction

If object-storage extension work resumes later, the same `TraceStoreRef` contract must still support:

- `file://...`
- `s3://bucket/...`
- MinIO S3 endpoints

That is not a blocker for the current phase. The only active path right now is local `Zarr`.

## Related

- [Data Storage](../../explanation/architecture/data-storage.en.md)
- [Query Indexing Strategy](query-indexing-strategy.en.md)
- [Raw Data Layout](raw-data-layout.en.md)
