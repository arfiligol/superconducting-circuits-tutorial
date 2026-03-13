---
aliases:
  - Backend Datasets Results Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Backend dataset、trace、result 與 provenance reference surface。
version: v0.6.0
last_updated: 2026-03-13
updated_by: team
---

# Datasets & Results

本頁定義 Dashboard、Raw Data Browser、Characterization 與部分 Result View 依賴的 dataset / trace / result surface。

!!! info "Surface Boundary"
    本頁負責 design browse、trace metadata、trace detail、dataset profile read/write、tagged core metrics summary 與 provenance-bearing result handles。
    task lifecycle 與 characterization artifact manifest 不屬於本頁責任。

!!! tip "Primary Consumers"
    主要消費者是 [Dashboard](../frontend/workspace/dashboard.md)、[Raw Data Browser](../frontend/workspace/raw-data-browser.md)、[Characterization](../frontend/research-workflow/characterization.md) 與 [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md)。

---

## 涵蓋範圍 (Coverage)

| Surface | 說明 |
| :--- | :--- |
| **Design Browse** | 模型設計清單與詳情 |
| **Trace Surface** | Trace 元資料列表與單筆詳情 |
| **Dataset Profile** | 讀取與寫入介面 |
| **Tagged Core Metrics Summary** | Dashboard 唯讀摘要所需的核心指標 |
| **Provenance** | 帶有原溯資訊的結果控制項 |
| **Storage** | 面向後端之儲存語意 |

---

## Surface Contracts

=== "Design Browse"

    backend 至少必須支援以下摘要資訊：

    | 欄位 | 說明 |
    | :--- | :--- |
    | **Summary List** | design 摘要清單 |
    | **Single Summary** | 單個 design 摘要 |
    | **Provenance** | design-level source coverage 與來源追蹤摘要 |

=== "Trace Surface"

    trace surface 必須嚴格拆分為兩條異步路徑以優化載入效能：

    1. **Metadata List Path**: 僅載入元資料列表
    2. **Trace Detail Path**: 僅在點選時請求詳細數據

=== "Dataset Profile"

    backend 必須支援 Dashboard 對應的 profile 操作：

    - 讀取 dataset profile summary。
    - 儲存由 dashboard 編輯後的最新 profile。
    - 同一 session 內立即反映異動。

=== "Tagged Core Metrics Summary"

    Dashboard 顯示的 `Tagged Core Metrics` 屬於唯讀摘要 surface，backend 至少必須提供：

    | 欄位 | 說明 |
    | :--- | :--- |
    | `metric_id` | 指標唯一識別 |
    | `label` | 顯示名稱 |
    | `source_parameter` | 來源參數 |
    | `designated_metric` | 對應度量 |
    | `tagged_at` | 標記時間 |

!!! warning "Summary-first Browse"
    design list path 只能提供 **summary-safe** 欄位。
    不得在 list 查詢時一併回傳巨大的 trace numeric payload。

!!! warning "Write Boundary 限定"
    dataset profile 的正式可寫入口**僅服務於 Dashboard 類型**的 surface。
    Raw Data Browser 與 Circuit Simulation 不應提供等價的元資料寫入行為。

!!! tip "Lazy Loading 規則"
    frontend 只有在使用者選定特定 trace 時，才透過 detail path 取得單筆 payload。
    backend 不得要求 Raw Data Browser 一次性載入整個 design 的所有 trace arrays。

!!! tip "Read / Write Split"
    `Tagged Core Metrics` 的讀取摘要屬於本頁 surface。
    實際的 identify / tagging mutation 則由 [Characterization Results](characterization-results.md) 定義。

---

## Related

- [Dashboard](../frontend/workspace/dashboard.md)
- [Raw Data Browser](../frontend/workspace/raw-data-browser.md)
- [Characterization](../frontend/research-workflow/characterization.md)
- [Characterization Results](characterization-results.md)
- [Design / Trace Schema](../../data-formats/dataset-record.md)
- [Analysis Result](../../data-formats/analysis-result.md)
