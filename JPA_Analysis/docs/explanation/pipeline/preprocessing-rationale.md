---
aliases:
  - "Preprocessing Rationale"
  - "前處理設計理由"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "為什麼引入 ComponentRecord 中間層"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Preprocessing Rationale

為什麼我們不直接讀取 CSV 進行分析，而要多此一舉建立 `data/preprocessed/*.json`？

## 問題：數據來源的多樣性

在開發過程中，我們面臨多種數據來源：
1. **ANSYS HFSS (頻域)** - 虛阻納 (Admittance)
2. **ANSYS HFSS (Driven Modal)** - S-parameters (Phase)
3. **VNA 測量** - 實機測量的 Flux Sweep
4. **Sonnet 模擬** - (未來可能引入)

這些來源的檔案格式截然不同：
- Header 不同
- 分隔符不同 (逗號 vs Tab)
- 矩陣排列不同 (Pivot vs Long format)
- 單位不同 (Hz vs GHz, Rad vs Deg)

## 解法：標準化中間層 (`ComponentRecord`)

我們引入 `ComponentRecord` (Pydantic Model) 作為統一的中間交換格式。

### 優點

1. **解耦分析與 I/O**
   - 分析邏輯 (`squid-model-fit`) 不需要知道數據來自 HFSS 還是 VNA。
   - 它只需要知道：「這是一個 Component，它有一組頻率 vs 數值」。

2. **Schema Validation**
   - 轉換階段就會檢查數據完整性 (例如是否缺失軸數據)。
   - 避免分析跑到一半才因為 `KeyError` 崩潰。

3. **Metadata 管理**
   - JSON 可以攜帶額外資訊 (Attenuator 設定、溫度、模擬版本)。
   - 原始 CSV 通常會丟失這些 Context。

4. **快取與效能**
   - 解析大型 TXT 可能很慢。
   - 讀取優化過的 JSON 結構更快。

## Related

- [[../../reference/data-formats/component-record.md|Component Record Schema]] - Schema 定義
- [[./data-flow.md|Data Flow]] - 整體流程
