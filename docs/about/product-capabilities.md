---
aliases:
  - Product Capabilities
  - 產品能力
tags:
  - diataxis/explanation
  - audience/public
status: draft
owner: docs-team
audience: public
scope: 以產品敘事方式描述本專案的最終能力與研究工作流目標。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# Product Capabilities

這個應用的目標，是建立一個以 `sc_core` 為中心、同時支援 UI / CLI / task / trace / provenance 的超導電路研究工作平台。

## One Research Workspace

研究者應能在同一套系統中完成：

- circuit definition 撰寫與驗證
- schemdraw 與視覺化
- simulation 與後處理
- characterization 與參數萃取
- dataset / trace / result / provenance 管理
- task 追蹤、回看與重建

## Data And Trace Management

本系統強調清楚的資料邊界：

- metadata 由 database 管理
- numeric trace payload 由 TraceStore 管理
- dataset / trace / result / analysis linkage 必須明確
- 結果應可追溯、可比較、可重建

## UI And CLI Parity

這個產品不以單一入口獨占工作流。

- UI 提供完整互動式工作台
- CLI 提供本地研究者 workflow、批次處理與自動化入口
- 同一份 canonical contract 應同時支援 UI、CLI、backend 與 worker

## Recovery And Reliability

本產品不只要求功能能跑，還要求研究流程可恢復：

- refresh 後可恢復 active dataset
- task 執行中可重新 attach
- result view 可從 persisted contract 重建
- 不依賴 in-memory UI state 才能理解結果

## Final Goal

最終成功條件只有一個：

**legacy NiceGUI + 既有 CLI 能做到的事，重構後都能做到。**

## Related

- [Parity Matrix](../reference/architecture/parity-matrix.md)
- [CLI Reference](../reference/cli/index.md)
- [App Reference](../reference/ui/index.md)
- [Project Overview](../reference/guardrails/project-basics/project-overview.md)
