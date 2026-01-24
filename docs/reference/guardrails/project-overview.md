# 專案概述 (Project Overview)

本文件說明專案的核心目標、範疇與目標受眾。

## 專案使命

建立一個高品質的雙語（繁體中文/英文）**超導電路教學網站**，涵蓋從 HFSS/VNA 資料匯入到 `JosephsonCircuits.jl` 模擬與分析的完整流程。

## 範疇

- **資料來源**: HFSS Admittance/Phase data, VNA S-parameter
- **核心模擬**: `JosephsonCircuits.jl` (Julia)
- **分析工具**: Python CLI 腳本 (Squid fitting, Plotting)
- **文件系統**: MkDocs Material, 雙語化 (zh-TW / en)

## 目標受眾

- 量子計算 / 超導電路領域的**研究人員**與**學生**
- 希望將 HFSS 模擬結果轉換為電路參數的使用者
- 希望了解 JPA/SQUID 電路分析方法的學習者

---

## Agent Rule { #agent-rule }

```markdown
## Project Goal
- **Mission**: Create a high-quality, bilingual (Traditional Chinese/English) tutorial for superconducting circuits simulation.
- **Scope**:
    - **Data Sources**: HFSS (Admittance/Phase), VNA (S-param).
    - **Simulation**: `JosephsonCircuits.jl` (Julia).
    - **Analysis**: Python CLI scripts (SQUID fitting, Plotting).
- **Core Values**:
    - **Scientific Accuracy**: All equations and physics explanations must be rigorous.
    - **Bilingual**: Primary content in **Traditional Chinese (zh-TW)**.
- **Target Audience**: Researchers/Students (PhD/Master level).
```
