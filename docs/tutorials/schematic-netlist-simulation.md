---
aliases:
  - From Netlist to Simulation
  - Netlist 到模擬
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
status: stable
owner: docs-team
audience: user
scope: 從 Schema Source Form 到 Simulation Result 的操作流程
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# From Netlist to Simulation

本頁串接 Schema 與 Simulation 的最短操作路徑。

## 流程

1. 在 Schema Editor 撰寫 Source Form，儲存 schema。
2. 於 Simulation 頁確認 Expanded Netlist Configuration。
3. 設定 sources、solver options、必要時設定 post-processing。
4. 執行 simulation，檢視 Raw / Post-Processed Result View。

## Related

- [Schema Editor UI](../reference/app/frontend/definition/schema-editor.md)
- [Circuit Simulation UI](../reference/app/frontend/research-workflow/circuit-simulation.md)
- [Analysis Result Data Contract](../reference/data-formats/analysis-result.md)
