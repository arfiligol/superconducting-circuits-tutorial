---
aliases:
  - "Simulation Guide"
  - "模擬指南"
tags:
  - diataxis/how-to
  - status/stable
  - topic/simulation
status: stable
owner: docs-team
audience: user
scope: "電路模擬教學索引"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# 電路模擬 (Simulation)

本專案使用 [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) 進行超導電路模擬。

## 教學方法選擇

我們提供**兩種主要方法**進行模擬，以 Python 為主：

| 方法 | 適合對象 | 學習曲線 |
|------|----------|----------|
| **Python CLI/API** | 大多數使用者 | ⭐ 簡單 |
| **原生 Julia** | 進階使用者、擴充開發 | ⭐⭐⭐ 進階 |

## 教學列表

### Python API

| 教學 | 說明 |
|------|------|
| [Python API 詳解](python-api.md) | 在 Python 腳本中定義電路、設定參數、執行模擬 |

### 原生 Julia

| 教學 | 說明 |
|------|------|
| [原生 Julia 模擬](native-julia.md) | 直接使用 JosephsonCircuits.jl 進行模擬 |

## 相關資源

- [CLI Reference: sc-simulate-lc](../../reference/cli/sc-simulate-lc.md) - 指令參數
- [Tutorial: LC 共振器](../../tutorials/lc-resonator.md) - 完整入門案例
- [Harmonic Balance 說明](../../explanation/physics/harmonic-balance.md) - 模擬原理
- [擴充 Julia 函數](../extend/extend-julia-functions.md) - 貢獻者指南
