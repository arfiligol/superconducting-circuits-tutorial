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
scope: /raw-data 頁面的 Dataset 清單、Data Record 預覽與大資料量互動契約
version: v0.3.0
last_updated: 2026-03-03
updated_by: docs-team
---

# Raw Data Browser

本頁定義 `/raw-data` 的正式 UI/UX 契約，重點是大資料量下的可用性與穩定性。

## Page Sections

1. `Dataset List`
2. `Dataset Preview`
3. `Visualization Preview`
4. `Dataset Metadata Summary (Read-only)`

!!! note "版面配置"
    `Dataset List` 與 `Dataset Preview` 採上下堆疊（全寬）而非左右分欄，
    以確保長名稱與大表格可完整顯示。

## Dataset List Contract

`Dataset List` 必須提供：

- 分頁（pagination）
- 欄位排序（sorting，透過點擊欄位標題）
- 文字過濾（filter/search）
- row click 選取 dataset

!!! tip "即時搜尋互動"
    搜尋可即時更新，但輸入期間不得重建輸入元件導致 focus 跳失。

!!! important "資料載入邊界"
    Dataset 列表查詢僅允許使用 summary 欄位（例如 `id`, `name`, `created_at`）。
    不可在列表查詢階段載入 DataRecord 的波形 payload。

## Dataset Preview Contract

選到某 dataset 後，`Dataset Preview` 的 Data Record table 必須提供：

- 分頁（pagination）
- 欄位排序（sorting，透過點擊欄位標題）
- 欄位過濾（至少包含 `data_type`, `representation`）
- row click 選取 record

!!! note "排序控制"
    若 table 欄位已可點擊排序，不應再額外放 `Sort By` / `Order` selector。

!!! warning "禁止全量 payload 預載"
    預覽表格只顯示 Data Record metadata（`id`, `data_type`, `parameter`, `representation`）。
    不可一次把 `axes` / `values` 全部送進前端。

## Dataset Metadata Summary Contract

!!! note "Current behavior（2026-03-04）"
    舊版 `/raw-data` 曾提供 metadata 編輯元件（`Device Type`、`Capabilities`、
    `Auto Suggest`、`Save Metadata`）。

!!! important "Contract（Dashboard-only edit entry）"
    `/raw-data` 不可再提供任何 metadata 寫入入口。  
    本頁僅可顯示 `source_meta.dataset_profile` 的 read-only summary。

!!! warning "禁止互動寫入"
    Raw Data Browser 不得出現 `Auto Suggest`、`Save Metadata` 或等價可寫入按鈕/表單。

## Visualization Preview Contract

- 只有當使用者在 Data Record table 點到某一列時，才讀取該筆詳細資料並繪圖。
- 切換 dataset 或切換資料頁時，不應自動重載所有圖資料。

!!! tip "Lazy Detail Fetch"
    將「列表」與「單筆詳細資料」拆成兩條查詢路徑：
    - List path: summary-only
    - Detail path: by record id

## Interaction Rules

- `Analyze This Dataset` 只依賴選中的 dataset id，不依賴 record 是否被選中。
- 若切換 dataset，應重置目前 selected record 狀態。
- 若 selected record 不在當前表格頁，應維持可預期狀態（保留或清空需一致，不可隨機）。
- Metadata 保存成功後，當前 session 應立即反映新 profile（不需重啟 app）。

!!! important "與 Characterization 的關係"
    Characterization analysis availability 會讀取 `source_meta.dataset_profile`。
    metadata 寫入需從 Dashboard 完成，Raw Data 僅負責顯示摘要狀態。

## Performance SLO (UI Layer)

- 單頁表格 rows 建議預設 `20`（可調整）。
- 單次 UI render 不應包含完整 multi-thousand record payload。
- UI 不應因為 DataRecord 總量增加而觸發 websocket 大訊息造成失連。
