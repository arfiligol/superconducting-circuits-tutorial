---
aliases:
  - Schema Editor
  - Schematic Netlist Editor
  - Schema 編輯器
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/ui
  - topic/visualization
status: draft
owner: docs-team
audience: user
scope: /schemas/{id} 的 Code Editor、Format、Save、Live Preview 與錯誤恢復行為規格
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Schema Editor

本頁描述 `/schemas/{id}` 的 UI 契約。

## Page Sections

1. `Circuit Definition`
2. `Live Preview`
3. `Component & Unit Reference`

## Circuit Definition

### Editor Model

- 輸入格式：`Schematic Netlist v0.1`
- 允許的文字風格：
  - JSON 風格
  - Python literal 風格（例如尾逗號）

### Format

- `Format` 會整理目前 editor 內容
- 若 browser formatter 可用，優先用 browser-side formatter
- 若 browser formatter 不可用，回退到後端 canonical formatter

### Save Schema

- `Save Schema` 會保存**目前 editor 中的文字**
- 對於已是 `v0.1` 的 schema：不會在存檔時重新排版
- 對於 legacy tuple schema：讀取時會先 migration，再以 canonical 格式存回

## Live Preview

- Pipeline：`Parse → Validate → CircuitIR → LayoutPlan → Schemdraw SVG`
- 若 parse / validate 失敗：
  - 保留上一張成功圖
  - 顯示錯誤狀態
  - 不清空預覽容器

### Interaction

- `+`
- `-`
- `Reset`
- 拖曳平移
- 滾輪平移
- `Ctrl/Cmd + 滾輪` 縮放

### Zoom Semantics

- `100%` = 完整顯示整個電路
- 最大放大 = `2000%`

## Common User Expectations

### If you want stable preview output

優先調整：

1. `pins`
2. `role`
3. `layout.profile`

而不是先調數值。

## Related

- [Circuit Simulation](circuit-simulation.md)
- [Schematic Netlist Core](../architecture/schematic-netlist-core.md)
- [Schematic Netlist Live Preview](../../explanation/architecture/design-decisions/circuit-schema-live-preview.md)
