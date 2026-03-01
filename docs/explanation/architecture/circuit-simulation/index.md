---
aliases:
- Circuit Simulation Architecture
- 電路模擬架構
tags:
- diataxis/explanation
- audience/team
- topic/architecture
- topic/simulation
status: draft
owner: docs-team
audience: team
scope: Circuit Simulation 在 UI/CLI 的結構、即時預覽、語意映射與編輯器策略
version: v0.2.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Circuit Simulation

Circuit Simulation 區塊聚焦三件事：Schema 如何被編輯、如何被理解（Live Preview）、以及如何維持可維護的互動體驗。

!!! info "定位"
    這裡討論的是架構與設計理由（why）。實際操作流程請看 How-to / Tutorials。

## Topics

- [Circuit Schema Live Preview](../design-decisions/circuit-schema-live-preview.md)
  Netlist 到 SVG 的佈局契約、標註策略、Panzoom 狀態同步與非回歸準則。
- [Schema Editor Formatting](../design-decisions/schema-editor-formatting.md)
  CodeMirror 編輯體驗、Ruff WebAssembly 格式化路徑與觸發模型。
- [Live Preview Domain Semantics Profiles](../design-decisions/live-preview-domain-semantics.md)
  Qubit / JPA / JTWPA / Quantum Memory 的語意規則與視覺映射。
- [Simulation Result Views](simulation-result-views.md)
  Result Card 的多視圖契約、S/Gain/Z/Y/Complex family 與 selector 設計。

## Related

- [Architecture](../index.md)
- [Pipeline](../pipeline/index.md)
