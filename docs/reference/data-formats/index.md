---
aliases:
- Data Formats Reference
- 數據格式參考
tags:
  - diataxis/reference
  - audience/team
status: stable
owner: docs-team
audience: team
scope: 數據格式規格，包括目錄結構與 Schema 定義
version: v1.4.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Data Formats

數據格式規格參考。

## Topics

- [Raw Data Layout](raw-data-layout.md) - `data/raw/` 目錄結構
- [Dataset Record](dataset-record.md) - `DatasetRecord` SQLite Schema (**推薦**)
- [Circuit Netlist](circuit-netlist.md) - `CircuitDefinition` 規格（value_ref、parameters、Sweep）
- [Analysis Result](analysis-result.md) - 分析結果 TypedDict 格式

## Related

- [Pipeline](../../explanation/architecture/pipeline/data-flow.md) - 理解數據流程
- [Data Handling](../guardrails/code-quality/data-handling.md) - 數據處理規範
