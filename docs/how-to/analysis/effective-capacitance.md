---
aliases:
  - "Effective Capacitance Fit"
  - "有效電容擬合"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "如何執行有效電容擬合分析"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Effective Capacitance Fit

本指南說明如何使用 `effective-capacitance-fit` 工具。

> [!NOTE]
> 這是一個舊版工具，主要用於比較不同設計版本的有效電容。新版建議使用 [squid-model-fit](admittance-fit.md)。

## Steps

1. **準備前處理數據** (同 [HFSS Admittance](../preprocess/hfss-admittance.md)).

2. **執行指令**
   ```bash
   uv run effective-capacitance-fit [components ...]
   ```

3. **解讀結果**
   該工具會假設 $L_s=0$，並計算每個 $L_{jun}$ 點對應的有效電容 $C_{eff}$，最後取平均值。

## Related

- [Admittance Fit](admittance-fit.md) - 更完整的擬合方法
