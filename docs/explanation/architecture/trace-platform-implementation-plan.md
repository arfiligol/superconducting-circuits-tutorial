---
aliases:
  - Trace Platform Implementation Plan
  - 設計/Trace 平台實作計畫
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/implementation
status: draft
owner: docs-team
audience: team
scope: Design/Trace/TraceStore architecture implementation plan and multi-agent execution split
version: v0.1.0
last_updated: 2026-03-08
updated_by: codex
---

# Trace Platform Implementation Plan

本頁不是 migration plan。  
它是這次架構重整的 **execution plan**，讓 Integrator / Contributors 在 context compaction 後仍能快速接手。

## Goal

把現有 `Dataset/DataRecord/ResultBundle + SQLite large payload` 的實作，收斂為：

- `DesignRecord`
- `TraceRecord`
- `TraceBatchRecord`
- `AnalysisRunRecord`
- `TraceStore` (`Zarr`)

並確保：

- Simulation
- Post-Processing
- Characterization
- JosephsonCircuits.jl 官方 examples

都能在新架構下端到端工作。

## Non-Goals

- 不做歷史資料 migration
- 不做舊資料雙寫長期維護
- 不先做 PostgreSQL deployment
- 不先做全部 layout/measurement ingest 重寫

## Success Criteria

1. JosephsonCircuits.jl 官方 examples 跑完後，能寫入新 metadata schema 與 Zarr TraceStore。
2. Simulation Result View 能從 `TraceRecord + TraceStore` 正常讀 raw sweep。
3. Post-Processing 能寫入新的 `TraceBatchRecord(stage=postprocess)` 與 post-processed traces。
4. Characterization 能直接吃新 `TraceRecord`，至少通過現有 circuit-simulation-derived examples。
5. 測試不再以舊 `DataRecord/ResultBundle` 名詞作為新功能新增的唯一 SoT。

## Workstreams

### Workstream A: Metadata Schema Rename + Contracts

目標：

- `DatasetRecord -> DesignRecord`
- `DataRecord -> TraceRecord`
- `ResultBundleRecord -> TraceBatchRecord`
- 明確引入 `AnalysisRunRecord`

重點：

- repository/UoW/contracts 同步收斂
- 名稱與責任邊界一致

### Workstream B: TraceStore (Zarr) Abstraction

目標：

- 實作 local `Zarr` baseline
- 導入 `TraceStoreRef`
- UI/service 不直接碰 backend-specific path logic

重點：

- chunked ND trace writes
- slice-first reads
- local backend 先落地
- contract 保留 S3-compatible extension

### Workstream C: Circuit Simulation Write Path

目標：

- raw simulation / sweep 寫入 `TraceBatchRecord + TraceRecord + TraceStore`
- post-processed outputs 也走同一條架構

重點：

- 不丟 sweep metadata
- raw 與 postprocess lineage 清楚
- examples 能跑通

### Workstream D: Result Views

目標：

- Simulation Results
- Post Processing Results

都能從新 `TraceRecord + TraceStore` 正常讀取與 compare。

重點：

- UI 不做 full-read then slice
- slice read 走 `TraceStore`
- 現有 compare interaction 保持可用

### Workstream E: Characterization

目標：

- Characterization 改為直接依賴新 `TraceRecord`
- 保留 trace-first
- 對 circuit-derived examples 完成驗證

重點：

- 不再依賴舊 storage shape 假設
- `2D Freq x L_jun` 路徑先確保通

## Recommended Multi-Agent Split

### 1. Metadata Contract Agent

Allowed Files:

- persistence models
- repository contracts
- repository tests
- data format docs

### 2. TraceStore Agent

Allowed Files:

- persistence database/store abstractions
- new TraceStore modules
- storage tests
- data handling / tech stack docs

### 3. Simulation Write Path Agent

Allowed Files:

- simulation page/service/application save path
- post-processing save path
- simulation tests / josephson E2E

### 4. Result View Agent

Allowed Files:

- simulation result-view code
- result-view tests / josephson E2E

### 5. Characterization Agent

Allowed Files:

- characterization page/services
- analysis-run integration
- characterization tests / E2E

## Integration Order

1. metadata contracts
2. TraceStore abstraction
3. simulation write path
4. result views
5. characterization

## Required Regression Set

最少必跑：

1. `uv run ruff check .`
2. `uv run pytest`
3. JosephsonCircuits.jl 官方 examples 對應的 app flows
4. 至少一條 post-processing sweep save + characterization regression

## Acceptance Notes for Integrator

- 先看 contract docs 是否被違反，再看 code
- 若 contributor 仍沿用舊名詞實作新功能，視為未完成收斂
- 若 UI 讀取 path 還是 full-read then slice，視為 TraceStore 任務未完成
- 若 examples 無法在新 schema 下產出完整 traces，視為寫入路徑未完成
