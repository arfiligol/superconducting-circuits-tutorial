---
title: "Header"
aliases:
  - "Frontend Header"
  - "Workspace Header"
  - "App Header"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/ui
status: draft
owner: docs-team
audience: team
scope: Frontend shared header 的 page identity、active workspace、global context controls、task queue 與 user menu contract
version: v0.3.0
last_updated: 2026-03-14
updated_by: team
---

# Header

本頁定義 frontend shared header 的正式契約。它是 app shell 的 global context carrier。

!!! info "Surface Boundary"
    Header 負責 page identity、`Active Workspace`、`Active Dataset`、`Tasks Queue`、worker status summary 與 user menu。
    page-local form、table filter、result table 與 editor internals 不屬於 Header。

!!! warning "Global Context Lives In Header"
    `Active Workspace`、`Active Dataset` 與 `Tasks Queue` 是 shared shell 的 global context。
    使用者必須能在 Header 直接點擊、展開與操作它們，而不是各頁各自重造入口。

!!! tip "Read With Task Management"
    Header 負責「從哪裡切換 active workspace、切換 dataset、打開 queue、看 worker 狀態、開啟 user menu」。
    queue row 內 `Attach`、`Cancel`、`Terminate`、`Retry` 的行為語意，則由 [Task Management](../shared-workflow/task-management.md) 定義。

## Slot Map

| Slot | Responsibility |
|---|---|
| Left Cluster | Sidebar toggle、page identity、所在 route family |
| Global Context Cluster | `Active Workspace`、`Active Dataset` 與 `Tasks Queue` triggers |
| Worker Status Summary | 在 queue trigger 旁顯示 processor health 摘要 |
| Right Cluster | page-local context chips 與 user menu trigger |

## Global Context Order

| Order | Control | Why it comes first |
|---|---|---|
| 1 | `Active Workspace` | 決定 dataset list、queue visibility 與 capability context |
| 2 | `Active Dataset` | 決定 workflow pages 的預設 dataset scope |
| 3 | `Tasks Queue` | 顯示目前 workspace 中的 shared task activity |
| 4 | worker status summary | 是 queue 與 runtime 的摘要，不高於 queue 本身 |
| 5 | user menu | identity、settings、appearance 與 sign out |

## Global Controls

=== "Active Workspace Trigger"

    | Element | Required behavior |
    |---|---|
    | workspace chip / button | 直接顯示目前 active workspace 名稱與 role 摘要 |
    | expand behavior | 點擊後展開 workspace switcher，只列出目前 user memberships |
    | propagation | 切換後必須同步更新 active dataset、queue visibility、role / capabilities |
    | unsafe-context handling | 若切換造成 attached task 或 active dataset 不再可見，Header 必須觸發清理或重選流程 |
    | dirty-state handling | 若目前頁存在 dirty draft，Header 先顯示 confirm，再送出 switch mutation |

=== "Active Dataset Trigger"

    | Element | Required behavior |
    |---|---|
    | dataset chip / button | 直接顯示目前 active dataset 名稱與狀態 |
    | expand behavior | 點擊後展開 dataset switcher，僅列出 active workspace 中可見的 datasets，並支援 search 與 select |
    | propagation | 切換後必須同步更新 Dashboard、Raw Data、Simulation、Characterization |
    | no-dataset state | 若目前 workspace 尚無可用 dataset，trigger 必須顯示 clear empty state 與 next step |

=== "Tasks Queue Trigger"

    | Element | Required behavior |
    |---|---|
    | queue button / badge | 顯示目前可見 active tasks 數量 |
    | expanded panel | 展示 queue rows、worker summary、filter (`Workspace` / `Mine`) |
    | worker summary | 展開後必須可看到各 lane 的 `healthy / busy / degraded / draining / offline` 摘要 |
    | row action entry | 每列至少支援 `Attach`，並依權限顯示 `Cancel` / `Terminate` / `Retry` |
    | default ordering | active tasks 優先，之後按 `updated_at desc` 顯示最近 terminal tasks |

=== "User Menu"

    | Element | Required behavior |
    |---|---|
    | user icon trigger | 顯示目前 user identity 或 avatar / initials |
    | menu sections | 至少包含 `Profile Summary`、`Settings`、`Appearance`、`Sign out` |
    | appearance control | `Light / Dark / System` 由 User Menu 擁有，不由 Sidebar 擁有 |

## Page Context Variants

| Page family | Header must surface |
|---|---|
| `Dashboard` | active dataset、dataset profile state |
| `Raw Data Browser` | active dataset、selected design summary |
| `Schemas` | page identity、catalog scope |
| `Schema Editor` | active schema、dirty / persisted state |
| `Schemdraw` | linked schema、render state |
| `Circuit Simulation` | active dataset、active definition、attached task summary |
| `Characterization` | active dataset / design、attached task summary |

## Context Switching Outcomes

| Switch | Header must do |
|---|---|
| workspace changed | 重新繫結 active dataset、刷新 queue、更新 role 與 user menu capabilities |
| dataset changed | 更新 dataset chip，通知 workflow pages 重讀 dataset-bound state |
| workspace caused task detachment | 顯示 detached notice，並將 queue panel 保持可重新 attach |
| invite accepted in another workspace | 顯示 `Switch to workspace` CTA，而非無提示地切換 |

## Delivery Rules

| Rule | Meaning |
|---|---|
| Context follows authority | workspace / dataset 來自 session surface；definition 來自 definition surface；task 來自 persisted task surface |
| Workspace is top-level shell context | `Active Workspace` 優先於 `Active Dataset`，因為 dataset list、queue 與 capabilities 都依賴它 |
| Queue is globally reachable | 不論目前在哪一頁，都能從 Header 打開 `Tasks Queue` |
| Worker summary is runtime-driven | Header 顯示的 worker status 必須來自 runtime summary，不可由 UI 推測 |
| Status is summary-only | Header 可以提示 dirty / attached / stale，但不取代 page body 的完整 workflow surface |
| Responsive collapse | 窄螢幕可縮成 icon + chips，但仍必須保留 dataset、queue 與 user menu trigger |

!!! tip "Header vs Sidebar"
    Header 負責 global context 與 user controls。
    [Sidebar](sidebar.md) 只負責穩定導航，不再承擔 dataset switch 或 appearance toggle。

## App Pair

| Concern | Authority |
|---|---|
| active workspace / dataset / user summary | [Backend / Session & Workspace](../../backend/session-workspace.md) |
| attached task summary / queue rows | [Backend / Tasks & Execution](../../backend/tasks-execution.md) |
| permission & user menu capability | [App / Shared / Authentication & Authorization](../../shared/authentication-and-authorization.md) |
| workspace ownership / visibility | [App / Shared / Resource Ownership & Visibility](../../shared/resource-ownership-and-visibility.md) |
| worker / processor status summary | [App / Shared / Task Runtime & Processors](../../shared/task-runtime-and-processors.md) |

## Related

- [Sidebar](sidebar.md)
- [Task Management](../shared-workflow/task-management.md)
