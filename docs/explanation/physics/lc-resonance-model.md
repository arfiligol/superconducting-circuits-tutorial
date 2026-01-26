---
aliases:
- LC Resonance Model
- LC 共振模型
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: SQUID JPA LC 電路模型公式推導
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# lc-resonance-model

SQUID JPA 可以建模為一個包含 SQUID 和並聯電容的 LC 共振電路。其中 SQUID 貢獻了可調電感 $L_{jun}$，而電路佈局貢獻了幾何電容 $C$ 和寄生電感 $L_s$。

## 共振頻率公式

理想的 LC 共振頻率為：
$$ f = \frac{1}{2\pi\sqrt{L_{total} C}} $$

由於這是一個 SQUID，其電感 $L_{jun}$ 分佈在兩個結上，且通常有串聯電感 $L_s$ 影響。我們的擬合模型使用以下公式：

$$ f = \frac{1}{2\pi\sqrt{ (L_{jun}/2 + L_s) C_{eff} }} $$

### 參數定義

| 參數 | 符號 | 單位 | 物理意義 |
|------|------|------|----------|
| **Junction Inductance** | $L_{jun}$ | nH | SQUID 結的電感，隨磁通偏壓變化。這是我們的自變數 x。 |
| **Series Inductance** | $L_s$ | nH | 與 SQUID 串聯的幾何電感。這是擬合參數之一。 |
| **Effective Capacitance** | $C_{eff}$ | pF | 總有效電容。這是擬合參數之一。 |

## 模型變化

本專案支援三種擬合模式 (`FittingModel`)：

1. **No Ls ($L_s = 0$)**
   - 假設寄生電感忽略不計。
   - 公式簡化為：$f = \frac{1}{2\pi\sqrt{ (L_{jun}/2) C }}$
   - 適用於初步估算。

2. **With Ls (標準模式)**
   - 同時擬合 $L_s$ 和 $C$。
   - 最準確，但如果數據點過少可能會有參數相依性 (Parameter Correlation)。

3. **Fixed C**
   - 固定 $C$ 為已知值（例如來自模擬），僅擬合 $L_s$。
   - 適用於已知幾何電容，想精確提取寄生電感時。

## Related

- [squid-model-fit](../../reference/cli/squid-model-fit.md) - 執行此模型擬合的指令
- [SQUID JPA Basics](squid-jpa-basics.md) - 基礎物理背景
