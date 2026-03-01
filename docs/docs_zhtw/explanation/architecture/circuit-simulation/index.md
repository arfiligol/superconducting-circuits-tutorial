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
scope: Circuit Simulation 的架構索引，聚焦 Schematic Netlist、Live Preview、Simulation Compiler 與結果視圖的設計理由
version: v0.3.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Circuit Simulation

Circuit Simulation 現在以 `Schematic Netlist` 為中心，而不是以舊的 tuple-style `topology` 為中心。

它討論的是：

1. 為什麼需要新的語言層
2. 為什麼 Live Preview 與 Simulation 必須共用同一個 SoT
3. 為什麼 `Schemdraw` 只能是 renderer，而不能是 layout engine

!!! info "定位"
    這裡解釋的是架構與決策理由（why）。正式欄位與規格請以 Reference 為準。

## Core Direction

- **單一 SoT**：使用者在 Editor 寫的是 `Schematic Netlist`
- **雙路輸出**：同一份 SoT 同時編譯到 Live Preview 與 Simulation
- **分層 pipeline**：`Parse → Validate → IR → LayoutPlan / Compiler → Emit`

## Topics

- [LayoutPlan 與 Renderer 邊界](layout-plan-and-renderer-boundaries.md)
  - 定義 `LayoutPlan`、`Schemdraw` 與 `SVG viewBox` 互動層的責任邊界。
- [Schematic Netlist Live Preview](../design-decisions/circuit-schema-live-preview.md)
  - 定義 Live Preview 為什麼必須引入 `IR` 與 `LayoutPlan`，以及 `Schemdraw` 的責任邊界。
- [Schema Editor Formatting](../design-decisions/schema-editor-formatting.md)
  - 定義 Editor 如何穩定編輯 `Schematic Netlist`，以及 Ruff WASM 的格式化路徑。
- [Live Preview Domain Semantics Profiles](../design-decisions/live-preview-domain-semantics.md)
  - 定義 Qubit / JPA / JTWPA 等領域語意如何影響 `LayoutPlan`。
- [Simulation Result Views](simulation-result-views.md)
  - 定義 Result Card 的多視圖模型與 mode-aware 資料切換。

## Related

- [Architecture Reference / Schematic Netlist Core](../../../reference/architecture/schematic-netlist-core.md)
- [Architecture](../index.md)
- [Pipeline](../pipeline/index.md)
