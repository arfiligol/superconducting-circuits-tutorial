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
scope: Design/Trace/TraceBatch metadata schema、TraceStore contract、analysis output 的資料格式契約
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Data Formats

本章是新的資料格式 SoT，主軸為：

- `DesignRecord` 是設計層 container
- `TraceRecord` 是可分析的標準 trace 單位
- `TraceBatchRecord` 是 setup / provenance / lineage 邊界
- `TraceStore`（Zarr）保存大型 ND numeric payload

!!! important "Design baseline (2026-03-08)"
    - Characterization 的輸入一律是相容的 S/Y/Z matrix traces。
    - `layout_simulation` / `circuit_simulation` / `measurement` 只是來源不同。
    - metadata DB 與 numeric TraceStore 必須分離。
    - canonical trace 可為 1D / 2D / ND；sweep point 不是唯一 canonical record 單位。

## Topics

| Topic | 說明 |
|---|---|
| [Design / Trace Schema](dataset-record.md) | `DesignRecord`、`TraceRecord`、`TraceBatchRecord`、`TraceStoreRef` |
| [Circuit Netlist](circuit-netlist.md) | Circuit Definition source / expanded contract |
| [Raw Data Layout](raw-data-layout.md) | raw source 與 ingest / import 邊界 |
| [Analysis Result](analysis-result.md) | `AnalysisRunRecord` / `DerivedParameter` 相關契約 |
| [Query Indexing Strategy](query-indexing-strategy.md) | metadata DB 查詢與 TraceStore slice-read 效能策略 |

## Quick Lookup

| 你想確認什麼？ | 先看哪頁 |
|---|---|
| 一個 design 可以同時有 circuit / layout / measurement 嗎？ | [Design / Trace Schema](dataset-record.md) |
| sweep trace 是存成 ND 還是每點一筆？ | [Design / Trace Schema](dataset-record.md) |
| 大型 trace values 存在哪裡？ | [Design / Trace Schema](dataset-record.md) + [Data Storage](../../explanation/architecture/data-storage.md) |
| local 與 S3/MinIO backend 如何共存？ | [Design / Trace Schema](dataset-record.md) + [Data Storage](../../explanation/architecture/data-storage.md) |
| Circuit Definition 在這套架構裡扮演什麼角色？ | [Circuit Netlist](circuit-netlist.md) |
| Query / indexing 該先優化 DB 還是 TraceStore？ | [Query Indexing Strategy](query-indexing-strategy.md) |

## Current Implementation Direction (2026-03-08)

!!! note "Docs first"
    本章定義的是 target architecture direction。
    實作接下來應依此收斂，而不是在舊 `Dataset/DataRecord/ResultBundle` 名稱上持續疊 patch。

## Related

- [Data Storage](../../explanation/architecture/data-storage.md)
- [Project Overview Guardrail](../guardrails/project-basics/project-overview.md)
- [Data Handling Guardrail](../guardrails/code-quality/data-handling.md)
