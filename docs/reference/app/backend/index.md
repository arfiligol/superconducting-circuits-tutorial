---
aliases:
  - Backend App Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Backend app reference 索引，收錄 frontend 與 CLI 依賴的 backend reference surface。
version: v0.6.0
last_updated: 2026-03-13
updated_by: team
---

# Backend Reference

本區收錄 backend app layer 的可查詢規格，描述 frontend、CLI 與 backend service layer 在對齊時所依賴的 reference surface。

!!! info "How To Read Backend App Docs"
    先讀 `Foundation` 釐清 session、definition、dataset 等共用 authority，再讀 `Workflow` 了解 task、render、analysis result 這些流程型 surface。

!!! tip "Read With Frontend Reference"
    Backend reference 不描述頁面排版，而是定義 app surfaces。
    最穩定的閱讀方式是將本頁與 [Frontend Reference](../frontend/index.md) 對照著看。

!!! warning "Boundary"
    本區定義的是 backend authority surface，不是 API tutorial，也不是頁面互動說明。
    若你要看的是使用者如何操作頁面，請先回到 frontend page specs。

---

## Surface Map

=== "Foundation"

    | Surface | 主要消費者 | 核心聚焦 |
    |---|---|---|
    | [Session & Workspace](session-workspace.md) | Dashboard, Raw Data Browser, Circuit Simulation | active dataset、workspace scope、capability exposure |
    | [Circuit Definitions](circuit-definitions.md) | Schemas, Schema Editor, Schemdraw, Circuit Simulation | definition catalog、detail、mutation、persisted preview |
    | [Datasets & Results](datasets-results.md) | Dashboard, Raw Data Browser, Characterization, Circuit Simulation | design browse、trace preview、dataset profile、tagged metrics summary、result handles |

=== "Workflow"

    | Surface | 主要消費者 | 核心聚焦 |
    |---|---|---|
    | [Tasks & Execution](tasks-execution.md) | Circuit Simulation, Characterization | task submission、status、event history、result attachment |
    | [Schemdraw Render](schemdraw-render.md) | Schemdraw | debounced render request、diagnostics、SVG response |
    | [Characterization Results](characterization-results.md) | Characterization, Dashboard | run history、artifact manifest、artifact payload、identify/tagging |

---

## Frontend Pairing

| Frontend page | Backend authority |
|---|---|
| [Dashboard](../frontend/workspace/dashboard.md) | [Session & Workspace](session-workspace.md), [Datasets & Results](datasets-results.md), [Characterization Results](characterization-results.md) |
| [Raw Data Browser](../frontend/workspace/raw-data-browser.md) | [Datasets & Results](datasets-results.md) |
| [Schemas](../frontend/definition/schemas.md) | [Circuit Definitions](circuit-definitions.md) |
| [Schema Editor](../frontend/definition/schema-editor.md) | [Circuit Definitions](circuit-definitions.md) |
| [Schemdraw](../frontend/research-workflow/schemdraw.md) | [Circuit Definitions](circuit-definitions.md), [Schemdraw Render](schemdraw-render.md) |
| [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md) | [Circuit Definitions](circuit-definitions.md), [Tasks & Execution](tasks-execution.md), [Datasets & Results](datasets-results.md) |
| [Characterization](../frontend/research-workflow/characterization.md) | [Datasets & Results](datasets-results.md), [Tasks & Execution](tasks-execution.md), [Characterization Results](characterization-results.md) |

!!! success "Current App Coverage"
    目前 frontend reference 中已存在的頁面，都能在 backend reference 找到對應的 authority surface。
    新增 app workflow 時，應先補這個 pairing，再補頁面細節。

---

## Consumer Questions

| 想回答的問題 | 應優先查看 |
|---|---|
| 目前 active dataset 與 workspace scope 從哪裡來？ | [Session & Workspace](session-workspace.md) |
| definition catalog 與 persisted preview 由哪個 surface 提供？ | [Circuit Definitions](circuit-definitions.md) |
| raw trace summary、detail payload 與 dataset profile 誰負責？ | [Datasets & Results](datasets-results.md) |
| task lifecycle、event history 與 result attachment 怎麼定義？ | [Tasks & Execution](tasks-execution.md) |
| Schemdraw live render 的 request / response contract 是什麼？ | [Schemdraw Render](schemdraw-render.md) |
| characterization run history、artifact 與 tagging 誰負責？ | [Characterization Results](characterization-results.md) |

---

## Related

- [Frontend Reference](../../app/frontend/index.md)
- [CLI Options](../../cli/index.md)
- [Architecture Reference](../../architecture/index.md)
