---
aliases:
- Preprocessing Rationale
- 前處理設計理由
tags:
  - diataxis/explanation
  - status/stable
  - topic/architecture
  - topic/pipeline
  - audience/team
status: stable
owner: docs-team
audience: team
scope: 為什麼使用 SQLite Dataset 作為中間層
version: v0.2.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Preprocessing Rationale

即使我們把 Analysis 與 Visualization 合併成單一流程，前處理中間層仍然必要。

## 問題不是「能不能直接算」，而是「能不能穩定重現」

原始資料來源天然異質：

1. HFSS 匯出（Admittance / S-parameters）
2. VNA 實驗量測
3. 其他模擬工具格式

如果分析直接吃 raw 檔，會遇到：

- 欄位命名/單位/shape 不一致
- 同一分析方法在不同資料源需分支邏輯
- UI 與 CLI 可能各自實作自己的解析流程

## 解法：先標準化，再分析與可視化

我們保留 SQLite Dataset 當中間層，讓「資料清理/轉換」與「分析語意」分離。

### 為什麼這樣更好

1. **分析語意固定**

- 分析方法只處理統一 schema，不處理來源格式差異。

2. **可視化輸出可預測**

- 因為分析輸入穩定，UI/CLI 的圖表與摘要格式可以一致對應。

3. **驗證責任前移**

- schema/unit 檢查在 ingestion 時完成，避免分析過程才爆錯。

4. **重現性與追溯性**

- Dataset 作為 SoT，可重跑分析並比對結果差異。

!!! info "一體化不等於無分層"
    「分析直接對應可視化」是執行語意的一體化；
    「Raw -> Dataset -> Analysis」仍是資料責任的分層。

## Related

- [Dataset Record Schema](../../../reference/data-formats/dataset-record.md) - Schema 定義
- [Data Flow](data-flow.md) - 整體流程
