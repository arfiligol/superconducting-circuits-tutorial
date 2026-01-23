---
aliases:
  - "Flux Dependence Plot Guide"
  - "磁通依賴繪圖指南"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "如何繪製 Flux Dependence Heatmap"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Flux Dependence Plot

本指南說明如何使用 `flux-dependence-plot` 工具視覺化 VNA 掃描數據。

## Prerequisites

- 已完成 [[../preprocess/flux-dependence.md|Flux Dependence 前處理]]。

## Steps

1. **基本繪圖**
   同時顯示 Amplitude 與 Phase 熱圖。
   ```bash
   uv run flux-dependence-plot LJPAL6572_B44D1
   ```

2. **觀察相位**
   S11 Phase 通常能更清晰地顯示共振點。
   ```bash
   uv run flux-dependence-plot --view phase --phase-unit deg --wrap-phase LJPAL6572_B44D1
   ```
   - `--phase-unit deg`: 使用角度顯示。
   - `--wrap-phase`: 將相位折疊在 $\pm 180^\circ$ 區間，增強對比。

3. **切片分析 (Slicing)**
   如果想看特定 Bias 下的頻率響應（類似 VNA 單次掃描）：
   ```bash
   uv run flux-dependence-plot --slice-bias 0.0 --slice-bias 0.5 LJPAL6572_B44D1
   ```
   這會生成額外的 2D 切片圖。

## Related

- [[../../reference/cli/flux-dependence-plot.md|CLI Reference]] - 完整參數
