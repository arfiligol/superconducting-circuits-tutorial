---
aliases:
  - Architecture Reference
  - 架構參考
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
status: stable
owner: docs-team
audience: team
scope: 架構層的 owner boundary、cross-layer registry 與 App/CLI/Core/Data Formats 對齊關係
version: v0.6.0
last_updated: 2026-03-14
updated_by: team
---

# Architecture Reference

本區定義系統架構層真正需要保留的正式 SoT：owner boundary、cross-layer registry 與 alignment。

!!! info "How To Read Architecture Docs"
    若你要回答的是 page layout、app-shared semantics、backend surface、CLI usage 或 data payload 細節，先回到對應的 `App / CLI / Core / Data Formats` reference。
    本區只處理 cross-layer ownership、registry 與 alignment。

!!! warning "Architecture 不是 Implementation Notes"
    若某一頁主要在描述資料格式、core package family、task runtime 細節或 app surface，它就不應留在 Architecture。
    Architecture 只保留真正跨層的 owner / registry / parity 文件。

## Page Map

| Page | Core focus | Main pairing |
|---|---|---|
| [Canonical Contract Registry](canonical-contract-registry.md) | cross-layer canonical contracts 與 owner registry | App, CLI, Core, Data Formats |
| [Parity Matrix](parity-matrix.md) | App / CLI / Core / Data Formats 對齊狀態 | 全部 reference surfaces |

## Related Layers

| Layer | What it answers |
|---|---|
| [App / Shared](../app/shared/index.md) | workspace collaboration、auth、runtime、audit 等 app-shared semantics |
| [App / Frontend](../app/frontend/index.md) | 頁面與 shared shell 怎麼呈現 |
| [App / Backend](../app/backend/index.md) | frontend 直接依賴哪些 backend surfaces |
| [Core](../core/index.md) | installable core contracts、Python/Julia bridge 與 package boundaries |
| [CLI Options](../cli/index.md) | standalone-first CLI 與 local runtime contract |

## Related

* [App / Shared](../app/shared/index.md)
* [App / Frontend](../app/frontend/index.md)
* [App / Backend](../app/backend/index.md)
* [CLI Options](../cli/index.md)
* [Core Reference](../core/index.md)
* [Data Formats](../data-formats/index.md)
