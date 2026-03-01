---
aliases:
  - LayoutPlan 與 Renderer 邊界
  - LayoutPlan and Renderer Boundaries
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/visualization
status: draft
owner: docs-team
audience: team
scope: 解釋為什麼使用者必須先寫對語意結構，Live Preview 才能穩定，且這個責任不應落在 Schemdraw 上
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# LayoutPlan 與 Renderer 邊界

本頁回答一個常見問題：

> 為什麼我明明把元件都寫上了，Preview 卻沒有照我心裡想的樣子畫？

答案是：因為 `Schemdraw` 不是 graph layout engine，而 `LayoutPlan` 只能根據你提供的結構語意做穩定推理。

## 真正的責任分工

- `Schematic Netlist`：表達你想要的電路語意
- `CircuitIR`：把語意轉成可推理的內部結構
- `LayoutPlan`：決定 backbone、branch、label slots、draw order
- `Schemdraw`：依照 `LayoutPlan` 命令式繪圖

## 什麼是使用者可以控制的

使用者真正能控制的是：

1. `pins`（節點關係）
2. `role`（語意角色）
3. `layout.direction`
4. `layout.profile`

這四件事決定了 `LayoutPlan` 的輸入品質。

## 什麼不是 Schemdraw 的責任

以下事情不應該期待由 `Schemdraw` 自動猜出：

- 哪兩個元件其實是同一組 parallel branch
- 哪條是主幹、哪條是支路
- 哪個 port 是 signal、哪個是 pump
- 哪種圖在 JPA / JTWPA / qubit 中才算可讀

## 對 Tutorial 的意義

這就是為什麼 Tutorial 會先教：

- 節點關係
- `series / shunt / parallel branch`
- `Port / Source / Mode`
- `layout.profile`

因為這些才是讓 Preview 接近使用者意圖的根本。

## Related

- [Schematic Netlist Core](../../../reference/architecture/schematic-netlist-core.md)
- [Schematic Netlist Live Preview](../design-decisions/circuit-schema-live-preview.md)
- [Live Preview Domain Semantics Profiles](../design-decisions/live-preview-domain-semantics.md)
