---
aliases:
  - "Preprocess HFSS Admittance"
  - "HFSS 虛阻納處理"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "如何處理 HFSS 匯出的 Admittance CSV"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Preprocess HFSS Admittance

本指南說明如何將 HFSS 匯出的 Im(Y) CSV 數據轉換為分析用的 JSON。

## Prerequisites

- 原始 CSV 檔案已放置於 `data/raw/admittance/` (建議位置)。
- CSV 應包含 Frequency 與不同 $L_{jun}$ 變數的欄位。

## Steps

1. **確認檔案路徑**
   ```bash
   ls data/raw/admittance/MyChip_Im_Y11.csv
   ```

2. **執行轉換**
   使用 `convert-hfss-admittance` 指令：
   ```bash
   uv run convert-hfss-admittance data/raw/admittance/MyChip_Im_Y11.csv
   ```

3. **檢查輸出**
   轉換後的檔案會位於 `data/preprocessed/`，檔名通常與 CSV 相同但副檔名為 `.json`。
   ```bash
   ls -l data/preprocessed/
   ```

4. **(Optional) 指定 Component ID**
   如果你希望 JSON 檔名更乾淨：
   ```bash
   uv run convert-hfss-admittance \
       --component-id "LJPAL658_v1" \
       data/raw/admittance/MyChip_Im_Y11.csv
   ```
   這會生成 `data/preprocessed/LJPAL658_v1.json`。

## Next Steps

- [[../analysis/admittance-fit.md|Run Admittance Fit]] - 執行擬合分析
