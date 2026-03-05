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
version: v1.5.0
last_updated: 2026-03-04
updated_by: docs-team
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
