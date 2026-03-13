---
title: "Characterization"
aliases:
  - "Characterization UI"
  - "特徵分析介面"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/ui
page_id: app.page.characterization
route: /characterization
status: draft
owner: docs-team
audience: team
scope: "/characterization 的 design scope、run analysis、attached task、run history、result view 與 identify mode 契約"
version: v0.13.0
last_updated: 2026-03-14
updated_by: team
---

# Characterization

本頁定義 design-scoped characterization workflow 的 analysis selection、trace selection、attached task、run history、result view 與 identify mode 契約。

!!! info "Page Frame"
    本頁負責 design scope、compatible traces、analysis run、persisted result inspection 與 identify / tagging。
    raw data ingest、schema editing 與 simulation execution 不屬於本頁責任。

!!! info "Analysis Path"
    本頁遵循嚴格線性邏輯：
    `選擇 Design` → `選取相容 Traces` → `執行分析` → `附加 Task` → `檢閱持久化結果`。

!!! tip "Shared Surfaces"
    本頁使用 shared [Header](../shared-shell/header.md)、[Sidebar](../shared-shell/sidebar.md) 與 [Task Management](../shared-workflow/task-management.md)。
    `Tasks Queue` 與 worker status 由 Header 提供；`Run History` 是 characterization-specific artifact surface，不取代 shared task queue / attach semantics。

## 核心職責

=== "配置與執行"
    * **範圍定義**: 選擇一個 Design 並檢視其 Source Coverage。
    * **分析選擇**: 選擇 Analysis 類型並確認與當前 Traces 的相容性。
    * **任務提交**: 選取多筆 Traces 並啟動 Characterization Run。

=== "結果與標記"
    * **歷史追蹤**: 檢視過往執行紀錄 (Run History) 與附加 task log。
    * **多維檢視**: 透過 Table 或 Plot 檢視 Result Artifacts。
    * **參數標記**: 進入 Identify Mode，將分析結果標記回系統核心度量。

## UI 佈局與工作流

```mermaid
graph LR
    Header[Header: Active Dataset + Tasks Queue + Worker Status] --> Design[1. Design Selector]
    Design --> Traces[2. Trace Selection]
    Traces --> Run[3. Run Analysis]
    Run --> Attached[4. Attached Task & Log]
    Attached --> History[5. Run History]
    History --> Result[6. Result View]
    Result --> Tag[7. Identify & Tag]
```

## 關鍵組件清單

| ID | 組件名稱 | 作用 |
| :--- | :--- | :--- |
| **C1** | Design Selector | 決定分析資料邊界與相容性檢查基準。 |
| **C2** | Analysis Selector | 選擇演算法類型並顯示 `Recommended / Available / Unavailable`。 |
| **C3** | Trace Selection Table | 展示 compatible traces，支援 `All / Base / Clear` 操作。 |
| **C4** | Attached Task & Log | 顯示目前附加 task 的 lifecycle 與 log。 |
| **C5** | Run History | 展示 persisted analysis runs。 |
| **C6** | Result View Controls | 切換結果類別與 artifact 頁籤。 |
| **C7** | Identify & Tag | 自動提取參數並執行 tagging 提交。 |

## 狀態與相容性契約

=== "分析可用性"
    | 狀態 | 定義 |
    | :--- | :--- |
    | **Recommended** | 偵測到相容 Traces，且符合 profile 建議。 |
    | **Available** | 具備基礎執行條件。 |
    | **Unavailable** | 當前 Design 範圍內無相容數據。 |

=== "Trace 模式"
    * **Base**: 基礎掃描數據。
    * **Sideband**: 側帶或輔助測量數據。
    * **All**: 包含所有已索引 Trace 種類。

!!! tip "Profile 只做提示"
    Design Profile 僅作為推薦參考。
    analysis 是否可執行的最終判定權在於 compatible traces 的存在與否。

## 數據持續性與運行時規則

* **Task Attachment**: Run 啟動後，Header queue 必須立即出現該 task，且頁面自動附加到對應任務並顯示日誌。
* **Result Persistence**: 結果檢閱僅依賴持久化 artifacts，刷新頁面後必須能精確還原視圖。
* **非重複計算**: 切換 Table / Plot 或類別時，僅改變呈現方式，不重跑分析。

!!! warning "Run History 不是 Queue"
    使用者若要重新附著到正在執行或剛完成的 task，應從 Header `Tasks Queue` 進入。
    `Run History` 只負責回看 persisted analysis artifacts。

## 相關參考

* [Raw Data Browser](../workspace/raw-data-browser.md)
* [Header](../shared-shell/header.md)
* [Sidebar](../shared-shell/sidebar.md)
* [Task Management](../shared-workflow/task-management.md)
* [Backend: Tasks & Execution](../../backend/tasks-execution.md)
* [Backend: Characterization Results](../../backend/characterization-results.md)
* [Data Format: Analysis Result](../../../data-formats/analysis-result.md)
