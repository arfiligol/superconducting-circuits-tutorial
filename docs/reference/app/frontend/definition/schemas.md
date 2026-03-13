---
title: "Schemas"
aliases:
  - "Schemas UI"
  - "Circuit Schemas UI"
  - "電路綱要清單介面"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/ui
page_id: app.page.schemas
route: /schemas
status: draft
owner: docs-team
audience: team
scope: "/schemas 頁面的 circuit schema catalog、搜尋/排序/分頁，以及建立/開啟/刪除契約"
version: v0.4.0
last_updated: 2026-03-13
updated_by: team
---

# Schemas

本頁定義 Circuit Schema catalog 的瀏覽、搜尋、排序、建立、開啟與刪除契約。

!!! info "Page Frame"
    本頁負責 schema catalog、搜尋 / 排序 / 分頁、建立、刪除與開啟 editor。
    source 編輯、preview render 與 simulation execution 不屬於本頁責任。

---

## 使用者目標 (User Goals)

*   **高效檢索**: 在數以百計的 Schema 中快速定位目標。
*   **版本確認**: 根據建立時間或名稱確認最新的開發進度。
*   **便捷管理**: 快速啟動新專案 (New Circuit) 或清理廢棄的電路定義。
*   **流暢對接**: 從清單無縫導向至 `Schema Editor` 或 `Circuit Simulation`。

---

## UI 配置與 組件說明

### 佈局結構 (Layout Structure)

```mermaid
graph LR
    H[Page Header] --> Actions[Primary Actions]
    Actions --> Filters[Search & Sort Bars]
    Filters --> List[Schema List Container]
    List --> Paging[Pagination & Status]
```

### 關鍵組件清單 (Components)

| ID | 組件 | 功能描述 | 關鍵行為 |
| :--- | :--- | :--- | :--- |
| **C1** | New Circuit Button | 位於頂部，為主要行動按鈕。 | 導向至 Schema 建立流程。 |
| **C2** | Filter Bar | 提供名稱搜尋、欄位排序與方向選擇。 | 觸發列表重新查詢。 |
| **C3** | Schema Item Row | 列表核心，顯示 `name`, `created_at`。 | 支援開啟、編輯與刪除。 |
| **C4** | Pagination | 位於底部，控制頁碼與筆數。 | 驅動分段載入，同步更新總數。 |

---

## 資料與狀態契約 (Contract)

=== "數據依賴 (Data Dependencies)"
    | 資料 | 來源 | 必要性 | 用途 |
    | :--- | :--- | :---: | :--- |
    | schema summary list | definition summary service | ✅ | 渲染各列摘要。 |
    | total items count | definition summary service | ✅ | 計算分頁與顯示總筆數。 |
    | search & sort params | UI State | ✅ | 控制過濾與排序行為。 |

=== "頁面狀態 (States)"
    | 狀態 | 說明 |
    | :--- | :--- |
    | `Default` | 正常顯示清單與控制項。 |
    | `Loading` | 資料更新中，列表顯示載入遮罩。 |
    | `Empty` | 查無資料 (或搜尋後無結果)，顯示對應提示。 |
    | `Error` | 服務請求失敗，於列表區塊顯示錯誤資訊。 |

!!! warning "邊界約束"
    Schema Catalog **禁止**在列表階段預載完整的 Definition Payload。其詳細內容應僅在 Editor 或 Detail 流中按需讀取。

---

## 互動流程 (Interaction Flow)

=== "建立與開啟 (Create/Open)"
    1.  點擊 `New Circuit` → 導向 Editor 建立新檔。
    2.  點擊 `Edit` 或 Row → 導向 Editor 並帶入選定 `schema_id`。

=== "搜尋與排序 (Search/Sort)"
    1.  更新搜尋框或排序選項。
    2.  重置 `current_page = 1`。
    3.  根據新條件刷新列表視圖。

=== "刪除流程 (Delete)"
    1.  點擊 `Delete` → 觸發二次確認視窗。
    2.  成功刪除後，刷新列表並進行頁碼校正 (如有必要)。

---

## 視覺規範 (Visual Rules)

*   **層次分明**: Page Title 的視覺比重必須顯著高於 Subtitle。
*   **CTA 定位**: `New Circuit` 按鈕應始終位於主要內容區的最上方。
*   **密度一致**: 無論使用 Table 或 Card，`Created At` 與 Action 按鈕在每列中需維持穩定對齊。
*   **反饋定位**: Error 或 Mutation Feedback 應在列表區域附近清晰可見。

---

## 相關參考

*   [Schema Editor](schema-editor.md)
*   [Circuit Simulation](../research-workflow/circuit-simulation.md)
*   [Backend: Circuit Definitions](../../backend/circuit-definitions.md)
*   [Record Format: Circuit Netlist](../../data-formats/circuit-netlist.md)
