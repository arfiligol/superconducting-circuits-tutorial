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
scope: "高頻 DataRecord/ResultBundle 查詢路徑與索引策略（不改 DB 架構方向）"
version: v1.0.0
last_updated: 2026-03-05
updated_by: codex
---

# Query Indexing Strategy

本頁定義高頻查詢路徑與索引策略，目的在於：

1. 維持現有 `SQLModel + UnitOfWork + Repository` 架構不變。
2. 讓大資料量頁面（Raw Data / Characterization）有可預期延遲。
3. 在不立即改 schema 的前提下，先明確「應監控與優先補索引」的路徑。

!!! important "邊界"
    本頁是 **查詢策略與優先級契約**，不是 migration 指令。
    若要新增索引，請走正常 DB migration 流程，並同步更新本頁。

## 高頻查詢路徑

### DataRecord 路徑（Trace-first）

| Repo API | 使用情境 | 主要 filter/sort |
|---|---|---|
| `count_by_dataset(dataset_id)` | Characterization/Raw Data scope summary | `dataset_id` |
| `list_distinct_index_for_profile(dataset_id)` | dataset profile hint 推導 | `dataset_id` + `data_type/parameter/representation` distinct |
| `list_index_page_by_dataset(dataset_id, query=...)` | Trace table 分頁/篩選/排序 | `dataset_id`, `data_type`, `parameter`, `representation`, `mode_filter`, `search`, `sort_by` |

### ResultBundle 路徑（provenance/cache 分流）

| Repo API | 使用情境 | 主要 filter/sort |
|---|---|---|
| `list_by_dataset(dataset_id)` | Dataset 下所有 bundles（除錯/追蹤） | `dataset_id`, `id` |
| `list_cache_by_dataset(dataset_id)` | Simulation cache 管理 | `dataset_id`, `role=cache` |
| `list_provenance_by_dataset(dataset_id)` | UI 顯示可追蹤結果批次 | `dataset_id`, `role!=cache` |
| `count_by_dataset(..., include_cache=...)` | Source Scope / summary counters | `dataset_id`, `bundle_type`, `role` |
| `list_data_record_index_page(bundle_id, query=...)` | bundle-scoped trace paging | `result_bundle_id` + trace query filters |

## 現況索引（模型層）

目前 `SQLModel` 明確宣告的索引重點：

- `dataset_records.name`
- `data_records.dataset_id`
- `result_bundle_records.dataset_id`
- `result_bundle_records.bundle_type`
- `result_bundle_records.role`
- `result_bundle_records.status`
- `result_bundle_records.schema_source_hash`
- `result_bundle_records.simulation_setup_hash`

參考：
- [`models.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/shared/persistence/models.py)
- [`data_record_repository.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/shared/persistence/repositories/data_record_repository.py)
- [`result_bundle_repository.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/shared/persistence/repositories/result_bundle_repository.py)

## 優先索引候選（下一階段）

!!! note "候選，非立即強制"
    以下是針對高頻 query 的優先候選，需在 migration 任務中驗證後實施。

1. `data_records(dataset_id, data_type, parameter, representation)`
   適用 `list_index_page_by_dataset` 多條件過濾。
2. `result_bundle_data_links(result_bundle_id, data_record_id)`
   適用 bundle-scoped trace paging join。
3. `result_bundle_records(dataset_id, role, bundle_type, status)`
   適用 provenance/cache summary 與列表。

## 監控建議

1. JTWPA 等大資料案例記錄 P95 query latency。
2. 追蹤 `count_*` 與 `list_*_page` 的 DB 執行時間。
3. 若 `search + mode_filter` 組合顯著退化，優先補複合索引或調整查詢策略。

## Related

- [Dataset Record](dataset-record.md)
- [Analysis Result](analysis-result.md)
- [Characterization UI](../ui/characterization.md)
- [Data Handling Guardrail](../guardrails/code-quality/data-handling.md)
