---
aliases:
- Resonance Fitting Workflow
- 共振擬合工作流
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 完整 SQUID 參數提取流程：原理、操作與解讀
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Resonance Fitting

本教程將引導你完成 SQUID JPA 的核心分析任務：**從導納數據提取電路參數 ($L_s, C_{eff}$)**。

## 1. Goal & Physics

**目標**：我們有一組 HFSS 模擬的虛阻納 (Imaginary Admittance) 數據，我們想要知道這個設計的寄生電感 ($L_s$) 與有效電容 ($C_{eff}$) 是多少。

**背後原理**：
1. **為什麼看 Im(Y)?**
   並聯 LC 電路共振時，虛部導納為零 ($Im(Y)=0$)。我們透過尋找過零點來提取共振頻率 $f_0$。
   > 深入閱讀：[Physics（重建中）](../explanation/physics/index.md)

2. **為什麼擬合模型?**
   提取出的 $f_0$ 會隨 $L_{jun}$ (Junction Inductance) 變化。透過擬合 $f_0(L_{jun})$ 曲線，我們可以反推電路參數。
   $$ f = \frac{1}{2\pi\sqrt{(L_{jun}/2 + L_s)C_{eff}}} $$
   > 深入閱讀：[Physics（重建中）](../explanation/physics/index.md)

## 2. Step-by-Step Analysis

### Step 1: Preprocess (Format Conversion)

原始 HFSS 數據通常是 CSV 格式，包含頻率與多個參數。我們首先將其標準化。

```bash
# 假設原始檔位於 data/raw/admittance/
uv run sc preprocess admittance data/raw/admittance/MyChip_Y11.csv --dataset-name MyChip
```
這會在 `data/database.db` 中建立對應的 Dataset，包含標準化的頻率掃描資料。

### Step 2: Visualization (Sanity Check)

在擬合前，先確認數據品質。共振點是否清晰？有無雜訊？

```bash
uv run sc plot admittance --show-zeros MyChip
```

- **操作**：瀏覽器會打開互動圖表。
- **觀察**：開啟 `--show-zeros` 後，圖上會標示出紅色的 `x`，這些就是程式自動識別的共振點 $f_0$。
- **物理檢核**：如果 $Im(Y)$ 曲線沒有穿過零點，代表該頻率範圍內無共振，後續擬合會失敗。

### Step 3: Model Fitting (Parameter Extraction)

執行擬合。建議從簡單模型 (No $L_s$) 開始，再嘗試完整模型。

```bash
uv run sc analysis fit lc-squid MyChip
```

### 3. Interpreting Results

程式會輸出如下結果：

```text
Fitting Results for MyChip:
----------------------------------------
Mode 1:
  Ls = 0.082 nH
  C  = 1.450 pF
  RMSE = 0.005 GHz
```

**如何解讀？**
- **$C$ (1.45 pF)**: 這是你的總並聯電容。如果與 HFSS 設定的幾何電容差異過大，可能暗示模型誤差。
- **$L_s$ (0.082 nH)**: 這是寄生電感。對於寬頻 JPA 設計，我們希望這個值越小越好（通常 < 0.1 nH）。
- **RMSE**: 擬合曲線與實際數據的頻率誤差。如果 > 0.01 GHz，可能需要檢查是否有 Mode Crossing 或數據壞點。

## Next Steps

- **多模態分析**：如果看到多個 Mode，可以使用 `--modes 'Mode 2'` 指定分析特定模態。
- **固定電容**：如果你很確定電容值，可以使用 `sc analysis fit lc-squid --fixed-c <pF>` 來獲得更精準的 $L_s$。
