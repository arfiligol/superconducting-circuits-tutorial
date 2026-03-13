---
aliases:
  - Circuit Netlist Getting Started
  - Netlist 入門
tags:
  - diataxis/tutorial
  - audience/user
  - topic/netlist
status: stable
owner: docs-team
audience: user
scope: Circuit Netlist Source Form 入門與最小可執行流程
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Circuit Netlist Getting Started

本頁提供最小化的 Circuit Netlist Source Form 入門路徑。

## 快速開始

1. 在 Schema Editor 建立 `name`、`components`、`topology`。
2. Ground node 只使用字串 `"0"`。
3. Component 僅可二選一：`default` 或 `value_ref`。
4. 於 Expanded Netlist Preview 檢查展開結果。

## Related

- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Schema Editor UI](../reference/app/frontend/definition/schema-editor.md)
- [From Netlist to Simulation](schematic-netlist-simulation.md)
