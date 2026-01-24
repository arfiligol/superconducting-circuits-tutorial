---
aliases:
  - "Preprocess Flux Dependence"
  - "磁通依賴數據處理"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "如何處理 VNA Flux Dependence TXT"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Preprocess Flux Dependence

本指南說明如何將 VNA 測量的 Flux Dependence TXT 檔案轉換為標準 JSON。

## Format Requirements

支援 Linköping VNA Lab 的標準 TXT 輸出格式：
- 包含 header metadata
- 數據區塊為 Matrix 形式
- 包含 Frequency 向量與 Bias Current 向量

## Steps

1. **執行轉換**
   ```bash
   uv run convert-flux-dependence data/raw/measurement/flux_dependence/Biasing_Sweep.txt
   ```

2. **指定參數 (Optional)**
   如果測量的是 S21 而非 S11：
   ```bash
   uv run convert-flux-dependence --parameter S21 data/raw/...
   ```

## Next Steps

- [Plot Flux Dependence](../analysis/flux-dependence-plot.md) - 繪製熱圖

## Related

- [CLI Reference](../../reference/cli/convert-flux-dependence.md)
