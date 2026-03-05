---
aliases:
  - Circuit Netlist Core
  - 電路 Netlist 核心
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
  - topic/netlist
status: stable
owner: docs-team
audience: team
scope: Circuit Netlist source->expanded pipeline 與驗證規則的核心契約
version: v0.1.0
last_updated: 2026-03-05
updated_by: codex
---

# Circuit Netlist Core

本頁定義 Circuit Netlist 在應用中的核心架構契約。

## Core Contract

- **Source Form**：儲存於 DB，允許 `repeat`。
- **Expanded Form**：執行時展開結果，用於 preview 與 simulation。
- **Single Pipeline**：Schema Preview 與 Simulation Configuration 使用同一展開鏈路。

## Validation Highlights

- ground token 僅允許 `"0"`。
- `components[*]` 需 `name`、`unit`，且必須擇一 `default` / `value_ref`。
- `topology` row 必須引用存在 component 或合法 port index。
- `repeat` 展開後仍需通過完整 netlist 驗證。

## Related

- [Circuit Netlist Format](../data-formats/circuit-netlist.md)
- [Restricted Netlist Generators](../../explanation/architecture/circuit-simulation/restricted-netlist-generators.md)
