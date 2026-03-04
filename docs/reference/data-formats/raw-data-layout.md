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
scope: data/raw Project-first 來源目錄結構與 ingest 自動分類邊界
version: v0.3.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Raw Data Layout

`data/raw/` 用於存放外部來源的原始檔案（量測與外部模擬輸出）。  
Raw layout 以 **Project Folder** 為主，不要求使用者先按 phase/admittance 拆子資料夾。

## 目錄結構（Project-first）

```text
data/raw/
└── <project_name>/
    ├── *.csv
    ├── *.txt
    └── ...
```

範例：

```text
data/raw/
└── PF6FQ_Q0/
    ├── PF6FQ_Q0_XY_Im_Y11.csv
    ├── PF6FQ_Q0_Readout_ang_rad_S21.csv
    └── PF6FQ_Q0_flux_sweep.txt
```

## 自動分類與 preprocess 決策

CLI / UI ingest 可依檔名與欄位內容進行分類與路徑決策：

| 規則類型 | 說明 |
|---|---|
| 檔名語意 | 例如 `Y11`, `S21`, `Re_`, `Im_`, `ang`, `cang`, `deg`, `rad` |
| 表示法推斷 | phase / unwrapped_phase / real / imaginary / magnitude |
| 跳過策略 | 對不匹配目標處理器的檔案可跳過，不強制失敗 |

!!! important "不再要求 phase/admittance 目錄分拆"
    文件契約不再要求 `admittance/`、`phase/` 這類手動分類資料夾。  
    類型判斷由 ingest 階段自動完成。

!!! note "Raw 與 Trace 的分工"
    `data/raw/` 只保存來源檔。  
    Analysis 讀取的是 ingest 後的 `DataRecord` traces（SQLite）。

## 規則

1. **Immutable by default**：匯入後原始檔視為只讀，不覆寫。
2. **Project-first**：先以專案彙整資料，再由 ingest 進行分類。
3. **Filename 可判讀**：建議保留參數/表示法/單位資訊於檔名。
4. **來源完整性**：raw 檔應保持與儀器/solver 匯出一致，不做人工重排。

## 與 DatasetRecord 的關係

- `DatasetRecord.source_meta.raw_file` / `raw_files` 可指向 raw 檔來源。
- ingest 後會產生 `DataRecord` 並建立 Trace Index（供 Characterization / Simulation Result 使用）。
- `dataset_profile` 是 Dataset 摘要，不取代 trace-level 相容性判斷。

## Related

- [Dataset Record](dataset-record.md)
- [Analysis Result](analysis-result.md)
- [Pipeline Data Flow](../../explanation/architecture/pipeline/data-flow.md)
