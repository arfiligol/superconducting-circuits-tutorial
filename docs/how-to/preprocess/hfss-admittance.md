---
aliases:
- Preprocess HFSS Admittance
- HFSS 虛阻納處理
tags:
- audience/team
- diataxis/how-to
- topic/preprocess
status: stable
owner: docs-team
audience: team
scope: 如何處理 HFSS 匯出的 Admittance CSV
version: v0.2.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Preprocess HFSS Admittance

本指南說明如何將 HFSS 匯出的 Im(Y) CSV 數據轉換為分析用的 JSON 或直接匯入 SQLite 資料庫。

## Prerequisites

- 原始 CSV 檔案已放置於 `data/raw/layout_simulation/admittance/`。
- CSV 應包含 Frequency 與不同 $L_{jun}$ 變數的欄位。

## Steps (Database Only)

1. **確認檔案路徑**
   ```bash
   ls data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
   ```

2. **執行資料庫匯入**
   使用 `sc-preprocess-admittance` 指令 (預設匯入至 `data/database.db`)：
   ```bash
   uv run sc-preprocess-admittance data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
   ```

3. **(Optional) 指定 Component ID 與 Tags**
   ```bash
   uv run sc-preprocess-admittance \
       --component-id "LJPAL658_v1" \
       --tags "chip/PF6FQ,experiment/2026Q1" \
       data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
   ```

4. **驗證匯入結果**
   使用 `sc-list-datasets` 檢查：
   ```bash
   uv run sc-list-datasets
   ```

## Next Steps

- [Run Admittance Fit](../analysis/admittance-fit.md) - 執行擬合分析
