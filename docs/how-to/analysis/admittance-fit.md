---
aliases:
- Admittance Fit Analysis
- 執行虛阻納擬合
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 如何執行 SQUID LC 模型擬合
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Run Admittance Fit

本指南說明如何使用 `squid-model-fit` 工具分析共振頻率並提取 $L_s, C$ 參數。

## Prerequisites

- 已完成 [前處理](../preprocess/hfss-admittance.md)，並有 `data/preprocessed/*.json` 檔案。

## Steps

1. **執行基本擬合 (無串聯電感)**
   最簡單的模式，快速檢查數據品質。
   ```bash
   uv run squid-model-fit LJPAL658_v1
   ```
   > 註：`LJPAL658_v1` 是 Component ID (對應 `data/preprocessed/LJPAL658_v1.json`)。

2. **檢視結果**
   - 終端機會顯示擬合參數 ($C$, RMSE)。
   - 瀏覽器會自動打開 Plotly 圖表，顯示原始數據點與擬合曲線。

3. **執行完整擬合 (含 $L_s$)**
   如果基本擬合誤差 (RMSE) 較大，嘗試加入串聯電感：
   ```bash
   uv run squid-model-with-Ls-fit LJPAL658_v1
   ```

4. **(進階) 設定參數邊界**
   如果擬合結果不物理 (例如 $L_s < 0$)，可以強制邊界：
   ```bash
   uv run squid-model-with-Ls-fit --ls-min 0.0 --ls-max 0.5 LJPAL658_v1
   ```

## Troubleshooting

- **"Not enough points"**: 數據點過少，無法擬合。請檢查原始數據是否包含足夠多的 $L_{jun}$ 掃描點。
- **RMSE 過大**: 模型可能不適用，或者共振點提取錯誤 (Plotly 圖中檢查 Outliers)。

## Related

- [LC Model Theory](../../explanation/physics/lc-resonance-model.md) - 理解參數意義
- [CLI Reference](../../reference/cli/squid-model-fit.md) - 完整參數表
