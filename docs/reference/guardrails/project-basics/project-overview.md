---
aliases:
  - Project Overview
  - 專案概述
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/project-basics
status: stable
owner: docs-team
audience: contributor
scope: 定義 rewrite branch 的產品使命、功能範疇、desktop 支援與 migration 方向。
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Project Overview

本專案不再把 NiceGUI 視為主要產品落點。
當前 branch 的目標是把既有需求重構為 **前後端分離的超導電路工作台**，同時保留 CLI 與科學計算核心，並支援本地 desktop runtime。

## Mission

建立一個讓研究者能在同一套系統中完成下列工作的平台：

- Data Browser
- Circuit Definition Editor
- Circuit Schemdraw
- Circuit Simulation
- Characterization
- Analysis
- CLI Available

## Scope

### Core Product Surfaces

| 能力 | 說明 |
| --- | --- |
| Data Browser | 瀏覽 metadata、trace summary、analysis result 與 lineage |
| Circuit Definition Editor | 編輯 circuit/netlist/schema 定義，並提供驗證與格式化 |
| Circuit Schemdraw | 由 canonical circuit definition 產生可視化電路圖 |
| Circuit Simulation | 以 `JosephsonCircuits.jl` 為核心進行模擬與掃描 |
| Characterization | 對 simulation / layout / measurement traces 套用一致分析流程 |
| Analysis | 後處理、擬合、比較、參數萃取與視覺化 |
| CLI Available | 所有關鍵工作流必須可從 CLI 執行，不以 UI 獨占 |

### Accepted Data Sources

- circuit simulation traces
- layout simulation traces（例如 HFSS / Q3D）
- measurement traces（例如 VNA）
- 相容的 S/Y/Z matrix traces 與其衍生分析結果

### Rewrite Direction

- UI：以 **Next.js App Router** 為主
- API：以 **FastAPI** 為主
- CLI：維持一級公民，與 API/核心服務共用規則而非複製邏輯
- Desktop：允許使用 **Electron** 包裝 frontend，形成可本地執行的 desktop app
- Legacy：既有 NiceGUI 僅作為 migration 參考，不再作為新功能預設實作層

## Target Audience

- 超導電路與量子硬體研究人員
- 需要整合 simulation / layout / measurement 的使用者
- 需要可重現 CLI workflow 與可擴充 Web UI 的開發者

## Agent Rule { #agent-rule }

```markdown
## Project Goal
- **Mission**: Build a superconducting-circuit workbench with a separated frontend/backend architecture and first-class CLI support.
- **Core product surfaces**:
    - Data Browser
    - Circuit Definition Editor
    - Circuit Schemdraw
    - Circuit Simulation
    - Characterization
    - Analysis
    - CLI Available
- **Data sources**:
    - circuit simulation
    - layout simulation
    - measurement
    - compatible S/Y/Z traces
- **Architecture direction**:
    - UI uses Next.js App Router
    - API uses FastAPI
    - CLI stays supported and must share business rules with the core/backend
    - Electron is an allowed desktop wrapper for local-first desktop runtime
    - existing NiceGUI code is legacy, not the default place for new work
- **Core values**:
    - scientific accuracy
    - reproducible workflows
    - one canonical definition feeding UI, API, CLI, simulation, and schemdraw
- **Audience**: researchers, students, and developers working on superconducting-circuit simulation and analysis workflows.
```
