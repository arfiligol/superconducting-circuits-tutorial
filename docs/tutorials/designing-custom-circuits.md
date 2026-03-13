---
aliases:
  - Designing Custom Circuits
  - 自訂電路設計
tags:
  - diataxis/tutorial
  - audience/user
  - topic/circuit-design
status: stable
owner: docs-team
audience: user
scope: 自訂電路從 source netlist 到可模擬 setup 的設計指引
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Designing Custom Circuits

本頁聚焦自訂電路時的設計與驗證清單。

## Checklist

1. `components` 先定義可重用參數接口（`default`/`value_ref`）。
2. `topology` 僅處理連線，不混入參數語意。
3. 優先使用 `repeat` 降低展開後維護成本。
4. 用 Expanded Netlist Preview 做 deterministic 驗證。
5. 在 Simulation 端先驗證 base mode，再開 sideband/post-processing。

## Related

- [Circuit Netlist](../reference/data-formats/circuit-netlist.md)
- [Schema Editor UI](../reference/app/frontend/definition/schema-editor.md)
- [Simulation Workflow](simulation-workflow.md)
