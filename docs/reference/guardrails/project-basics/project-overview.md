---
aliases:
  - "專案概述 (Project Overview)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# 專案概述 (Project Overview)

本專案的目標已從單純教學網站，收斂為一個以 **超導電路設計資料平台** 為核心的雙語應用與文件系統。

## 專案使命

建立一個高品質的雙語（繁體中文/英文）平台，讓使用者可以在同一個 `Design` scope 下：

- 定義與模擬 circuit
- 匯入與分析 layout simulation traces
- 匯入與分析 measurement traces
- 對來自不同來源但相容的 S/Y/Z matrix traces 執行同一套 Characterization
- 比較 layout / circuit / measurement 之間的差異

## 範疇

- **資料來源**
  - circuit simulation（`JosephsonCircuits.jl`）
  - layout simulation（HFSS/Q3D 等）
  - measurement（VNA 等）
- **統一分析輸入**
  - S/Y/Z matrix traces
- **核心 UI**
  - Schema Editor
  - Circuit Simulation
  - Post-Processing
  - Characterization
- **文件系統**
  - Zensical，雙語化（zh-TW / en）

## 目標受眾

- 超導電路 / 量子計算領域的研究人員與學生
- 需要比較 layout / circuit / measurement 差異的使用者
- 希望建立 trace-first characterization workflow 的開發者

---

## Agent Rule { #agent-rule }

```markdown
## Project Goal
- **Mission**: Build a bilingual superconducting-circuit design data platform plus tutorial/docs system.
- **Scope**:
    - **Sources**: circuit simulation, layout simulation, and measurement.
    - **Simulation**: `JosephsonCircuits.jl` (Julia).
    - **Analysis**: one characterization workflow over compatible S/Y/Z matrix traces.
    - **Storage direction**: metadata DB + external trace store.
- **Core Values**:
    - **Scientific Accuracy**: physics and equations must remain rigorous.
    - **Trace-first analysis**: characterization operates on trace compatibility, not source-kind-specific UI rules.
    - **Bilingual**: primary content remains **Traditional Chinese (zh-TW)** with synced English pages.
- **Target Audience**: researchers, students, and developers working on superconducting-circuit simulation and analysis workflows.
```
