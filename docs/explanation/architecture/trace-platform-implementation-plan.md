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
version: v0.3.0
last_updated: 2026-03-08
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

### Phase 3 Active

接下來的工作重點不是再重做一次 schema，而是把已落地的新架構推進到：

- 更完整的 cross-source product workflow
- 更乾淨的 legacy cleanup
- 更可部署的 backend / operational boundary
- 更穩定的 examples-driven acceptance baseline

## Goal

讓系統真正達到：

- `DesignRecord` 成為統一 root container
- `TraceRecord` 成為 layout / circuit / measurement 的統一分析單位
- `TraceBatchRecord` 成為 import / simulation / preprocess / postprocess 的統一 provenance boundary
- `TraceStore` 不只 contract-ready，還要達到 server / object-storage operational readiness
- `Characterization` 對來源保持 source-agnostic，只依賴 trace compatibility
- 使用者可在同一個 `Design` scope 下穩定比較 layout / circuit / measurement traces

## Non-Goals

- 不做歷史資料 migration；physical schema 收斂時直接切到新 schema
- 不先重寫全部 UI hierarchy
- 不以 point-per-record 取代 canonical ND `TraceRecord`
- 不為了 phase-3 便利而把大型 numeric payload 回塞 metadata DB

## Success Criteria

1. `Design` scope 下可穩定完成 layout / circuit / measurement traces 的 cross-source browsing 與 compare workflow
2. phase-2 遺留的 legacy compatibility paths 有明確收斂策略，不再無限制保留 dual-write / dual-read
3. `TraceStore` backend boundary 對 local `Zarr` 已具備明確 operational entry points，未來 extension 不阻塞當前 phase
4. examples-driven regression 能覆蓋 circuit / layout / measurement 的 saved-trace reuse paths，而不是只驗證單一路徑
5. phase-3 驗收完成後，Integrator 能明確指出哪些 legacy names / compatibility layers 仍保留，哪些已退休

## Phase 3 Workstreams

### Workstream A: Cross-Source Product Workflow (Completed)

目標：

- 把 `Design` 從語意收斂推進到真正的 product workflow
- 讓使用者能在同一個 `Design` scope 內理解並操作：
  - circuit traces
  - layout traces
  - measurement traces
  - characterization outputs

重點：

- `Raw Data`
- `Characterization`
- trace selection / result navigation
- source compare / source summary / provenance visibility
- 不做大型頁面重排，但要把 cross-source compare 體驗補完整

已完成項目：

- `Raw Data` 已呈現 design-scoped source summary / compare readiness / trace provenance
- `Simulation` / `Post Processing` 已明確標示 inspect-only 與 save-then-compare 邊界
- `Characterization` 已在同一 design scope 下強化 source coverage / provenance / analysis-run history

剩餘擴張：

- 若要做更完整的 per-source side-by-side compare UI，可另開後續產品 workstream

### Workstream B: Legacy Cleanup and Persistence Convergence (Completed)

目標：

- 收斂 phase-2 為了安全整合而保留的 compatibility layers
- 明確決定哪些 dual-write / dual-read / legacy aliases 可以退休
- 讓 persistence / query / characterization / result-view 盡量共用同一套 canonical path

重點：

- legacy aliases vs canonical names
- trace-store authority vs inline fallback
- raw/postprocess/manual-save 等雙軌路徑
- 不要求 physical table rename，但要讓 logical contract 更單一路徑

已完成項目：

- `store_key` 已成為 canonical locator
- `store_uri` 明確降為 opaque compatibility/debug locator
- simulation write/read path 與 targeted regressions 已不再把 `store_uri` 當 primary local path source

剩餘擴張：

- physical schema rename / migration 仍 deferred，不在目前 phase-3 範圍

### Workstream C: TraceStore Operational Boundary (Completed)

目標：

- 把目前 backend abstraction 從 contract-ready 推進到可部署 readiness
- 讓 local 開發與後續 storage extension 的 boundary 更清楚

重點：

- `TraceStoreRef` contract 穩定
- backend-specific path logic 不外漏到 UI/app layer
- local filesystem 與 object storage layout 保持一致語意
- 不要求 live `s3_zarr` / MinIO / S3 integration
- local backend 必須是唯一 active、可驗證、可部署的 path

已完成項目：

- `local_zarr` runtime path 與 backend binding 已收斂
- UI / app layer 不應解析 backend-specific local path layout 的規則已進 guardrails

### Workstream D: Platform Acceptance Matrix (Active)

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
| TraceStore backend readiness | implemented | local backend 路徑穩定、可驗證、可支撐 app/examples | 若未來重新啟動 object-storage 擴張，再補 MinIO/S3 smoke tests |

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
- cross-cutting architecture docs when needed

### 2. Simulation Agent

主要承接：

- simulation page
- post-processing page
- result views
- simulation-oriented UX/performance/lifecycle
- Josephson examples E2E

### 3. Characterization Agent

主要承接：

- characterization page
- analysis services
- trace scope / trace compatibility
- characterization regressions
- cross-source compare behaviors when they center on analysis consumption

如有大型 docs-only、validation-only、或 infra-only 任務，可由 Integrator 臨時增派 specialist agent，但不應取代上述 3 位固定 contributors 的預設模式。

## Integration Order

1. legacy cleanup / canonical path convergence
2. TraceStore operational boundary
3. cross-source product workflow
4. platform acceptance matrix expansion

## Required Regression Set

最少必跑：

1. `uv run ruff check .`
2. targeted `pytest` for touched architecture slices
3. JosephsonCircuits.jl app flows
4. layout / measurement saved-trace reuse regression
5. characterization over saved traces regression
6. cross-source compare / scope regression（若本輪有碰）
7. TraceStore backend-boundary regression（local 必跑）

## Acceptance Notes for Integrator

- 已完成的 phase-1 / phase-2 workstreams 不要重新打開，除非 phase-3 明確需要擴張其 contract
- 優先檢查 contributor 是否仍引入新的 legacy naming 或新的 dual-path 寫法
- 若 ingest / UI / characterization 仍主要依賴 metadata DB inline payload，而不是 TraceStore authority，視為未符合架構
- 若 UI/app layer 直接碰 backend-specific TraceStore path，視為 backend boundary 未完成
- 若 validation 仍只證明單一路徑，而未覆蓋 cross-source trace model，視為 phase-3 未完成
