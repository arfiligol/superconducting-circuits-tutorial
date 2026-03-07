---
aliases:
  - Query Indexing Strategy
  - 查詢索引策略
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: "metadata DB 查詢策略與 TraceStore slice-read 效能策略"
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Query Indexing Strategy

本頁定義 target architecture 下的效能責任分工：

1. **metadata DB** 處理查詢、索引、關聯、lineage。
2. **TraceStore (`Zarr`)** 處理 ND numeric payload 與 slice read。
3. 不應再把大型 trace values 的主要效能問題推回 SQLite/PostgreSQL JSON/BLOB。

## Metadata DB Hot Paths

### Design / Trace 路徑

| Repo API | 使用情境 | 主要 filter/sort |
|---|---|---|
| `count_by_design(design_id)` | Design scope summary | `design_id` |
| `list_trace_index_page(design_id, query=...)` | Raw Data / Characterization / compare trace selection | `design_id`, `family`, `parameter`, `representation`, `source_kind`, `stage_kind` |
| `list_distinct_trace_index(...)` | trace compatibility / UI filter options | `design_id`, `family/parameter/representation` |

### TraceBatch 路徑

| Repo API | 使用情境 | 主要 filter/sort |
|---|---|---|
| `list_batches_by_design(design_id)` | provenance timeline | `design_id`, `source_kind`, `stage_kind`, `created_at` |
| `get_batch_lineage(batch_id)` | postprocess / analysis lineage | `parent_batch_id` |
| `list_traces_by_batch(batch_id)` | batch-scoped trace lookup | `trace_batch_id` |

### Analysis 路徑

| Repo API | 使用情境 | 主要 filter/sort |
|---|---|---|
| `list_analysis_runs_by_design(design_id)` | Characterization history | `design_id`, `analysis_id`, `created_at` |
| `list_derived_parameters_by_design(design_id)` | result tables / dashboards | `design_id`, `analysis_run_id`, `name` |

## Metadata Index Direction

優先索引候選：

1. `trace_records(design_id, family, parameter, representation)`
2. `trace_batch_records(design_id, source_kind, stage_kind, created_at)`
3. `trace_batch_records(parent_batch_id)`
4. `trace_batch_trace_links(trace_batch_id, trace_record_id)`
5. `analysis_run_records(design_id, analysis_id, created_at)`

## TraceStore Read Strategy

!!! important "Do not full-read then slice"
    UI / Characterization 若只需要某個 ND slice，應直接對 `Zarr` 做 slice read。
    不可先 `[:]` 全讀，再在 Python 記憶體內切片。

### Common Access Pattern

Simulation / Post-Processing UI 常見路徑：

- 固定 sweep coordinates
- `X = frequency`
- 多條 traces 比較不同 sweep values

建議 chunking direction：

- sweep dims 用小 chunk
- frequency dim 用連續 chunk

例如 trace shape:

```text
(sweep_a, sweep_b, frequency)
```

可考慮 chunk:

```text
(1, 1, 4001)
```

或

```text
(1, 1, 512)
```

### Why canonical ND still scales

canonical `TraceRecord` 為 ND，不代表每次都讀完整 ND array。
只要 chunking 與 axis order 對齊 access pattern，就能只讀需要的 chunks。

## S3 / MinIO Direction

當 TraceStore backend 改為 S3-compatible 時，效能策略仍相同：

- metadata query 先在 DB 完成
- numeric payload 以 chunked slice read 存取
- app/service 層不得耦合 local-path-only 邏輯

## Validation Direction

實作此架構時，優先驗證：

1. JosephsonCircuits.jl 官方 examples 跑完後，能正確寫入 `DesignRecord + TraceBatchRecord + TraceRecord + Zarr`
2. UI compare / Characterization path 只讀必要 slices，不做整體 full-read
3. post-processed sweep 與 raw sweep 都能對齊同一套 trace-first query model

## Related

- [Design / Trace Schema](dataset-record.md)
- [Data Storage](../../explanation/architecture/data-storage.md)
