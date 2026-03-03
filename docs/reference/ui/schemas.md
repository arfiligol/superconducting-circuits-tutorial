---
aliases:
- Schemas UI
- Circuit Schemas UI
- 電路綱要清單介面
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /schemas 頁面的清單顯示、搜尋/排序/分頁，以及大清單互動契約
version: v0.2.0
last_updated: 2026-03-03
updated_by: docs-team
---

# Schemas

本頁定義 `/schemas` 的正式 UI/UX 契約。

## Page Sections

1. `Header Actions`（含 `New Circuit`）
2. `Schema List`

## Schema List Contract

`Schema List` 必須提供：

- 搜尋（search by schema name）
- 排序（sorting，至少 `name`, `created_at`）
- 分頁（pagination）
- 每筆 schema 的 `Edit` / `Delete` 操作

!!! note "呈現型態"
    可使用 table 或 card list。
    若使用 card list，仍必須具備與 table 等效的搜尋/排序/分頁能力。

!!! important "Card List 密度與對齊"
    當採 card list 時，預設為一列一個全寬 card。
    每列需維持 table-like 對齊：名稱區、`Created` 區與右側 `Edit/Delete` 操作區需在所有列保持一致對齊。

!!! tip "搜尋輸入體驗"
    搜尋可即時更新，但不可因為列表重繪而讓輸入框失去焦點。

## Data Loading Boundary

Schema 列表查詢只應讀取 summary 欄位（例如 `id`, `name`, `created_at`）。

!!! warning "禁止在清單頁預載 definition payload"
    `definition_json` 屬於大欄位，只能在進入 `/schemas/{id}` 或執行需要時再讀取。

## Delete Action Contract

- `Delete` 必須有明確動作回饋（success/failure notify）
- 刪除成功後刷新當前頁資料
- 若刪除後當前分頁超出範圍，應回退到最後一個有效頁

## Performance SLO (UI Layer)

- 預設 page size 建議 `12`（card）或 `20`（table）
- 每次換頁僅渲染當前頁資料
- 大量 schema（數百筆以上）仍需維持可操作，不可因一次性渲染全量卡片造成明顯卡頓
