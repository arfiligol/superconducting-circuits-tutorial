---
aliases:
  - "Simulation Workflow"
  - "模擬分析工作流"
tags:
  - boundary/system
  - audience/team
status: draft
owner: docs-team
audience: team
scope: "完整 HFSS 模擬到參數提取的端到端流程"
version: v0.1.0
last_updated: 2026-01-13
updated_by: docs-team
---

# Simulation Workflow (HFSS to Parameter Extraction)

本教程涵蓋從 ANSYS HFSS 模擬到 SQUID 參數提取的**完整流程**。

> [!TIP]
> 如果你已經有 CSV 數據，可以直接跳到 [[./resonance-fitting.md|Resonance Fitting]]。

## Overview

```mermaid
flowchart LR
    A["HFSS Simulation"] --> B["Export CSV"]
    B --> C["Preprocess"]
    C --> D["Resonance Extraction"]
    D --> E{"Im(Y) vs Phase(S)<br/>Consistency Check"}
    E -->|OK| F["Discrete Re-simulation"]
    F --> G["High-Accuracy Data"]
    G --> H["Parameter Fit"]
```

---

## Step 1: HFSS Simulation Setup

### 1.1 Parametric L_jun Sweep

在 HFSS 中設定一個 **Design Variable** `L_jun`，代表 Junction Inductance (單位: nH)。

建議掃描範圍：
- **Coarse Sweep**: `L_jun = 0.1 nH ~ 10 nH`，步長 `0.5 nH`
- **Fine Sweep**: 根據初步結果縮小範圍

### 1.2 Frequency Range

| Mode Type | Suggested Range |
|-----------|-----------------|
| JPA Mode (低頻) | 1 ~ 12 GHz |
| SRF Mode (高頻) | 8 ~ 20 GHz |

> [!NOTE]
> 確保頻率範圍涵蓋預期的共振頻率，否則後續擬合會失敗。

### 1.3 What to Export

從 HFSS 匯出以下 CSV 檔案：

| Parameter | HFSS Export Name | Purpose |
|-----------|-----------------|---------|
| **Im(Y11)** | `im(Y(1,1))` | 主要共振提取方法 |
| **Phase(S11)** | `ang_deg(S(1,1))` | 交叉驗證共振頻率 |

---

## Step 2: Resonance Extraction (Im(Y) Method)

這是主要的共振頻率提取方法。詳細操作見 [[./resonance-fitting.md|Resonance Fitting Tutorial]]。

```bash
# 轉換 CSV → JSON
uv run convert-hfss-admittance data/raw/admittance/MyChip_Im_Y11.csv --component-id MyChip

# 視覺化並標示共振點
uv run plot-admittance --show-zeros MyChip
```

---

## Step 3: Resonance Extraction (Phase(S) Method)

使用 S11 的相位數據來交叉驗證共振頻率。

### 3.1 Preprocess

```bash
uv run convert-hfss-phase data/raw/phase/MyChip_Phase_S11.csv --component-id MyChip_Phase
```

### 3.2 Extraction (Manual)

> [!WARNING]
> 目前 Phase 方法尚未整合至 CLI 工具，需手動分析。

**原理**：共振點會造成相位的 $180°$ 突變 (Group Delay 峰值)。

**手動分析步驟**：
1. 使用 `src/extraction/phase.py` 中的函式
2. 或在 HFSS 中直接觀察 Phase vs Frequency 曲線的拐點

---

## Step 4: Consistency Check (Im(Y) vs Phase(S))

**目的**：確保兩種方法提取的共振頻率一致。

### 手動比較

1. 記錄 Im(Y) 方法的 $f_0$ (每個 $L_{jun}$ 值)
2. 記錄 Phase(S) 方法的 $f_0$
3. 計算差異：$\Delta f = |f_{Y} - f_{S}|$

**預期結果**：
- $\Delta f < 0.01$ GHz：一致性良好
- $\Delta f > 0.05$ GHz：需檢查模擬設定或 Port 阻抗

> [!NOTE]
> 差異來源：S-parameter 會受到 Port Impedance ($Z_0$) 影響，而 Y-parameter 是純元件特性。

---

## Step 5: Discrete Re-simulation

當初步分析確認共振頻率範圍後，進行高精度再模擬。

### 5.1 HFSS Settings (手動操作)

1. **Sweep Type**: 改為 **Discrete**
2. **Frequency Points**: 只掃描共振附近 (例如 $f_0 \pm 0.5$ GHz，每 10 MHz 一點)
3. **Solution Type > Advanced**:
   - **Order of Basis Functions**: Second Order
   - **Maximum Delta S**: 0.001 (或更小)

### 5.2 Re-export

完成後，重新匯出高精度數據，覆蓋原始 CSV。

---

## Step 6: Re{Y_in} from S (HFSS 內部操作)

> [!IMPORTANT]
> 此步驟在 HFSS 內完成，非本專案工具。

在 HFSS 的 **Results > Create Report** 中：

1. **Category**: Terminal Solution Data
2. **Quantity**: `re(Yin(Port1))`
3. **X-axis**: Frequency

**用途**：觀察 $Re\{Y_{in}\}$ 的峰值位置，這對應於共振點的功率吸收。

---

## Step 7: C_eff Extraction (No Lumped L)

當您有一組**不包含 Lumped L 設定**的 Y-parameter 數據時，可以直接提取有效電容 $C_{eff}$。

> [!CAUTION]
> 使用此方法前，**請手動確認**您的 HFSS 模型中沒有設定 Lumped Element 的電感。

### 原理

沒有 Lumped L 時，電路總電感只有 $L_{jun}$。由共振條件：
$$ f_0 = \frac{1}{2\pi\sqrt{L_{jun} \cdot C_{eff}}} $$

我們可以反推：
$$ C_{eff} = \frac{1}{(2\pi f_0)^2 L_{jun}} $$

### 執行

```bash
uv run effective-capacitance-fit MyChip_NoL
```

程式會對每個 $L_{jun}$ 計算對應的 $C_{eff}$，並輸出平均值與標準差。

---

## Next Steps

- [[./resonance-fitting.md|Resonance Fitting]] - 完整 LC 模型擬合 (有 $L_s$)
- [[../how-to/analysis/admittance-fit.md|Admittance Fit How-to]] - CLI 參數詳解
