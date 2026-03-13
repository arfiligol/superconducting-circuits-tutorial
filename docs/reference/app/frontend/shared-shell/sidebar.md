---
title: "Sidebar"
aliases:
  - "Frontend Sidebar"
  - "Unified Sidebar"
  - "App Sidebar"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/ui
status: draft
owner: docs-team
audience: team
scope: Frontend shared sidebar 的導航、route grouping 與 responsive shell contract
version: v0.2.0
last_updated: 2026-03-14
updated_by: team
---

# Sidebar

本頁定義 frontend shared sidebar 的正式契約。它是 app shell 的 primary navigation surface。

!!! info "Surface Boundary"
    Sidebar 負責全域導航、route grouping 與 responsive shell entry。
    active dataset、tasks queue 與 user settings 不屬於 Sidebar。

!!! warning "Navigation Is Not Page Logic"
    Sidebar 只決定「如何在 app surfaces 之間移動」。
    它不得承擔 page body 內的 workflow 邏輯，也不得重複 page-local controls。

## Sidebar Composition

| Area | Responsibility |
|---|---|
| Branding | 顯示 app identity，提供回到主要 workspace 的穩定入口 |
| Navigation Groups | 以穩定資訊架構列出 app pages |
| Collapse Control | 在窄螢幕下提供展開 / 收合行為 |

## Navigation Contract

=== "Top-level Groups"

    | Group | Purpose |
    |---|---|
    | `Dashboard` | app 主入口與總覽 |
    | `Pipeline` | dataset-driven workflow：Dashboard、Raw Data、Characterization |
    | `Circuit Simulation` | definition-driven workflow：Schemas、Simulation、Schemdraw |

=== "Required Behaviors"

    | Behavior | Meaning |
    |---|---|
    | Active route highlight | 目前 route 必須在 Sidebar 中有清楚的 active 狀態 |
    | Stable entry points | 主要頁面不得只靠 page-internal links 才能抵達 |
    | Responsive collapse | 窄螢幕可收合，但不可丟失 active route 與導覽分組 |

!!! tip "Sidebar vs Header"
    Sidebar 負責持久導航。
    [Header](header.md) 負責 `Active Dataset`、`Tasks Queue`、worker status 與 user menu。

## Primary Consumers

| Consumer | Why it depends on Sidebar |
|---|---|
| [Dashboard](../workspace/dashboard.md) | 共享 pipeline 導覽入口 |
| [Raw Data Browser](../workspace/raw-data-browser.md) | 共享 design browse 導覽入口 |
| [Schemas](../definition/schemas.md) | 共享 definition workflow entry |
| [Schema Editor](../definition/schema-editor.md) | 共享 catalog-to-editor navigation |
| [Schemdraw](../research-workflow/schemdraw.md) | 共享 research workflow shell |
| [Circuit Simulation](../research-workflow/circuit-simulation.md) | 共享 task-driven workflow shell |
| [Characterization](../research-workflow/characterization.md) | 共享 task-driven workflow shell |

## Related

- [Header](header.md)
- [Frontend Reference](../index.md)
