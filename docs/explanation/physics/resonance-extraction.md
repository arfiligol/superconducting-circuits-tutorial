---
aliases:
- Resonance Extraction
- 共振擷取方法
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 從 Im(Y) 和 Phase 數據擷取共振頻率的方法
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# resonance-extraction

在進行 LC 模型擬合前，我們必須先從原始掃頻數據中提取出共振頻率 $f_0$。本專案支援兩種提取方法：

## 1. Admittance Method (虛阻納法)

適用於 `hfss-admittance` 數據。

### 原理
在並聯 LC 電路共振時，導納 (Admittance) $Y = G + jB$ 的虛部 (Susceptance, $B$) 為零。
即 $Im(Y) = 0$。

### 演算法
1. 對於每個 $L_{jun}$ 掃描點：
2. 尋找 $Im(Y)$ 曲線與 0 的交點 (Zero Crossings)。
3. 當 $y_i$ 與 $y_{i+1}$ 異號時，透過線性插值求出精確過零頻率：
   $$ f_0 = f_i - y_i \frac{f_{i+1} - f_i}{y_{i+1} - y_i} $$
4. 這些 $f_0$ 即為共振頻率（可能有多個 Mode）。

## 2. Phase Group Delay Method (相位群延遲法)

適用於 `hfss-phase` 或 `measurement` S11 數據。

### 原理
在共振點附近，相位 $\phi$ 會發生劇烈變化。相位對角頻率的導數定義為群延遲 (Group Delay)：
$$ \tau_g = -\frac{d\phi}{d\omega} $$
共振點通常對應於群延遲的 **峰值 (Peak)**。

### 演算法
1. 將相位由 Degrees 轉換為 Radians。
2. 進行相位解包裹 (Unwrap Phase) 以移除 $2\pi$ 跳變。
3. 計算數值微分求群延遲：$\tau = -\Delta\phi / \Delta\omega$。
4. 尋找 $\tau$ 的最大值位置，對應的頻率即為 $f_0$。
5. **Q-factor 估算**：利用 $\tau_{max} = \frac{4 Q}{\omega_0}$ 關係式，可同時估算品質因子 Q。

## Source Code Reference

- Admittance Extraction: `src/extraction/admittance.py`
- Phase Extraction: `src/extraction/phase.py`

## Related

- [LC Resonance Model](lc-resonance-model.md) - 提取後的頻率用於模型擬合
- [Admittance Fit Guide](../../how-to/analysis/admittance-fit.md) - 實際操作指南
