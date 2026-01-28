---
aliases:
- Data Flow
- 數據流程
tags:
  - diataxis/explanation
  - status/stable
  - topic/architecture
  - topic/pipeline
  - audience/team
status: stable
owner: docs-team
audience: team
scope: 分析管線的數據流程：Raw -> Dataset -> Analyzed
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Data Flow

本專案採用三階段的數據處理流程，確保數據的一致性與可追溯性。

<div align="center">

```mermaid
flowchart TB
    Raw["Raw Data\n(CSV/TXT)"] -->|Convert / Ingest| Pre["Dataset\n(SQLite)"]
    Pre -->|Analyze| Result["Analysis Result\n(Dict/Table)"]
    Result -->|Visualize| Report["Report\n(HTML/PNG)"]
```

</div>

## 1. Raw Data (`data/raw/`)

**來源**：ANSYS HFSS 匯出、VNA 測量數據。

**格式**：CSV, TXT。

**特性**：

- **唯讀 (Read-Only)**：永遠不修改原始檔案。
- **格式混亂**：不同機器、不同版本軟體匯出的格式差異大。
- **非結構化**：缺乏 metadata（如 Dataset 名稱、掃描參數）。

## 2. Dataset (`data/database.db`)

**來源**：由 `convert-*`/匯入流程從 Raw 轉換而來。

**格式**：SQLite（Dataset / DataRecord 等結構）。

**特性**：

- **標準化**：不論來源是 HFSS 還是量測，都轉成一致的資料表結構。
- **自包含**：包含所有必要 metadata（Bias 軸、頻率軸、單位）。
- **Source of Truth**：後續分析（擬合、繪圖）以資料庫為準，不再回頭讀取 Raw。

## 3. Analysis Reports (`data/processed/reports/`)

**來源**：由 `squid-model-fit` 等分析腳本生成。

**格式**：

- 控制台輸出 (Table)
- 視覺化圖表 (HTML/PNG)
- 分析參數 (JSON)

**特性**：

- **可重現**：只要 Dataset 不變，分析結果應一致。
- **決策依據**：提供最終的物理參數 ($L_s, C$) 供設計參考。

## Related

- [Raw Data Layout](../../../reference/data-formats/raw-data-layout.md) - 目錄結構
- [Preprocessing Rationale](preprocessing-rationale.md) - 為什麼需要中間層
