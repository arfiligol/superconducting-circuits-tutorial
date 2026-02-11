---
aliases:
  - "Ingest HFSS Data"
  - "匯入 HFSS 模擬數據"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/data-ingestion
status: stable
owner: team
audience: user
scope: "如何將 HFSS 匯出的 Admittance CSV 檔案匯入系統資料庫"
version: v1.1.1
last_updated: 2026-02-11
updated_by: team
---

# Ingesting HFSS Data

本指南說明如何將 HFSS 報表匯出的 Admittance (Y-parameter) `.csv` 數據匯入系統，以供後續分析使用。

!!! info "前置條件"
    - 您已在 HFSS 完成模擬，並建立 Admittance 報表（例如 Im(Y11) 對 Frequency）。
    - 您已將報表數據匯出為 `.csv` 檔案。
    - 檔案名稱將直接作為 Dataset Name（例如 `Design_A_Im_Y11.csv` -> Dataset: `Design_A_Im_Y11`）。

---

## 操作步驟

=== "CLI"

    先在 HFSS 匯出 `.csv`，再使用 `sc preprocess admittance` 進行匯入。

    ### 1. 在 HFSS 匯出 `.csv`

    以 Admittance 報表視窗為例：

    1. 建立或開啟 Admittance Report（例如 Im(Y11)）。
    2. 在報表視窗選擇 **Export** / **Export to File**。
    3. 檔案格式選擇 `.csv`，儲存到本機資料夾。

    ### 2. 匯入單一 `.csv` 檔案

    若您只需要分析特定的設計檔案：

    ```bash
    uv run sc preprocess admittance path/to/your/file.csv
    ```

    ### 3. 批量匯入資料夾中的 `.csv`

    若您有一系列的掃描數據，可以直接指定目錄，系統會自動處理所有支援的檔案：

    ```bash
    uv run sc preprocess admittance path/to/data_folder/
    ```

    !!! tip "重複匯入檢查"
        系統會自動檢查 Dataset Name。如果名稱已存在，預設會跳過以避免重複數據。
        若需強制更新，請先使用資料庫管理工具刪除舊資料（詳見 [Manage Database](../manage-db/index.md)）。

=== "UI (TBD)"

    !!! warning "開發中"
        圖形化介面尚在開發階段。

    1. 開啟 Dashboard，進入 **Data Ingestion** 頁面。
    2. 點擊 **Upload Files** 或直接將 `.csv` 檔案拖入上傳區。
    3. 確認列表中的檔案名稱與預覽資訊。
    4. 點擊 **Import** 按鈕開始處理。

---

## 驗證結果

匯入完成後，請確認資料是否正確建立：

```bash
uv run sc db dataset-record list
```
