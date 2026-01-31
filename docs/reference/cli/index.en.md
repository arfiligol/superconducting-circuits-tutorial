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
last_updated: 2026-01-28
updated_by: docs-team
---

# CLI Reference

Command-line tool reference.

## Preprocessing (Data Ingestion)

- [sc preprocess admittance](sc-preprocess-admittance.en.md) - Convert HFSS admittance data
- [sc preprocess phase](sc-preprocess-phase.en.md) - Convert HFSS phase data
- [sc preprocess flux](sc-convert-flux-dependence.en.md) - Convert VNA flux dependence data

## Analysis (Data Fitting)

- [sc analysis fit](sc-fit-squid.en.md) - SQUID LC Model Fit
- [flux-dependence-plot](flux-dependence-plot.en.md) - Flux dependence heatmap (Todo: integrate into `sc analysis`)

## Database

- [sc db](sc-db.en.md) - Dataset management
- [sc db dataset-record](sc-db-dataset-record.en.md) - DatasetRecord CRUD
- [sc db data-record](sc-db-data-record.en.md) - DataRecord CRUD
- [sc db derived-parameter](sc-db-derived-parameter.en.md) - DerivedParameter CRUD
- [sc db tag](sc-db-tag.en.md) - Tag CRUD

## Related

- [How-to Guides](../../how-to/index.md) - Task-oriented guides
