---
aliases:
  - Backend Characterization Results
  - Characterization Result Service
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Characterization analysis registry、run history、artifact manifest、artifact payload 與 identify/tagging 的 backend reference surface。
version: v0.4.0
last_updated: 2026-03-13
updated_by: team
---

# Characterization Results

本頁定義 frontend `Characterization` 頁依賴的 analysis result surface。

!!! info "Surface Boundary"
    本頁負責 analysis-specific read / mutation contract。
    task lifecycle 本身由 [Tasks & Execution](tasks-execution.md) 定義。

!!! tip "Primary Consumers"
    主要消費者是 [Characterization](../frontend/research-workflow/characterization.md) 與 [Dashboard](../frontend/workspace/dashboard.md)。

---

## 涵蓋範圍 (Coverage)

| Surface | 說明 |
| :--- | :--- |
| **Analysis Registry Summary** | 分析項註冊摘要 |
| **Run History List** | 執行歷史列表 |
| **Result Artifact Manifest** | 結果產出清單 |
| **Artifact Payload Query** | 產出內容查詢 |
| **Identify Mode / Parameter Tagging** | 識別模式與參數標記異動 |

---

## Surface Contracts

=== "Analysis Registry"

    registry summary 至少必須提供：

    | 欄位 | 說明 |
    | :--- | :--- |
    | `analysis_id` | 分析項唯一識別 |
    | `label` | 顯示標籤 |
    | `availability_state` | 可用狀態 |
    | `required_config_fields` | 必要配置欄位 |
    | `trace_compatibility` | Trace 相容性摘要 |

=== "Run History"

    run history 每列至少必須提供：

    | 類別 | 包含項目 |
    | :--- | :--- |
    | **Identity** | run identifier, analysis type |
    | **State** | status, scope |
    | **Metrics** | traces count |
    | **Metadata** | sources summary, provenance summary |

=== "Result Artifacts"

    manifest 至少必須提供：

    | 屬性 | 說明 |
    | :--- | :--- |
    | `artifact_id` | 產出唯一識別 |
    | `category` | 類別 (例如：Plot, Table) |
    | `view_kind` | 視圖類型 |
    | `title` | 標題 |
    | `query_spec` | artifact-level 查詢規格 |

    query 至少必須支援：

    - **Mode Filter**: trace mode filter
    - **Selection**: category selection / artifact tab selection
    - **Data**: table / plot 繪製所需 payload

=== "Identify / Tagging"

    backend 必須支援以下操作：

    1. **Selection Path**: source parameter selection 所需資料
    2. **Metric Path**: designated metric selection 所需資料
    3. **Mutation**: parameter tagging mutation

!!! warning "Trace-first Gating"
    availability 必須由 **compatible traces** 與 **selected trace ids** 驅動。
    design profile 只提供提示，不是唯一的硬性門檻。

!!! tip "Persisted Authority"
    run history 是 **persisted record surface**。
    frontend 重新整理後必須能重新讀回一致內容，不得僅依賴 page-local memory。

!!! warning "Artifact-first Result View"
    frontend result view 應 **僅依賴** artifact manifest 與 artifact payload。
    backend 不得要求 frontend 直接解析 `DerivedParameter.name` 來自行拼接結果視圖。

!!! check "Consistency Guarantee"
    mutation 完成後，當 result context 或 run history 需要重讀時，應能從 **persisted state** 取得一致結果。

---

## Tagging Propagation

`Tag Parameter` mutation 成功後，backend 還必須更新供 Dashboard 使用的 dataset-level metrics summary。

| 後續讀取方 | 預期結果 |
| :--- | :--- |
| [Characterization](../frontend/research-workflow/characterization.md) | 重新讀取後看到最新 tagging 狀態 |
| [Dashboard](../frontend/workspace/dashboard.md) | `Tagged Core Metrics` 摘要可讀回最新標記 |

!!! warning "Cross-page Consistency"
    identify / tagging 不是只影響 Characterization 局部畫面。
    mutation 成功後，相關 dataset summary 必須能跨頁一致讀回。

---

## Delivery Rules

| 項目 | 規則 |
| :--- | :--- |
| **Run/Result Split** | run lifecycle 與 result payload 是不同 surface，但必須可由同一 run lineage 串接。 |
| **Empty Diagnostics** | 若 run 完成但無 renderable artifact，backend 應回傳顯式的 empty-state 診斷資訊。 |
| **No Rerun** | artifact payload query **不得隱式重跑** analysis。 |
| **Trace Consistency** | `All / Base / Sideband` 的過濾語意必須與 frontend 保持絕對一致。 |

---

## Related

- [Characterization](../frontend/research-workflow/characterization.md)
- [Tasks & Execution](tasks-execution.md)
- [Analysis Result Schema](../../data-formats/analysis-result.md)
- [Task Semantics](../../architecture/task-semantics.md)
