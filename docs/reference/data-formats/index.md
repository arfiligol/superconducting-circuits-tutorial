---
aliases:
  - Data Formats Reference
  - 數據格式參考
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: Raw ingest、SQLite persistence、analysis output 的資料格式契約
version: v1.7.0
last_updated: 2026-03-06
updated_by: codex
---

# Data Formats

本章是資料格式的 Reference SoT，涵蓋：

- 原始輸入目錄 (`data/raw/`)
- SQLite 持久化模型（Dataset/DataRecord/ResultBundle/DerivedParameter）
- 分析輸出與 Result View 讀取契約

!!! important "設計主軸（2026-03-04）"
    - Analysis 的資料可用性以 **Trace（DataRecord）** 為主，不以 Dataset 名稱或單一 profile 決定。
    - `dataset_profile` 是 Dataset 層級的**摘要與建議**，不是唯一的可執行依據。
    - Result 顯示與重用由 `ResultBundleRecord` 提供 provenance 與 identity。

## Topics

| Topic | 說明 |
|---|---|
| [Raw Data Layout](raw-data-layout.md) | `data/raw/` 的來源目錄契約與 ingest 邊界 |
| [Dataset Record](dataset-record.md) | SQLite 主模型、`dataset_profile`、Trace Index 契約 |
| [Circuit Netlist](circuit-netlist.md) | Circuit Netlist Source/Expanded 契約與 repeat 展開 |
| [Analysis Result](analysis-result.md) | `ResultBundleRecord`、`analysis_result` DataRecord、DerivedParameter 契約 |
| [Query Indexing Strategy](query-indexing-strategy.md) | 高頻查詢路徑、索引候選與效能監控建議 |

## 問題導覽（先看這裡）

| 你想確認什麼？ | 先看哪頁 |
|---|---|
| Circuit Definition 到底是 components-first 還是 parameters-first？ | [Circuit Netlist](circuit-netlist.md) |
| Simulation sweep（含多軸）結果實際存在哪裡？ | [Dataset Record](dataset-record.md) |
| Sweep target 到底可以掃哪些欄位（netlist parameter vs source bias）？ | [Circuit Netlist](circuit-netlist.md) + [Circuit Simulation UI](../ui/circuit-simulation.md) |
| Characterization run 的 provenance / selected traces 存在哪裡？ | [Analysis Result](analysis-result.md) |
| 為什麼 UI 顯示可執行但 run 仍需選 trace？ | [Analysis Result](analysis-result.md) + [Dataset Record](dataset-record.md) |
| 增加 sweep 後，是否必須同時改 Characterization？ | [Dataset Record](dataset-record.md) + [Analysis Result](analysis-result.md) |
| 大資料時應該看哪個查詢契約與索引策略？ | [Query Indexing Strategy](query-indexing-strategy.md) |

## 實作對齊狀態（2026-03-04）

!!! note "目前狀態"
    Characterization Run Analysis 目前採「混合 gating」：
    1. Dataset profile capability gating
    2. Trace compatibility 檢查（data_type / parameter / representation）
    3. 使用者選取 trace IDs
    實際執行仍需有相容且被選取的 traces。

!!! warning "文件與程式碼同步策略"
    本章已將 Trace-first 定義為資料契約方向；當 capability hard-block 移除後，
    請同步更新 [Characterization UI Reference](../ui/characterization.md) 的 availability 描述。

## Related

- [Pipeline Data Flow](../../explanation/architecture/pipeline/data-flow.md)
- [Characterization UI](../ui/characterization.md)
- [Data Handling Guardrail](../guardrails/code-quality/data-handling.md)
