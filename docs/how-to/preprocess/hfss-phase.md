---
aliases:
- Preprocess HFSS Phase
- HFSS 相位處理
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 如何處理 HFSS S-parameter Phase CSV
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Preprocess HFSS Phase

本指南說明如何將 HFSS 匯出的 S-parameter Phase CSV 數據轉換為分析用的 JSON。

適用於 **Driven Modal** 模擬數據，利用 Group Delay 峰值來尋找共振頻率。

## Steps

1. **確認檔案**
   CSV 應包含 `Freq` 與 Phase 欄位 (e.g., `ang_deg(S(1,1))`).

2. **執行轉換**
   ```bash
   uv run convert-hfss-phase data/raw/phase/MyChip_Phase.csv
   ```

3. **輸出**
   生成 `data/preprocessed/MyChip_Phase.json`。

## Next Steps

- 目前 `squid-model-fit` 主要針對 Admittance 數據，Phase 數據的擬合功能尚未完全整合至 CLI，需使用 `src/extraction/phase.py` 進行代碼層級調用，或等待未來更新。

## Related

- [Resonance Extraction](../../explanation/physics/resonance-extraction.md#2-phase-group-delay-method) - 相位法原理
