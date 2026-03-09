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
scope: Design/Trace/TraceStore architecture phase-3 execution plan and multi-agent execution split
version: v0.4.0
last_updated: 2026-03-09
updated_by: codex
---

# Trace Platform Implementation Plan

本頁不是 migration plan。  
它是 **下一階段 active execution plan**，讓 Integrator / Contributors 在 context compaction 後能直接接手。

!!! important "Current active decisions"
    - `TraceStore` 目前只以 local `Zarr` 為 active backend。
    - `s3_zarr` / MinIO / S3 是 deferred extension，不是當前 phase 的 blocking target。
    - 當 physical schema 收斂開始時，不做歷史資料 migration；直接切到新 schema。

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

### Phase 2 Completed

以下 phase-2 workstreams 已完成並進入 `main`：

- `Raw Data` / `Characterization` 的主要使用者語言已收斂到 `Design / Trace / Trace Batch`
- layout ingest 與 measurement ingest 已能寫入 `TraceBatchRecord + TraceRecord + TraceStore`
- `TraceStoreRef` 已收斂出 local-first backend contract，並保留 `s3_zarr` extension-safe shape
- `AnalysisRunRecord` 已落地為 logical persistence boundary
- examples-driven validation matrix 已建立 phase-2 基礎骨架

### Phase 3 Completed

以下 phase-3 workstreams 已完成並進入 `main`：

- cross-source product workflow 第一批 UX / provenance / scope 已完成
- local-only TraceStore operational boundary 已收斂
- major legacy cleanup 已完成到不再阻塞 phase-4
- cached result / sweep write path 已收斂到 slice-first 與 incremental persist 基線

### Phase 4 Active

接下來的重點不是再擴 schema 名詞，而是把整個執行模型收斂成 persisted orchestration：

- `Simulation` 不再依賴 live session result state
- `Post Processing` 不再依賴 page-local latest raw result
- UI / CLI 都只建立 persisted execution boundary
- backend workers 只讀 persisted metadata DB + TraceStore
- cache hit 只是 optimization，不影響 workflow authority

## Goal

讓系統真正達到：

- `DesignRecord` 成為統一 root container
- `TraceRecord` 成為 layout / circuit / measurement 的統一分析單位
- `TraceBatchRecord` 成為 import / simulation / preprocess / postprocess 的統一 provenance boundary
- `TraceStore` 不只 contract-ready，還要達到 server / object-storage operational readiness
- `Characterization` 對來源保持 source-agnostic，只依賴 trace compatibility
- 使用者可在同一個 `Design` scope 下穩定比較 layout / circuit / measurement traces
- `Simulation` / `Post Processing` / `Characterization` 都可由 UI 或 CLI 以同一套 persisted contract 啟動

## Non-Goals

- 不做歷史資料 migration；physical schema 收斂時直接切到新 schema
- 不先重寫全部 UI hierarchy
- 不以 point-per-record 取代 canonical ND `TraceRecord`
- 不為了 phase-3 便利而把大型 numeric payload 回塞 metadata DB
- 不把 numeric payload 的 authority 從 TraceStore 搬回 metadata DB

## Success Criteria

1. `Simulation` / `Post Processing` / `Characterization` 都能由 persisted run boundary 啟動，不依賴 live session authority
2. saved raw simulation batch 可以在沒有 live simulation session 的情況下重新進入 post-processing
3. cache hit 只縮短 run path，不會造成 workflow 能力差異
4. UI 與 CLI 對同一 run contract 共享同一套 persisted orchestration semantics
5. examples-driven regression 能覆蓋 circuit / layout / measurement 的 saved-trace reuse paths

## Phase 4 Workstreams

### Workstream A: Persisted Orchestration for Trace-Producing Flows (Active)

目標：

- 把 `Simulation` / `Post Processing` 從 page-local live session orchestration 收斂成 persisted orchestration
- 讓 UI / CLI 都只建立 persisted execution boundary，再由 backend worker 執行

重點：

- `TraceBatchRecord(status=running/completed/failed)` 作為 trace-producing execution boundary
- `setup_payload` / `provenance_payload` 明確表達 input batch / source refs / progress
- saved raw batch 可直接重新 post-process
- cache hit 只做 optimization，不得改變 authority 來源

最低完成標準：

- `Run Simulation` 建立 persisted raw batch，逐點寫入 TraceStore
- `Run Post Processing` 以 persisted input batch 為輸入，而不是 `latest_simulation_result`
- live session 斷線後，run 仍可由 persisted state 繼續查詢 / 驗證

本 workstream 目前的 immediate TODO 是：

- `/simulation` 在 design selection 改變時，優先解析 persisted raw batch / persisted postprocess batch
- `Simulation Results` / `Post Processing Results` 優先從 persisted batch authority 讀取
- `Run Post Processing` 對 saved raw batch 與 saved postprocess batch 的 rerun，不再依賴 page-local `latest_*` state
- live session state 只保留為短期 preview / just-finished run bridge，不再是唯一 workflow authority

