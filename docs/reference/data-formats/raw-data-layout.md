---
aliases:
  - Raw Data Layout
  - 原始數據結構
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: raw source layout 與 Design/Trace ingest 邊界
version: v1.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Raw Data Layout

`data/raw/` 只保存外部來源檔案。  
它不是 UI/Characterization 的直接讀取格式；trace-first 流程的正式輸入必須是 ingest 後的 `TraceRecord`。

## Source Categories

```text
data/raw/
├── measurement/
├── layout_simulation/
└── imported/
```

!!! note "Circuit simulation is not a raw-file source"
    `circuit_simulation` 通常由應用內部產生 `TraceBatchRecord + TraceRecord + TraceStore payload`，
    而不是先落到 `data/raw/` 再二次 ingest。

## Project-first / Design-first layout

建議以 design/project 為主做外部來源彙整：

```text
data/raw/
└── <design_name>/
    ├── layout/
    │   ├── *.csv
    │   └── *.txt
    └── measurement/
        ├── *.csv
        └── *.s2p
```

## Ingest Boundary

ingest/import 完成後應產生：

1. `DesignRecord`
2. `DesignAssetRecord`
3. `TraceBatchRecord`
4. `TraceRecord`
5. `TraceStore` numeric payload

!!! important "Raw file is provenance, not the working trace authority"
    raw 檔負責保留來源完整性；
    plotting / Characterization / compare 不應直接依賴 raw file parser 在 UI 當場重讀。
    ingest 後的 `TraceRecord` 應以輕量 metadata + `store_ref` 指向 `TraceStore`；
    selection 走 metadata，真正需要 numeric payload 時再 materialize。

### Layout HFSS ingest contract

- layout CSV preprocess 完成後，必須先 materialize 成 canonical ND `TraceRecord`
- `TraceRecord.axes` 在 metadata DB 只保留 `name/unit/length`
- `TraceRecord.store_ref` 指向正式 numeric authority
- frequency / bias axis arrays 與 trace values 都必須寫進 `TraceStore`
- `TraceBatchRecord(source_kind=layout_simulation, stage_kind=raw)` 負責保留 import provenance / setup summary
- 不得再把 layout numeric matrix 主要存回 metadata DB JSON 作為 working SoT

## Related

- [Design / Trace Schema](dataset-record.md)
- [Data Storage](../../explanation/architecture/data-storage.md)
