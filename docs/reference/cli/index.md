---
aliases:
- CLI Reference
- CLI 指令參考
tags:
- audience/team
status: draft
owner: docs-team
audience: team
scope: 命令列工具參考，所有 CLI 指令與參數
version: v0.1.0
last_updated: 2026-02-11
updated_by: docs-team
---

# CLI Reference

命令列工具參考。

## Preprocessing (Data Ingestion)

- [sc preprocess admittance](sc-preprocess-admittance.md) - 轉換 HFSS 虛阻納數據
- [sc preprocess phase](sc-preprocess-phase.md) - 轉換 HFSS 相位數據
- [sc preprocess flux](sc-convert-flux-dependence.md) - 轉換 VNA 磁通依賴數據

## Analysis (Data Fitting)

- [sc analysis fit](sc-fit-squid.md) - SQUID 模型擬合

## Plotting

- [sc plot admittance](plot-admittance.md) - 觀察 Im(Y) 線圖，檢查共振點品質
- [sc plot flux-dependence](flux-dependence-plot.md) - 磁通掃描熱圖與切片視覺化
- [sc plot different-qubit-structure-frequency-comparison-table](sc-plot-resonance-map.md) - Qubit Structure Resonance Frequency 二維圖/表

## Database

- [sc db](sc-db.md) - Dataset 管理
- [sc db dataset-record](sc-db-dataset-record.md) - DatasetRecord CRUD
- [sc db data-record](sc-db-data-record.md) - DataRecord CRUD
- [sc db derived-parameter](sc-db-derived-parameter.md) - DerivedParameter CRUD
- [sc db tag](sc-db-tag.md) - Tag CRUD

## Related

- [How-to Guides](../../how-to/index.md) - 操作指南
