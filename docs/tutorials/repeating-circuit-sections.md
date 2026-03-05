---
aliases:
  - Repeating Circuit Sections
  - 重複電路區段
tags:
  - diataxis/tutorial
  - audience/user
  - topic/netlist
status: stable
owner: docs-team
audience: user
scope: 使用 repeat 在 Source Form 中建立可維護的重複結構
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Repeating Circuit Sections

本頁說明如何在 Source Form 內使用 `repeat` 建立可重用拓樸與元件段落。

## 建議流程

1. 先寫一個可運行的顯式區段。
2. 抽取重複規律到 `repeat`：`count`、`start`、`emit`。
3. 在 Expanded Netlist Preview 驗證展開結果與索引。
4. 只儲存 Source Form，展開結果僅用於 preview 與 simulation。

## Related

- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Restricted Generators Rationale](../explanation/architecture/circuit-simulation/restricted-netlist-generators.md)
