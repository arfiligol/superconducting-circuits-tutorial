---
aliases:
  - "Raw Data Layout"
  - "原始數據結構"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "data/raw 目錄結構定義"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Raw Data Layout

`data/raw/` 目錄用於存放所有原始輸入數據。

## Structure

```
data/raw/
├── measurement/
│   └── flux_dependence/       # VNA 測量的 Flux Sweep (*.txt)
│
├── circuit_simulation/        # (保留給 Sonnet/HFSS Circuit)
│
└── layout_simulation/
    ├── admittance/            # HFSS Driven Modal Im(Y) (*.csv)
    └── phase/                 # HFSS Driven Modal S-param Phase (*.csv)
```

## Rules

1. **Read-Only**: 此目錄下的檔案視為不可變 (Immutable)。
2. **Naming Convention**: 建議檔名包含元件 ID 與掃描類型，例如 `LJPAL658_v1_Im_Y11.csv`。
3. **Source**: 所有數據應直接來自儀器或模擬軟體匯出。

## Path Helpers

請使用 `src/utils/paths.py` 中的常數來引用這些目錄：

- `RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR`
- `RAW_LAYOUT_ADMITTANCE_DIR`
- `RAW_LAYOUT_PHASE_DIR`

## Related

- [Preprocess Guide](../../how-to/preprocess/index.md) - 如何處理這些數據
- [Data Handling](../guardrails/data-handling.md) - 一般處理原則
- [Data Flow](../../explanation/architecture/pipeline/data-flow.md) - 數據流架構
