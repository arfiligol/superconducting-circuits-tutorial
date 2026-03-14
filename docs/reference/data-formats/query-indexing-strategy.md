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
scope: dataset-first metadata DB query strategy and TraceStore slice-read strategy
version: v3.0.0
last_updated: 2026-03-14
updated_by: codex
---

# Query Indexing Strategy

本頁定義 dataset-first persisted model 下的效能責任分工：

1. **metadata DB** 處理 dataset、design、trace、lineage、artifact query。
2. **TraceStore (`Zarr`)** 處理 ND numeric payload 與 slice read。
3. 不應再把大型 trace values 的主要效能問題推回 SQLite/PostgreSQL JSON/BLOB。

## Metadata DB Hot Paths

### Dataset / Design / Trace 路徑

| Repo API | 使用情境 | 主要 filter / sort |
| --- | --- | --- |
| `list_visible_datasets(workspace_id, query=...)` | Header dataset switcher / dashboard selector | `workspace_id`, `visibility_scope`, `updated_at` |
| `get_dataset_profile(dataset_id)` | Dashboard profile read | `dataset_id` |
| `list_design_scopes(dataset_id, query=...)` | Raw Data / Characterization design selector | `dataset_id`, `name`, `updated_at` |
| `count_traces(dataset_id, design_id)` | design scope summary | `dataset_id`, `design_id` |
| `list_trace_index_page(dataset_id, design_id, query=...)` | Raw Data / Characterization / compare trace selection | `dataset_id`, `design_id`, `family`, `parameter`, `representation`, `source_kind`, `stage_kind` |
| `list_distinct_trace_index(dataset_id, design_id, ...)` | trace compatibility / UI filter options | `dataset_id`, `design_id`, `family`, `parameter`, `representation` |

### TraceBatch / Provenance 路徑

| Repo API | 使用情境 | 主要 filter / sort |
| --- | --- | --- |
| `list_batches(dataset_id, design_id)` | provenance timeline | `dataset_id`, `design_id`, `source_kind`, `stage_kind`, `created_at` |
| `get_batch_lineage(batch_id)` | postprocess / analysis lineage | `parent_batch_id` |
| `list_traces_by_batch(batch_id)` | batch-scoped trace lookup | `trace_batch_id` |

### Analysis / Artifact 路徑

| Repo API | 使用情境 | 主要 filter / sort |
| --- | --- | --- |
| `list_analysis_runs(dataset_id, design_id)` | Characterization history | `dataset_id`, `design_id`, `analysis_id`, `created_at` |
| `list_result_artifacts(run_id)` | Result artifact manifest | `run_id`, `category`, `trace_mode_group` |
| `list_derived_parameters(dataset_id, design_id)` | result tables / dashboards | `dataset_id`, `design_id`, `analysis_run_id`, `name` |

## Metadata Index Direction

優先索引候選：

1. `dataset_records(workspace_id, visibility_scope, lifecycle_state, updated_at)`
2. `design_scopes(dataset_id, name, updated_at)`
3. `trace_records(dataset_id, design_id, family, parameter, representation)`
4. `trace_batch_records(dataset_id, design_id, source_kind, stage_kind, created_at)`
5. `trace_batch_trace_links(trace_batch_id, trace_record_id)`
6. `analysis_run_records(dataset_id, design_id, analysis_id, created_at)`
7. `result_artifacts(analysis_run_id, category, trace_mode_group)`
8. `derived_parameter_records(dataset_id, design_id, analysis_run_id, name)`

## Required Join Discipline

| Rule | Meaning |
| --- | --- |
| Dataset first | 先以 `dataset_id` 確認 app shell context |
| Design second | 再以 `design_id` 決定 page-local analytical scope |
| Trace third | trace / batch / run 查詢不得跳過 dataset boundary 直接只用 `design_id` |

## TraceStore Read Strategy

!!! important "Filter in metadata DB first"
    dataset / design / trace selection 必須先在 metadata DB 完成。
    只有在使用者真正進入 trace detail、result payload 或 slice preview 時，才對 `TraceStore` 做 read。

!!! important "Do not full-read then slice"
    UI / Characterization 若只需要某個 ND slice，應直接對 `Zarr` 做 slice read。
    不可先 `[:]` 全讀，再在 Python 記憶體內切片。

### Common Access Pattern

Simulation / Post-Processing / Characterization UI 常見路徑：

- 固定 sweep coordinates
- `X = frequency`
- 多條 traces 比較不同 sweep values

建議 chunking direction：

- sweep dims 用小 chunk
- frequency dim 用連續 chunk

例如 trace shape：

```text
(sweep_a, sweep_b, frequency)
```

可考慮 chunk：

```text
(1, 1, 4001)
```

或

```text
(1, 1, 512)
```

## S3 / MinIO Direction

當 TraceStore backend 改為 S3-compatible 時，效能策略仍相同：

- metadata query 先在 DB 完成
- numeric payload 以 chunked slice read 存取
- app / service 層不得耦合 local-path-only 邏輯

## Validation Direction

實作此架構時，優先驗證：

1. ingest / simulation / postprocess 流程都能正確寫入 `dataset_id + design_id + TraceBatchRecord + TraceRecord + Zarr`
2. dataset / design / trace 的 query path 先在 metadata DB 完成篩選
3. UI compare / Characterization path 只讀必要 slices，不做整體 full-read
4. post-processed sweep 與 raw sweep 都能對齊同一套 trace-first query model

## Related

- [Dataset / Design / Trace Schema](dataset-record.md)
- [Analysis Result](analysis-result.md)
- [Data Storage](../../explanation/architecture/data-storage.md)
