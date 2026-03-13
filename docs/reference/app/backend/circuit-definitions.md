---
aliases:
  - Backend Circuit Definitions
  - Circuit Definition Service
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Circuit definition catalog、detail、mutation 與 persisted inspection read model 的 backend reference surface。
version: v0.3.0
last_updated: 2026-03-13
updated_by: team
---

# Circuit Definitions

本頁定義 frontend `Schemas` / `Schema Editor` 依賴的 backend circuit definition surface。

!!! info "Surface Boundary"
    本頁只定義 definition catalog、detail、mutation 與 persisted inspection read model。
    simulation、schemdraw render 與 characterization run 不屬於本頁責任。

!!! tip "Primary Consumers"
    主要消費者是 [Schemas](../frontend/definition/schemas.md)、[Schema Editor](../frontend/definition/schema-editor.md)、[Schemdraw](../frontend/research-workflow/schemdraw.md) 與 [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md)。

---

## 涵蓋範圍 (Coverage)

| Surface | 說明 |
| :--- | :--- |
| **Definition Catalog List** | 定義目錄列表 |
| **Active Definition Detail** | 啟用中的定義詳情 |
| **CRUD Mutation** | 建立、更新、刪除操作 |
| **Validation** | 驗證通知與摘要 |
| **Output & Preview** | 正規化產出與預覽產物摘要 |

---

## Surface Contracts

=== "Catalog"

    catalog list 最低必須支援以下功能：

    | 功能 | 說明 |
    | :--- | :--- |
    | **搜尋** | 關鍵字查找 |
    | **排序** | 按日期、名稱或其他屬性排序 |
    | **分頁** | 大量資料的分段載入 |
    | **Metadata** | 僅包含 summary-safe 的元資料 |

=== "Detail"

    單一 definition detail 至少必須提供：

    | 類別 | 包含項目 |
    | :--- | :--- |
    | **Source** | canonical source text |
    | **Identity** | schema name |
    | **Validation** | validation notices, validation summary |
    | **Result** | normalized output, preview artifacts summary |

=== "Mutation"

    backend 必須支援標準的 CRUD 操作：

    1. **Create**: 建立新 definition
    2. **Update**: 更新既有 definition
    3. **Delete**: 刪除既有 definition

!!! warning "Catalog is Summary-only"
    definition catalog **不得**把完整 definition payload 當成列表回應的一部分。
    list path 只提供 `id`、`name`、`created_at` 與等價 summary 欄位。

!!! warning "Persisted Preview Authority"
    `validation notices`、`normalized output` 與 `preview artifacts` 只代表**最後一次成功儲存後**的 persisted state。
    backend 不得把未儲存的 editor draft 當成正式的 preview authority。

!!! tip "Persistence Sync"
    mutation 成功後，frontend 重新讀取 detail 時，必須能看到最新的 persisted inspection result。

!!! warning "Destructive Mutation"
    刪除 definition 是 **destructive mutation**。
    backend 應維持明確的成功 / 失敗回應，不得以靜默忽略取代。

---

## Delivery Rules

| 項目 | 規則 |
| :--- | :--- |
| **Source of Truth** | canonical source text 是唯一的寫入 authority。 |
| **Derived Preview** | normalized output 與 preview artifacts 是 read model，不可反向寫回 source。 |
| **Mutation Refresh** | create / update / delete 後，catalog 與 detail 都必須可重新讀回一致結果。 |
| **Reuse** | 同一 definition detail 必須可供 schema editor、schemdraw、circuit simulation 共用。 |

---

## Related

- [Schemas](../frontend/definition/schemas.md)
- [Schema Editor](../frontend/definition/schema-editor.md)
- [Schemdraw](../frontend/research-workflow/schemdraw.md)
- [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md)
- [Circuit Netlist](../../data-formats/circuit-netlist.md)
