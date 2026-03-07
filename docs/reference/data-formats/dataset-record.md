---
aliases:
  - "Dataset Record Schema"
  - "Design / Trace Schema"
  - "DatasetRecord 格式"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "DesignRecord / TraceRecord / TraceBatchRecord / TraceStoreRef target schema"
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Design / Trace Schema

!!! note "Path is historical"
    本頁檔名仍為 `dataset-record.md`，但 SoT 語意已更新為
    `DesignRecord / TraceRecord / TraceBatchRecord` 架構。

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

1. `DesignRecord` 是最高層 container。
2. `TraceRecord` 是 plotting / Characterization / compare 的標準操作單位。
3. `TraceBatchRecord` 保存 setup、source kind、lineage、status。
4. metadata DB 與 numeric payload 分離。
5. numeric payload 由 `TraceStore`（Zarr）保存，可走 local 或 S3-compatible backend。

---

## DesignRecord

一個 `DesignRecord` 代表一個 design/device/project scope，可同時容納：

- circuit simulation traces
- layout simulation traces
- measurement traces
- post-processed traces
- characterization outputs

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | 主鍵 |
| `name` | str | ✅ | design 識別名稱 |
| `design_meta` | JSON | - | design level metadata / tags / summary |
| `created_at` | datetime | Auto | 建立時間 |

!!! important "Source mix is allowed"
    一個 design 可以同時有 `circuit_simulation`、`layout_simulation`、`measurement`；
    也可以只擁有其中任一來源。

---

## DesignAssetRecord

設計層 source artifact。

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | 主鍵 |
| `design_id` | int | ✅ | 所屬 DesignRecord |
| `asset_type` | str | ✅ | `circuit_definition` / `layout_source` / `measurement_source` |
| `version` | str | - | revision / import version |
| `content_payload` | JSON | ✅ | source-form document or import manifest |

!!! important "Circuit Definition stays document-first"
    Circuit Definition 的原子單位仍是一份 revisioned source document，
    不應先拆成 components/topology relational rows。

---

## TraceRecord

`TraceRecord` 是 **one logical observable over axes**。

它可以是：

- 1D: `Imag(Y_dm_dm)` over `frequency`
- 2D: `Imag(Y_dm_dm)` over `(frequency, L_jun)`
- ND: `Imag(Y_dm_dm)` over `(frequency, A, B, ...)`

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | 主鍵 |
| `design_id` | int | ✅ | 所屬 DesignRecord |
| `family` | str | ✅ | `s_matrix` / `y_matrix` / `z_matrix` / equivalent canonical family |
| `parameter` | str | ✅ | `Y11`, `Y_dm_dm`, `S21` 等 |
| `representation` | str | ✅ | `real`, `imaginary`, `magnitude`, `phase` |
| `axes` | JSON | ✅ | 軸定義與順序 |
| `trace_meta` | JSON | - | 單位、basis labels、source annotations 等 |
| `store_ref` | JSON | ✅ | 指向 TraceStore 的定位資訊 |

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
  "store_uri": "data/trace_store/designs/42/batches/105.zarr",
  "group_path": "/traces/9001",
  "array_path": "values",
  "dtype": "float64",
  "shape": [4001, 11],
  "chunk_shape": [4001, 1],
  "schema_version": "1.0"
}
```

**backend 可用值（目前 direction）**

- `local_zarr`
- `s3_zarr`

!!! important "Canonical ND trace"
    sweep point 不應自動升格為一筆 canonical `TraceRecord`。
    若 UI / export / cache 需要 point-level materialization，應視為 projection 契約。

---

## TraceBatchRecord

`TraceBatchRecord` 是一次 import / simulation / preprocess / postprocess 的 setup 與 provenance 邊界。

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | 主鍵 |
| `design_id` | int | ✅ | 所屬 DesignRecord |
| `source_kind` | str | ✅ | `circuit_simulation` / `layout_simulation` / `measurement` |
| `stage_kind` | str | ✅ | `import` / `raw` / `preprocess` / `postprocess` |
| `parent_batch_id` | int | - | 上游 batch lineage |
| `asset_record_id` | int | - | 關聯 source asset |
| `status` | str | ✅ | `running` / `completed` / `failed` |
| `setup_kind` | str | ✅ | 例如 `circuit_simulation.raw` |
| `setup_version` | str | ✅ | setup payload version |
| `setup_payload` | JSON | ✅ | source/setup/post-processing contract |
| `provenance_payload` | JSON | ✅ | lineage / source refs / summaries |
| `summary_payload` | JSON | - | optional UI summary |

!!! important "Generalized setup layer"
    `TraceBatchRecord` 是 circuit/layout/measurement 三種來源共用的 setup/provenance 抽象。
    差異放在 `source_kind + stage_kind + setup_payload`，而不是各自發明平行主模型。

---

## TraceBatchTraceLink

batch 與 trace 的關聯。

| Field | Type | Required | Description |
|---|---|---|---|
| `trace_batch_id` | int | ✅ | 所屬 TraceBatchRecord |
| `trace_record_id` | int | ✅ | 所屬 TraceRecord |

---

## AnalysisRunRecord

Characterization / fitting / extraction 的執行邊界。

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | 主鍵 |
| `design_id` | int | ✅ | 所屬 DesignRecord |
| `analysis_id` | str | ✅ | `admittance_extraction` 等 |
| `input_trace_ids` | JSON | ✅ | selected trace ids |
| `config_payload` | JSON | ✅ | analysis config |
| `status` | str | ✅ | `running` / `completed` / `failed` |
| `input_batch_ids` | JSON | - | optional source batch refs |

!!! important "Trace-first authority"
    Characterization 的統一輸入是 `TraceRecord`，不以來源類型區分 circuit/layout/measurement 專用分析流程。

---

## DerivedParameterRecord

物理萃取結果。

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | 主鍵 |
| `design_id` | int | ✅ | 所屬 DesignRecord |
| `analysis_run_id` | int | ✅ | 來源 AnalysisRunRecord |
| `name` | str | ✅ | parameter name |
| `value` | float | ✅ | value |
| `unit` | str | - | unit |
| `extra` | JSON | - | sweep provenance / fit metadata |

---

## TraceStore Direction

`TraceStore` 採 `Zarr`，並保留 backend abstraction：

- 現階段：local filesystem
- storage extension：S3-compatible endpoint（例如 MinIO / S3）

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

### S3-Compatible Direction

同一個 `TraceStoreRef` contract 應可對應：

- `file://...`
- `s3://bucket/...`
- MinIO S3 endpoint

不得讓 UI / Characterization / repositories 直接耦合 backend-specific path logic。

## Related

- [Data Storage](../../explanation/architecture/data-storage.md)
- [Query Indexing Strategy](query-indexing-strategy.md)
- [Raw Data Layout](raw-data-layout.md)
