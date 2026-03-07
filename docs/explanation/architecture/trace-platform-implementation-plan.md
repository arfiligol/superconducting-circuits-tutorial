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
scope: Design/Trace/TraceStore architecture phase-2 execution plan and multi-agent execution split
version: v0.2.0
last_updated: 2026-03-08
updated_by: codex
---

# Trace Platform Implementation Plan

本頁不是 migration plan。  
它是 **下一階段 active execution plan**，讓 Integrator / Contributors 在 context compaction 後能直接接手。

## Phase Status

### Phase 1 Completed

以下基礎工作已完成並進入 `main`：

- SoT docs / guardrails / architecture terminology 已切到 `DesignRecord / TraceRecord / TraceBatchRecord / TraceStore`
- persistence contract 已有 canonical naming，並保留 legacy aliases
- local `Zarr` TraceStore baseline 已落地
- circuit simulation write path 已能把 numeric payload 寫入 local TraceStore
- simulation result views 已能從 `TraceRecord + TraceStore` authority 讀取
- characterization consumer 已能接受新 `TraceRecord`-like contract
- JosephsonCircuits.jl examples 已覆蓋新 write/read path 的核心回歸

本頁不再重複列出上述已完成 workstreams。

### Phase 2 Active

接下來的工作重點是把「circuit simulation 已打通的新架構」擴展為完整平台語意。

## Goal

讓系統真正達到：

- `DesignRecord` 成為統一 root container
- `TraceRecord` 成為 layout / circuit / measurement 的統一分析單位
- `TraceBatchRecord` 成為 import / simulation / preprocess / postprocess 的統一 provenance boundary
- `TraceStore` 保持 local-first，但 backend abstraction 明確支援未來 `S3 / MinIO` extension
- `Characterization` 對來源保持 source-agnostic，只依賴 trace compatibility

## Non-Goals

- 不做歷史資料 migration
- 不做 DB physical table rename / migration
- 不先做 live S3/MinIO integration
- 不先重寫全部 UI hierarchy
- 不以 point-per-record 取代 canonical ND `TraceRecord`

## Success Criteria

1. `Raw Data` / `Characterization` / 相關 UI 主要語言收斂到 `Design / Trace / Trace Batch`
2. layout / measurement ingest 也能寫入 `TraceBatchRecord + TraceRecord + TraceStore`
3. Characterization 對 layout / circuit / measurement 三種來源維持同一套 trace-first model
4. TraceStore backend abstraction 對 local 與 `s3_zarr` 都有正式 contract
5. examples-driven regression 不再只覆蓋 circuit simulation，也覆蓋 ingest + characterize path

## Active Workstreams

### Workstream A: Product Vocabulary and UI Semantics

目標：

- 將使用者可見語言從 `Dataset/DataRecord/ResultBundle` 收斂到：
  - `Design`
  - `Trace`
  - `Trace Batch`
- 清掉 UI / docs / service layer 中殘留的舊語意

重點：

- `Raw Data`
- `Characterization`
- trace selection / result navigation
- 只改語意與查詢介面，不做大型頁面重排

### Workstream B: Layout and Measurement Ingest

目標：

- layout simulation ingest
- measurement ingest

都能產出：

- `TraceBatchRecord`
- `TraceRecord`
- `TraceStore` payload

重點：

- import contract generalized
- trace-first materialization
- 與 circuit simulation 同一 characterization path

### Workstream C: TraceStore Backend Boundary

目標：

- 把目前 local `Zarr` baseline 收斂成正式 backend abstraction
- contract 明確支持：
  - `local_zarr`
  - `s3_zarr`

重點：

- `TraceStoreRef` contract 穩定
- backend-specific path logic 不外漏到 UI/app layer
- local filesystem 與 object storage layout 保持一致語意

### Workstream D: Analysis Run Persistence Decision

目標：

- 決定 `AnalysisRunRecord` 是否維持 contract-only
- 或升級成正式 persistence object

重點：

- characterization history
- run provenance
- result navigation
- 與 `TraceBatchRecord` 的責任切分

Decision target for this workstream：

- Current
  - Characterization 寫入已落在 metadata DB，但 UI / page helper 仍直接操作 `TraceBatchRecord(bundle_type="characterization", role="analysis_run")`
  - `AnalysisRunRecord` 仍缺正式 repository boundary，因此 history / result navigation 仍容易退回 batch semantics
- Target
  - 以 `AnalysisRunRecord` 作為 logical persistence contract
  - 透過 repository adapter 將其持久化到既有 `TraceBatchRecord(bundle_type="characterization", role="analysis_run")`
  - Characterization UI 改讀寫 analysis-run repository，而不是直接組 generic batch row
  - `TraceBatchRecord` 繼續負責 import / simulation / postprocess provenance，不吸收 run-specific execution semantics
- Why this is safe now
  - 不需要 migration
  - 不需要新增 physical table
  - 不會把大型 numeric payload 放回 metadata DB
  - 不會把 canonical `TraceRecord` 退回 point-per-record
- Deferred
  - 若未來需要獨立 physical table，再另開 migration workstream；這不屬於本 phase-2 task

### Workstream E: Examples-Driven Validation Matrix

目標：

- 建立下一階段的正式 regression matrix

至少包含：

- circuit simulation examples
- post-process save/read
- characterization over saved traces
- layout/measurement ingest path（當其落地後）

## Recommended Multi-Agent Split

### 1. Design Semantics Agent

Allowed Files:

- raw-data / characterization UI
- trace scope / selection services
- related docs / tests

### 2. Layout Ingest Agent

Allowed Files:

- layout import / preprocess services
- persistence write path
- ingest tests

### 3. Measurement Ingest Agent

Allowed Files:

- measurement import / preprocess services
- persistence write path
- ingest tests

### 4. TraceStore Backend Agent

Allowed Files:

- TraceStore abstraction
- storage contracts
- backend tests
- data handling / tech stack docs if needed

### 5. Analysis Run Contract Agent

Allowed Files:

- characterization persistence contracts
- analysis run repositories / docs / tests

### 6. Validation Matrix Agent

Allowed Files:

- examples-driven E2E / integration tests
- supporting fixtures only

## Integration Order

1. product vocabulary / UI semantics
2. TraceStore backend boundary
3. layout ingest
4. measurement ingest
5. analysis-run persistence decision
6. validation matrix expansion

## Required Regression Set

最少必跑：

1. `uv run ruff check .`
2. targeted `pytest` for touched architecture slices
3. JosephsonCircuits.jl app flows
4. 新增 ingest path 的 trace write/read regression
5. characterization over saved traces regression

## Acceptance Notes for Integrator

- 已完成的 phase-1 workstreams 不要重新打開，除非新 phase 明確需要擴張其 contract
- 優先檢查 contributor 是否仍引入新的 legacy naming
- 若 ingest path 仍把大型 numeric payload 主要存進 metadata DB，視為未符合架構
- 若 UI/app layer 直接碰 backend-specific TraceStore path，視為 backend boundary 未完成
- 若 validation 仍只證明「circuit simulation 可跑」，而未覆蓋 cross-source trace model，視為 phase-2 未完成