### Workstream B: Persisted Orchestration for Analysis Flows (Planned)

目標：

- 把 `Characterization` 與 phase-4 trace-producing flows 對齊到完全 sessionless 的 persisted execution model

重點：

- `AnalysisRunRecord` 與 `TraceBatchRecord` 的關係清晰
- UI / CLI 對 analysis run 共享同一套 persisted semantics
- result navigation / run history / rerun 行為不依賴 page-local state

### Workstream C: Platform Acceptance Matrix (Active)

目標：

- 把 examples-driven validation matrix 從 phase-2 骨架擴張成 phase-3 acceptance baseline
- 不只驗證 circuit simulation，而是驗證整個設計平台的核心 reuse 路徑

重點：

- circuit simulation -> save/read -> characterize
- layout ingest -> save/read -> characterize
- measurement ingest -> save/read -> characterize
- cross-source compare in same `Design`
- TraceStore local vs backend-boundary readiness

| Scenario | 目前狀態 | 最低驗證重點 | 後續擴張點 |
|---|---|---|---|
| circuit simulation -> save/read -> characterize | implemented | saved traces 能重讀、能再進 characterization、能保留 provenance | 擴張更多 JosephsonCircuits example families / sweep variants |
| postprocess -> save/read -> characterize | implemented | post-processed traces 可保存、重讀、再次進 characterization / result navigation | 擴張更多 pipeline steps / matrix families |
| layout ingest -> save/read -> characterize | implemented | layout traces 以 trace-store path 寫入並可被 characterization 消費 | 補 full browser/E2E path |
| measurement ingest -> save/read -> characterize | implemented | measurement traces 以 trace-store path 寫入並可被 characterization 消費 | 補更多 matrix family coverage |
| cross-source compare within one design | implemented | 同一 design scope 下能同時顯示來源 summary / provenance / compatibility gating | 補更完整 per-source difference UX 與 compare assertions |
| persisted simulation run | active | save-only / cache-hit / rerun / reconnect 後仍能從 persisted batch 繼續 | 補 CLI/shared command contract |
| persisted post-processing run | active | saved raw batch 可直接重新 post-process；不依賴 live session | 補 CLI/shared command contract |

約束：

- 不要把 validation matrix 重新退回「只驗證 circuit simulation 能跑」
- 不要用假 fixture 取代真實 cross-source reuse path
- characterization coverage 應優先驗證「saved traces 可被再利用」，而不是重複驗證 phase-1 的單次 simulation 成功訊息

## Recommended Multi-Agent Split

Phase 3 預設維持 **3 位固定 Contributor Agents**，由 Integrator 每輪在 prompt 內細化 `Allowed Files` 與 bridge 邊界。

### 1. Platform Agent

主要承接：

- persistence contracts
- TraceStore backend
- ingest write paths
- lineage / query / metadata convergence
- persisted execution boundaries
- cross-cutting architecture docs when needed

### 2. Simulation Agent

主要承接：

- simulation page
- post-processing page
- result views
- simulation-oriented UX/performance/lifecycle
- Josephson examples E2E
- persisted orchestration UI/CLI bridge

### 3. Characterization Agent

主要承接：

- characterization page
- analysis services
- trace scope / trace compatibility
- characterization regressions
- cross-source compare behaviors when they center on analysis consumption
- persisted analysis-run semantics

如有大型 docs-only、validation-only、或 infra-only 任務，可由 Integrator 臨時增派 specialist agent，但不應取代上述 3 位固定 contributors 的預設模式。

## Integration Order

1. persisted trace-producing orchestration
2. persisted analysis orchestration
3. platform acceptance matrix expansion

## Required Regression Set

最少必跑：

1. `uv run ruff check .`
2. targeted `pytest` for touched architecture slices
3. JosephsonCircuits.jl app flows
4. saved raw batch -> post-processing rerun regression
5. layout / measurement saved-trace reuse regression
6. characterization over saved traces regression
7. cross-source compare / scope regression（若本輪有碰）
8. TraceStore backend-boundary regression（local 必跑）

## Acceptance Notes for Integrator

- 已完成的 phase-1 / phase-2 / phase-3 workstreams 不要重新打開，除非 phase-4 明確需要擴張其 contract
- 優先檢查 contributor 是否仍引入新的 legacy naming 或新的 dual-path 寫法
- 若 ingest / UI / characterization 仍主要依賴 metadata DB inline payload，而不是 TraceStore authority，視為未符合架構
- 若 UI/app layer 直接碰 backend-specific TraceStore path，視為 backend boundary 未完成
- 若 `Simulation` / `Post Processing` 仍依賴 page-local latest-result state，而不是 persisted input batch，視為 phase-4 未完成
