---
aliases:
  - Backend Session Workspace Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Backend session、workspace membership、active workspace、user summary、capability exposure 與 active dataset authority surface
version: v0.7.0
last_updated: 2026-03-14
updated_by: team
---

# Session & Workspace

本頁定義 frontend shell、workspace pages 與 shared app model 共用的 session / workspace authority surface。

!!! info "Surface Boundary"
    本頁負責 authenticated session、workspace membership、active workspace、user summary、active dataset、workspace role 與 capability exposure。
    task lifecycle、definition preview、result artifact 與 audit query 不屬於本頁責任。

!!! warning "Single Context Authority"
    app shell 顯示的 `Active Dataset`、`Workspace Role`、`User Menu Summary` 必須來自同一份 backend session authority。
    frontend 不得自行拼裝身份與權限。

## Coverage

| Surface | Meaning |
|---|---|
| Auth state | 使用者目前是 authenticated、anonymous 還是 degraded session |
| User summary | Header user icon / menu 所需的 display data |
| Workspace identity | active workspace、membership role、default queue scope |
| Workspace membership list | user 可切換的 workspaces 與 roles |
| Active dataset | shell-level global dataset context |
| Capability flags | frontend 與 shared task-management surface 可直接使用的 permission summary |

## Session Envelope

backend session surface 至少必須提供：

| Field | Meaning |
|---|---|
| `auth.state` | `authenticated`, `anonymous`, `degraded` 等 session state |
| `auth.mode` | auth transport or mode summary |
| `user.id` | 目前使用者 identity |
| `user.display_name` | Header user icon / menu 顯示名稱 |
| `user.platform_role` | `admin` / `user` |
| `workspace.memberships[]` | 使用者可進入的 workspace 列表與 role 摘要 |
| `workspace.id` | active workspace identity |
| `workspace.name` | workspace display name |
| `workspace.role` | `owner` / `member` / `viewer` |
| `workspace.default_task_scope` | queue default visibility scope |
| `active_dataset.id` / `name` | global dataset context |
| `capabilities` | capability flags summary |

## Active Workspace Switching

| Rule | Meaning |
|---|---|
| Session exposes memberships | Header 要能列出使用者可切換的 workspaces |
| Switch mutates session | active workspace switch 是 session mutation，不是純 frontend state |
| Dataset rebinding is required | workspace 切換後，active dataset 必須重新驗證或重選 |
| Queue rebinding is required | workspace 切換後，queue visibility 與 allowed actions 必須同步更新 |

## Capability Flags

| Capability | Why frontend needs it |
|---|---|
| `can_submit_tasks` | 決定 Simulation / Characterization 是否可送出 task |
| `can_manage_workspace_tasks` | 決定 Header queue 是否顯示 `Cancel` / `Terminate` / `Retry` |
| `can_manage_definitions` | 決定 `Schemas` / `Schema Editor` 是否可建立、儲存、刪除 |
| `can_manage_datasets` | 決定 `Dashboard` metadata editing 是否可寫入 |
| `can_view_audit_logs` | 決定 admin / governance surfaces 是否可顯示 audit entry points |

!!! tip "User Menu Pairing"
    Header user menu 顯示 `Profile Summary`、`Settings`、`Appearance`、`Sign out` 時，
    其中 `Profile Summary`、role label 與 capability-driven menu visibility 都依賴本頁定義的 session envelope。

## Delivery Rules

| Rule | Meaning |
|---|---|
| Dataset switch is global | active dataset 一旦切換，所有 page consumers 應看到同一版本 |
| Role is workspace-scoped | shell 與 pages 看到的 action availability 必須依 workspace role 決定 |
| Capability beats guessing | frontend page 不得自己推斷是否可 submit / manage / delete |
| Session survives refresh | refresh 後必須能重建 user summary、workspace role 與 active dataset |

## Pairing

| Consumer | Why it depends on this surface |
|---|---|
| [Header](../frontend/shared-shell/header.md) | 顯示 active workspace、active dataset 與 user menu |
| [Sidebar](../frontend/shared-shell/sidebar.md) | 需要知道 route family 與 shell-level context propagation |
| [Dashboard](../frontend/workspace/dashboard.md) | dataset metadata editing 依賴 capability flags |
| [Task Management](../frontend/shared-workflow/task-management.md) | queue visibility 與 queue filter 依賴 workspace role / default scope |

## Related

* [Shared / Resource Ownership & Visibility](../shared/resource-ownership-and-visibility.md)
* [Shared / Authentication & Authorization](../shared/authentication-and-authorization.md)
* [Header](../frontend/shared-shell/header.md)
* [Sidebar](../frontend/shared-shell/sidebar.md)
* [Tasks & Execution](tasks-execution.md)
