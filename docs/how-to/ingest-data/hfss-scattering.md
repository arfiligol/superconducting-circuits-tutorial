---
aliases:
  - "Ingest HFSS Scattering"
  - "匯入 HFSS 散射參數數據"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/data-ingestion
status: stable
owner: team
audience: user
scope: "如何將 HFSS 匯出的 S-Parameter (Scattering) CSV 檔案匯入系統資料庫"
version: v1.1.2
last_updated: 2026-02-23
updated_by: team
---

# Ingesting HFSS Scattering Data

本指南說明如何將 HFSS 中取得的 S-parameter (Scattering Matrix) `.csv` 數據匯入系統。支援 **實部 (Re)**、**虛部 (Im)**、與 **相位 (Phase)** 三種表示法，以供後續（例如共振頻率 Fitting）使用。適用於 **Driven Modal** 模擬數據。

!!! info "前置條件"
    - 您已在 HFSS 完成模擬，並建立 Phase Plot（例如 ang_rad(S21) 或 cang_deg(S11) 等）。
    - 您已從 Plot 匯出資料為 `.csv` 檔案。
    - **檔名必須包含 S 參數種類**（例如 `PF6FQ_Q1_Readout_ang_rad_S21.csv` 會自動辨識為 S21）。

---

## 自動過濾與單位處理機制

為了確保後續科學計算的便利性，系統對於 Phase 檔案有以下底層處理原則：

1. **統一儲存為 Radians (弧度)**：系統會自動掃描檔案。如果您的檔案或檔名包含 `deg`（Degree），系統會在寫入資料庫前**自動將數值轉換成 Radians**。如果是 `rad`，則保持原數值存入。
2. **區分 Wrapped 與 Unwrapped**：
    - 若檔名或欄位中包含 `cang` (Continuous Angle)，系統會將資料庫中 `representation` 標記為 `unwrapped_phase`。
    - 若僅包含 `ang` (或 `phase`)，則將 `representation` 標記為 `phase` (預設限制在 $[-\pi, \pi]$ 區間)。

> 在使用系統時，您**只需要匯入一種即可**，不必為了不同單位匯出多份。未來於分析模組如果需要，程式隨時能動態轉換單位或 Unwrap。

---

## 操作步驟

=== "CLI"

    使用 `sc preprocess hfss scattering` 進行匯入。

    ### 1. 匯入單一 `.csv` 檔案

    ```bash
    uv run sc preprocess hfss scattering path/to/your/phase_file.csv
    ```

    ### 2. 批量匯入資料夾中的 `.csv`

    若您有一系列的相位掃描數據，可以直接指定目錄：

    ```bash
    uv run sc preprocess hfss scattering path/to/data_folder/
    ```

    !!! tip "自動過濾機制與重複檢查"
        - 目錄模式下，系統預設只會抓取檔名符合散射參數或相角特徵（例如 `Phase`、`S21`、`deg`、`rad`、`re`、`im`、`mag` 等）的 `.csv` 檔案。您也可以透過 `--match` 選項來自訂過濾關鍵字。
        - 系統會透過檔名自動推斷 Dataset Name。如果該 Dataset 已存在資料庫，預設會跳過以避免重複數據。

=== "UI (TBD)"

    !!! warning "開發中"
        圖形化介面資料匯入尚在開發階段。

---

## 驗證結果

匯入完成後，請確認資料是否正確建立：

```bash
uv run sc db data-record list
```
應該要能在表格看見新增的資料，且其 `Type` 為 `s_parameters`，`Rep` 為 `phase` 或 `unwrapped_phase`。
