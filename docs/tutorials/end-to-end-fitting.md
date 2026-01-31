---
aliases:
  - "End-to-End SQUID Fitting"
  - "完整流程教學：SQUID 擬合"
tags:
  - diataxis/tutorial
  - audience/user
  - sot/true
  - topic/analysis
status: stable
owner: team
audience: user
scope: "從 HFSS 模擬數據匯出到 SQUID 參數擬合的完整流程教學"
version: v1.0.0
last_updated: 2026-01-31
updated_by: team
---

# End-to-End SQUID Fitting

本教學將引導您完成從 **HFSS 模擬數據匯出** 到 **SQUID 參數擬合 (LC Model)** 的完整流程。

??? abstract "您將學會..."
    1.  如何準備 HFSS 匯出的 Touchstone 檔案
    2.  將數據匯入系統資料庫 (`sc preprocess`)
    3.  驗證資料完整性 (`sc db dataset-record list`)
    4.  執行 SQUID 模型擬合與分析 (`sc analysis fit`)

---

## 1. 準備數據 (HFSS Export)

首先，您需要從 HFSS 模擬軟體匯出必要的數據。我們需要 **Admittance (Y-parameters)** 的 Touchstone 檔案。

!!! warning "格式要求"
    - 檔案格式：標準 Touchstone (`.snp`，例如 `.s1p` 或 `.s2p`)
    - 頻率範圍：建議覆蓋 SQUID 的預期共振頻率 ($10 \sim 30$ GHz)
    - 參數類型：必須包含 **Y-parameters** (Admittance)

假設您的檔案位於 `data/raw/hfss_export/`，檔名為 `LJPAL658_v1.s2p`。

---

## 2. 匯入數據 (Data Ingestion)

將原始模擬檔案匯入系統資料庫，以便後續分析工具使用。

=== "CLI"
    使用 `sc preprocess admittance` 指令：

    ```bash
    # 匯入單一檔案
    uv run sc preprocess admittance data/raw/hfss_export/LJPAL658_v1.s2p
    
    # 或者匯入整個目錄
    uv run sc preprocess admittance data/raw/hfss_export/
    ```

=== "UI (TBD)"
    !!! info "即將推出"
        圖形化匯入介面正在開發中。未來您可以透過拖放檔案完成此步驟。

成功執行後，您會看到类似 `Imported data/raw/... -> Dataset: LJPAL658_v1` 的成功訊息。

---

## 3. 驗證數據 (Verify)

在開始分析前，確認資料庫中是否已正確建立 Dataset 與 Data Record。

=== "CLI"
    列出所有 Dataset 與其關聯的記錄：

    ```bash
    uv run sc db dataset-record list
    ```

    **預期輸出範例**：
    ```text
    Dataset: LJPAL658_v1 (ID: 1)
      └─ Record 1: Y-parameters (imaginary, Y11)
    ```

=== "UI (TBD)"
    !!! info "即將推出"
        未來可在 Dashboard 的 "Data Explorer" 分頁查看所有數據。

---

## 4. 執行擬合 (Fitting)

現在我們可以針對匯入的數據執行 **LC-SQUID 模型擬合**。此模型會嘗試提取 $L_s$ (系列電感) 與 $C$ (電容)。

=== "CLI"
    使用 `sc analysis fit lc-squid` 指令：

    ```bash
    # 執行基本擬合 (預設開啟 Ls 擬合)
    uv run sc analysis fit lc-squid LJPAL658_v1
    ```

    如果已知電路特性（例如固定電容設計），可以使用參數優化擬合結果：

    ```bash
    # 固定電容模式 (例如 C = 1.45 pF)
    uv run sc analysis fit lc-squid --fixed-c 1.45 LJPAL658_v1
    
    # 排除系列電感 (Pure LC)
    uv run sc analysis fit lc-squid --no-ls LJPAL658_v1
    ```

    程式會輸出每個 Mode 的擬合參數 ($L_s, C$) 與 RMSE 誤差值，並自動產生擬合圖表 (HTML/PNG)。

=== "UI (TBD)"
    !!! info "即將推出"
        未來可在 "Analysis" 分頁選擇 Dataset 並點擊 "Fit Model" 按鈕。

---

## 5. 檢視結果

擬合完成後，結果會儲存在 `data/results/` (或您設定的輸出目錄)。

- **JSON**: 包含所有擬合參數與數值細節。
- **HTML**: 互動式圖表，可放大縮小檢視擬合曲線與原始數據的吻合度。

!!! success "恭喜！"
    您已完成從原始模擬數據到模型參數提取的完整流程。
