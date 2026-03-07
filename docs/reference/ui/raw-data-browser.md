---
aliases:
- Raw Data Browser UI
- 原始資料瀏覽介面
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /raw-data 頁面的 Design 清單、Trace 預覽與大資料量互動契約
version: v0.3.0
last_updated: 2026-03-08
updated_by: codex
---

# Raw Data Browser

本頁定義 `/raw-data` 的正式 UI/UX 契約，重點是大資料量下的可用性與穩定性。

## Page Sections

1. `Design List`
2. `Design Summary + Trace Preview`
3. `Visualization Preview`
4. `Design Summary (Read-only)`

!!! note "版面配置"
    `Design List` 與 `Design Summary + Trace Preview` 採上下堆疊（全寬）而非左右分欄，
    以確保長名稱與大表格可完整顯示。

## Design List Contract

`Design List` 必須提供：

- 分頁（pagination）
- 欄位排序（sorting，透過點擊欄位標題）
- 文字過濾（filter/search）
- row click 選取 design

!!! tip "即時搜尋互動"
    搜尋可即時更新，但輸入期間不得重建輸入元件導致 focus 跳失。

!!! important "資料載入邊界"
    Design 列表查詢僅允許使用 summary 欄位（例如 `id`, `name`, `created_at`）。
    不可在列表查詢階段載入 trace payload。

## Design Summary + Trace Preview Contract

選到某個 design 後，`Trace Preview` table 必須提供：

- 分頁（pagination）
- 欄位排序（sorting，透過點擊欄位標題）
- 欄位過濾（至少包含 `data_type`, `representation`）
- row click 選取 trace
- design-scope source context（至少包含 `source_kind`, `stage_kind`, `trace batch`）

!!! note "排序控制"
    若 table 欄位已可點擊排序，不應再額外放 `Sort By` / `Order` selector。

!!! warning "禁止全量 payload 預載"
    預覽表格只顯示 trace metadata（`id`, `data_type`, `parameter`, `representation`）。
    不可一次把 `axes` / `values` 全部送進前端。

!!! important "Cross-source browse contract"
    若同一個 `Design` 內同時存在 circuit / layout / measurement traces，
    本頁必須能清楚區分每筆 trace 屬於哪個 `source_kind`、哪個 `stage_kind`、
    以及哪個 `TraceBatchRecord` provenance boundary。
    這些欄位只能來自 trace-first / TraceBatch metadata path，
    不得靠 inline numeric payload 或 backend-specific store locator 拼湊。

## Design Summary Contract

!!! note "Current behavior（2026-03-04）"
    舊版 `/raw-data` 曾提供 metadata 編輯元件（`Device Type`、`Capabilities`、
    `Auto Suggest`、`Save Metadata`）。

!!! important "Contract（Dashboard-only edit entry）"
    `/raw-data` 不可再提供任何 metadata 寫入入口。
    本頁僅可顯示 design-level read-only summary；
    phase-2 相容層目前仍由 `source_meta.dataset_profile` 提供內容。

!!! warning "禁止互動寫入"
    Raw Data Browser 不得出現 `Auto Suggest`、`Save Metadata` 或等價可寫入按鈕/表單。

### Cross-source Workflow Summary

`Design Summary` 必須額外提供：

- `Current Design Scope`
- `Trace source summary`（每種 source 的 trace / batch 計數）
- `Latest provenance summary`（最近 batch 的來源與 stage）
- `Compare readiness`

!!! important "Compare readiness"
    compare readiness 必須用明確狀態呈現：
    - `Ready`：同 design scope 內至少有兩種 source traces 可供使用者區分與後續 compare
    - `Inspect only`：目前只有單一 source，或只有 provenance 可看但還不適合 compare
    - `Blocked`：目前缺少 trace-first compare 所需的最小條件

!!! warning "不可模糊隱藏"
    若 compare 尚未 fully expose，本頁必須顯示明確 empty-state / blocked-state，
    不可只是不顯示 cross-source 區塊。

## Visualization Preview Contract

- 只有當使用者在 Trace table 點到某一列時，才讀取該筆詳細資料並繪圖。
- 切換 design 或切換資料頁時，不應自動重載所有圖資料。

!!! tip "Lazy Detail Fetch"
    將「列表」與「單筆詳細資料」拆成兩條查詢路徑：
    - List path: summary-only
    - Detail path: by trace id

## Interaction Rules

- `Analyze This Design` 只依賴選中的 design id，不依賴 trace 是否被選中。
- 若切換 design，應重置目前 selected trace 狀態。
- 若 selected trace 不在當前表格頁，應維持可預期狀態（保留或清空需一致，不可隨機）。
- Metadata 保存成功後，當前 session 應立即反映新 profile（不需重啟 app）。

!!! important "與 Characterization 的關係"
    Characterization analysis availability 會讀取 design-level profile summary。
    metadata 寫入需從 Dashboard 完成，Raw Data 僅負責顯示摘要狀態。

!!! important "Compare authority"
    本頁顯示的 compare-ready / inspect-only 判斷只能依賴 design-scope trace metadata、
    `TraceBatchRecord` provenance、以及 trace-first compatibility。
    不可把 metadata DB 內的大型 numeric payload 或 point-per-record projection 當主要 authority。

## Performance SLO (UI Layer)

- 單頁表格 rows 建議預設 `20`（可調整）。
- 單次 UI render 不應包含完整 multi-thousand trace payload。
- UI 不應因為 trace 總量增加而觸發 websocket 大訊息造成失連。
