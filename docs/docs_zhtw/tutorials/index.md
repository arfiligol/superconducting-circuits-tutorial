---
aliases:
- Tutorials
- 教學
tags:
- diataxis/tutorial
- audience/user
- topic/schematic-netlist
status: draft
owner: docs-team
audience: user
scope: WebUI 中 Schematic Netlist 的學習路徑與教學入口
version: v0.2.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Tutorials

本區提供以 WebUI 為中心的教學路徑，目標是讓你從不會到能獨立寫出 `Schematic Netlist v0.1`、看到穩定的 Live Preview，並成功完成 Simulation。

!!! info "Diataxis 位置"
    這裡只放操作教學（how to learn by doing）。欄位規格請看 [Schematic Netlist Core](../reference/architecture/schematic-netlist-core.md)，設計理由請看 [Circuit Simulation](../explanation/architecture/circuit-simulation/index.md)。

## Recommended Learning Path

1. [Schematic Netlist Getting Started](schematic-netlist-getting-started.md)  
   第一次成功：寫出最小可用電路、Format、Save、進入 Simulation。
2. [From Preview to Simulation](schematic-netlist-simulation.md)  
   釐清 `Port`、`Applied Sources`、`HB Mode` 與 Result Views。
3. [Understand Live Preview](schematic-netlist-live-preview.md)  
   學會預測 `Schemdraw` 會怎麼畫，以及哪些結構需要語意提示。
4. [Designing Custom Circuits](designing-custom-circuits.md)  
   從需求出發，自行設計可預覽、可模擬的自訂電路。

## Supporting References

- [Schematic Netlist Core](../reference/architecture/schematic-netlist-core.md)
- [Schematic Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [Circuit Simulation](../reference/ui/circuit-simulation.md)

## Supporting Explanations

- [Circuit Simulation](../explanation/architecture/circuit-simulation/index.md)
- [LayoutPlan 與 Renderer 邊界](../explanation/architecture/circuit-simulation/layout-plan-and-renderer-boundaries.md)
- [Schematic Netlist Live Preview](../explanation/architecture/design-decisions/circuit-schema-live-preview.md)

## Legacy Tutorials

下列教學仍保留，但不屬於新的 `Schematic Netlist` 主學習路徑：

- [End-to-End Fitting](end-to-end-fitting.md)
- [Simulation Workflow](simulation-workflow.md)
- [LC Resonator](lc-resonator.md)
- [Parameter Sweep](parameter-sweep.md)
- [Resonance Fitting](resonance-fitting.md)
- [Flux Analysis](flux-analysis.md)
