---
aliases:
  - "Superconducting Circuits: Simulation & Analysis"
tags:
  - diataxis/reference
  - status/draft
---

# Superconducting Circuits: Simulation & Analysis

歡迎來到超導電路模擬與分析教學！

本專案是一個整合 **理論模擬** 與 **實驗分析** 的完整框架。無論你是要設計新的量子電路，還是要分析實驗室測量到的 VNA 數據，這裡都有對應的工具與指南。

## 這是什麼？

這是一個結合 **教學**、**研究** 與 **實戰工具** 的平台：

- 🎮 **Simulation (模擬)**：使用 [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) 與 HFSS 模擬電路行為。
- 📊 **Analysis (分析)**：提供通用的 Python 工具鏈，分析 **模擬** 或 **實測 (VNA)** 數據，提取關鍵參數(e.g: $L_s, C_{eff}, f_0$)。
- 📚 **Knowledge (知識)**：從基礎物理模型 (LC Resonator) 到進階架構 (Floating Qubit) 的完整筆記。

## 目前支援的分析 (Capabilities)

本平台目前專注於 SQUID 與 JPA 的靜態特性分析：

- **SQUID 参数提取**：從 S11/Y11 數據擬合電路模型，分離 **幾何電感 ($L_s$)** 與 **有效電容 ($C_{eff}$)**。
- **Flux Sweep 分析**：繪製隨磁通偏壓變化的頻率響應圖 (Flux Map)，驗證 SQUID 的調變能力。
- **共振點識別**：自動從複雜的頻譜中識別共振頻率 ($f_0$) 與品質因子 ($Q$)。

## 適合誰？

- **Theory / Simulation**: 想要模擬電路行為、預測頻譜的研究者。
- **Experiment / Analysis**: 擁有模擬或實驗數據，需要擬合 SQUID 參數的分析人員。
- **Newcomers**: 剛接觸超導量子電路，想了解從模擬到實測完整流程的學生。

## 快速開始 (Getting Started)

### 1. 環境準備
- [安裝指南](how-to/getting-started/installation.md) — 設定 Julia (模擬) 與 Python (分析) 環境

### 2. 選擇你的路徑
- **我是模擬使用者**：
    - [第一次模擬](how-to/getting-started/first-simulation.md) — 執行你的第一個 Julia 電路模擬
    - [HFSS 模擬流程](tutorials/simulation-workflow.md) — 從 HFSS 到參數提取的端到端流程
- **我是實驗分析者**：
    - [SQUID 參數提取](tutorials/resonance-fitting.md) — 從數據擬合 $L_s$ 與 $C$
    - [Flux Analysis](tutorials/flux-analysis.md) — 分析 VNA 磁通掃描數據

## 專案結構

此專案採用 **App-Centric Hybrid 架構**，核心邏輯位於 `src/`：

### 1. 核心邏輯
- **`src/sc_analysis/`** (Python): 實驗數據分析核心 (Fitting, Plotting, Processing)。
- **`src/plotting.jl`** (Julia): 模擬數據視覺化工具。

### 2. 應用層
- **`scripts/`**: CLI 工具集 (e.g., `squid-model-fit`, `flux-dependence-plot`)。
- **`sc_app/`**: GUI 應用程式 (NiceGUI)。

### 3. 文件
- **`docs/`**: 本文件網站，包含教學與 API 參考。
