---
aliases:
- App Reference
- UI Reference
- 介面參考
- Frontend Reference
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Frontend app reference 索引，涵蓋 workspace、definition 與 research workflow surfaces
version: v0.11.0
last_updated: 2026-03-13
updated_by: team
---

# Frontend Reference

本區收錄 frontend app layer 的可查詢規格，涵蓋工作空間、定義與研究流程之介面契約。

!!! info "How To Read Frontend App Docs"
    先讀 `Workspace` 取得 dataset 與 design 上下文，再讀 `Definition` 理解 canonical circuit definition，最後讀 `Research Workflow` 對齊 task-driven workflows。

!!! warning "IA Note"
    `Workspace`、`Definition`、`Research Workflow` 是文件分組，不是獨立頁面。
    本頁只列真正存在的 frontend reference pages。

---

## Page Map

=== "Workspace"

    | 頁面 | 核心聚焦 | Backend Pair |
    |---|---|---|
    | [Dashboard](workspace/dashboard.md) | Active dataset、dataset profile、tagged core metrics summary | [Session & Workspace](../backend/session-workspace.md), [Datasets & Results](../backend/datasets-results.md), [Characterization Results](../backend/characterization-results.md) |
    | [Raw Data Browser](workspace/raw-data-browser.md) | Design list、trace preview、compare readiness、summary-only browse | [Datasets & Results](../backend/datasets-results.md) |

=== "Definition"

    | 頁面 | 核心聚焦 | Backend Pair |
    |---|---|---|
    | [Schemas](definition/schemas.md) | Circuit schema catalog、搜尋 / 排序 / 分頁 | [Circuit Definitions](../backend/circuit-definitions.md) |
    | [Schema Editor](definition/schema-editor.md) | Canonical source 編輯、persisted validation、normalized preview | [Circuit Definitions](../backend/circuit-definitions.md) |

=== "Research Workflow"

    | 頁面 | 核心聚焦 | Backend Pair |
    |---|---|---|
    | [Schemdraw](research-workflow/schemdraw.md) | Linked schema、relation config、live Python editor、SVG preview | [Schemdraw Render](../backend/schemdraw-render.md), [Circuit Definitions](../backend/circuit-definitions.md) |
    | [Circuit Simulation](research-workflow/circuit-simulation.md) | Canonical definition、simulation setup、task queue、result surface、recovery | [Circuit Definitions](../backend/circuit-definitions.md), [Tasks & Execution](../backend/tasks-execution.md), [Datasets & Results](../backend/datasets-results.md) |
    | [Characterization](research-workflow/characterization.md) | Run analysis、trace selection、run history、result view、identify mode | [Datasets & Results](../backend/datasets-results.md), [Tasks & Execution](../backend/tasks-execution.md), [Characterization Results](../backend/characterization-results.md) |

---

## Surface Pairing

| 關心的問題 | Frontend 會去哪裡找 | Backend authority |
|---|---|---|
| Active dataset 與 workspace scope | Workspace pages | [Session & Workspace](../backend/session-workspace.md) |
| Dataset profile、trace summary、preview payload | Dashboard / Raw Data Browser / Characterization | [Datasets & Results](../backend/datasets-results.md) |
| Circuit definition catalog 與 persisted preview | Schemas / Schema Editor / Schemdraw / Circuit Simulation | [Circuit Definitions](../backend/circuit-definitions.md) |
| Task lifecycle、event history、result attachment | Circuit Simulation / Characterization | [Tasks & Execution](../backend/tasks-execution.md) |
| Schemdraw live render | Schemdraw | [Schemdraw Render](../backend/schemdraw-render.md) |
| Analysis artifact 與 tagging | Characterization / Dashboard | [Characterization Results](../backend/characterization-results.md) |

!!! success "Coverage Rule"
    每個 frontend page 都必須能在 backend reference 找到對應 surface。
    若新增 frontend workflow 卻無法在上表找到 backend authority，代表 App docs 尚未完整。

---

## Related

- [Reference](../../index.md)
- [Backend Reference](../backend/index.md)
- [CLI Options](../../cli/index.md)
