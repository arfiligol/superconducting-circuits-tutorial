---
aliases:
- SQUID JPA Basics
- SQUID JPA 基礎
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: SQUID JPA 基礎物理概念
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# squid-jpa-basics

SQUID JPA (Josephson Parametric Amplifier) 是一種利用超導量子干涉元件 (SQUID) 的非線性電感特性來實現參數放大的微波放大器。

## 為什麼需要 SQUID JPA？

在量子計算與超導電路測量中，訊號通常非常微弱（單光子等級）。傳統半導體放大器引入的雜訊過高，會淹沒量子訊號。JPA 可以達到接近量子極限 (Quantum Limited) 的低雜訊放大，是讀取超導量子位元 (Qubits) 的關鍵元件。

## 工作原理

JPA 的核心是一個可調變的 LC 共振電路：

1. **非線性電感**：SQUID 提供非線性電感 $L_{jun}(\Phi)$，其值隨磁通量 $\Phi$ 變化。
2. **共振頻率可調**：改變 $L_{jun}$ 會改變共振頻率 $f_0 = 1 / 2\pi\sqrt{LC}$。
3. **參數放大**：透過泵浦 (Pump) 訊號調變電感，當泵浦頻率滿足特定條件時（如 $f_{pump} \approx 2 f_{signal}$），能量會從泵浦轉移到訊號，實現放大。

## 本專案的角色

本專案專注於 **靜態特性分析** (Static Characterization)：
1. 分析 JPA 在不同磁通偏壓 (Flux Bias) 下的共振頻率。
2. 擬合 SQUID LC 模型，提取關鍵電路參數（串聯電感 $L_s$、有效電容 $C_{eff}$）。
3. 這些參數對於後續設計與操作點優化至關重要。

## Related

- [LC Resonance Model](lc-resonance-model.md) - 詳細的電路模型公式
- [Resonance Extraction](resonance-extraction.md) - 如何從數據中找到共振頻率
