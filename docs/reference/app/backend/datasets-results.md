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
version: v0.7.0
last_updated: 2026-03-14
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

    payload baseline：

    | Field | Meaning |
    |---|---|
    | `dataset_id` | active dataset identity |
    | `device_type` | dataset profile device type |
    | `capabilities[]` | dataset capability labels |
    | `source` | `manual`, `inferred`, `imported` 等 profile source |
    | `updated_at` | profile freshness |

=== "Tagged Core Metrics Summary"

    Dashboard 顯示的 `Tagged Core Metrics` 屬於唯讀摘要 surface，backend 至少必須提供：

    | 欄位 | 說明 |
    | :--- | :--- |
    | `metric_id` | 指標唯一識別 |
    | `label` | 顯示名稱 |
    | `source_parameter` | 來源參數 |
    | `designated_metric` | 對應度量 |
    | `tagged_at` | 標記時間 |

## Dataset Activation Pairing

| Concern | Rule |
|---|---|
| Dataset browse | 只列出對 active workspace 可見的 datasets / designs |
| Profile write | 必須對應 active dataset，不接受 page-local 假資料集 |
| Tagged metrics summary | 隨 active dataset 切換而一起切換 |

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

## Request / Response Examples

!!! example "Dataset profile read"
    Response:
    ```json
    {
      "ok": true,
      "data": {
        "dataset_id": "ds_xy_001",
        "device_type": "Unspecified",
        "capabilities": [],
        "source": "inferred",
        "updated_at": "2026-03-14T10:20:00Z"
      }
    }
    ```

!!! example "Dataset profile update"
    Request:
    ```json
    {
      "dataset_id": "ds_xy_001",
      "device_type": "transmon",
      "capabilities": ["characterization", "simulation_review"]
    }
    ```

    Response:
    ```json
    {
      "ok": true,
      "data": {
        "dataset_id": "ds_xy_001",
        "device_type": "transmon",
        "capabilities": ["characterization", "simulation_review"],
        "source": "manual",
        "updated_at": "2026-03-14T10:22:00Z"
      }
    }
    ```

!!! example "Tagged core metrics summary"
    Response:
    ```json
    {
      "ok": true,
      "data": {
        "dataset_id": "ds_xy_001",
        "metrics": [
          {
            "metric_id": "metric_mode_1_frequency",
            "label": "Mode 1 Frequency",
            "source_parameter": "L_q",
            "designated_metric": "mode_1_frequency",
            "tagged_at": "2026-03-14T10:24:00Z"
          }
        ]
      }
    }
    ```

## Error Code Contract

| Code | Category | When it applies |
|---|---|---|
| `dataset_not_found` | `not_found` | dataset 不存在 |
| `dataset_not_visible_in_workspace` | `permission_denied` | dataset 不屬於或不可見於 active workspace |
| `dataset_profile_update_denied` | `permission_denied` | session 無 dataset metadata write 權限 |
| `dataset_profile_invalid` | `validation_error` | device type 或 capability payload 不符合 contract |
| `trace_not_found` | `not_found` | trace detail 指向不存在 trace |
| `trace_payload_not_ready` | `task_not_ready` | trace / result payload 尚未準備好 |

---

## Related

- [Dashboard](../frontend/workspace/dashboard.md)
- [Raw Data Browser](../frontend/workspace/raw-data-browser.md)
- [Characterization](../frontend/research-workflow/characterization.md)
- [Characterization Results](characterization-results.md)
- [Design / Trace Schema](../../data-formats/dataset-record.md)
- [Analysis Result](../../data-formats/analysis-result.md)
