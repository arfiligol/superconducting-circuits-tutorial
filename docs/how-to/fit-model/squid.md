---
aliases:
  - "Fitting SQUID Parameters"
  - "SQUID 參數擬合"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/analysis
status: stable
owner: team
audience: user
scope: "如何從 Admittance 數據擬合 SQUID 電路參數 (Ls, C)"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# Fitting SQUID Models

本指南說明如何針對已匯入的 Admittance 數據執行 **LC-SQUID** 模型擬合，以提取電路參數（系列電感 $L_s$ 與電容 $C$）。

!!! info "前置條件"
    - 數據已匯入資料庫（請參閱 [Ingest HFSS Data](../ingest-data/hfss.md)）。
    - 知道目標 Dataset 的 **名稱 (Name)** 或 **ID**。

---

## 選擇擬合策略

根據您的電路設計與數據特性，選擇合適的擬合模式：

| 模式 | 適用情境 | 指令關鍵字 |
|------|----------|------------|
| **Standard (With Ls)** | 一般情況，需同時決定 $L_s$ 與 $C$ | (Default) |
| **Fixed Capacitance** | 已知量測或設計的準確電容值，僅需優化 $L_s$ | `--fixed-c <VAL>` |
| **Ideal LC (No Ls)** | 忽略系列電感，僅擬合純 LC 共振 (較少用) | `--no-ls` |

---

## 操作步驟

=== "CLI"

    核心指令為 `sc analysis fit lc-squid`。

    ### 1. 執行標準擬合 (Standard Fit)

    這是最常用的模式，同時擬合 $L_s, C$：

    ```bash
    uv run sc analysis fit lc-squid <DATASET_NAME>
    ```

    !!! tip "指定特定 Modes"
        若只想分析特定 Mode，可使用 `--modes` 參數：
        ```bash
        uv run sc analysis fit lc-squid --modes 1 --modes 2 <DATASET_NAME>
        ```

    ### 2. 固定電容擬合 (Fixed C)

    當 $C$ 已知時（例如 $C=1.45$ pF），此模式能提供更精準的 $L_s$ 結果：

    ```bash
    uv run sc analysis fit lc-squid --fixed-c 1.45 <DATASET_NAME>
    ```

    ### 3. 設定參數邊界 (Bounds)

    若擬合結果不物理（例如 $L_s < 0$ 或數值發散），可以強制設定邊界：

    ```bash
    # 限制 Ls <= 0.2 nH
    uv run sc analysis fit lc-squid --ls-max 0.2 <DATASET_NAME>
    ```

=== "UI (TBD)"

    !!! warning "開發中"
        圖形化分析介面尚在開發階段。

    1. 進入 **Analysis** 頁面。
    2. 從列表中選擇要分析的 **Dataset**。
    3. 在 "Fit Configuration" 面板選擇模型 (**LC-SQUID**)。
    4. 設定 Constraints (例如勾選 "Fixed C" 並輸入數值)。
    5. 點擊 **Run Fit**。

---

## 結果檢視

擬合完成後，系統會生成報告：

1. **Console 輸出**: 顯示每個 Mode 的擬合數值與 RMSE。
2. **HTML Plot**: 儲存於 `data/results/plots/`，可互動檢視。
3. **JSON Metadata**: 儲存於 `data/results/json/`，供程式化讀取。

---

## 相關參考

- [Tutorial: End-to-End Fitting](../../tutorials/end-to-end-fitting.md)
- [CLI Reference: analysis fit](../../reference/cli/sc-fit-squid.md)
