---
aliases:
  - Authentication and Authorization
  - Auth and Access Control
  - 身分驗證與授權
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: multi-user session、workspace membership、active workspace、capability exposure 與 task-management permission contract
version: v0.1.0
last_updated: 2026-03-14
updated_by: team
---

# Authentication & Authorization

本頁定義 multi-user app 的 identity、workspace membership、capabilities 與 task-management permission 契約。

!!! info "App-shared surface"
    Header 的 user menu、active workspace switch、active dataset switch、task queue actions，以及 backend session surface 都依賴本契約。

!!! warning "Shared Task Queue Needs Auth First"
    只要 task queue 是多人共用 surface，就必須先定義 visibility 與 action permission。

## Identity Objects

| Object | Required meaning |
|---|---|
| Authenticated Session | 綁定 `user`、`active workspace`、capabilities 與 active dataset 的有效作業階段 |
| Workspace Membership | 使用者在特定 workspace 內的角色與可見性邊界 |
| Active Workspace | 當前 session 正在操作的單一 workspace |
| Capability Flags | page 與 shared app surfaces 可直接消費的 permission summary |

## Role Model

| Role family | Values |
|---|---|
| Platform roles | `admin`, `user` |
| Workspace roles | `owner`, `member`, `viewer` |

## Task Queue Permission Matrix

| Action | `viewer` | `member` | `owner` | `admin` |
|---|---|---|---|---|
| Switch active workspace (within membership) | ✅ | ✅ | ✅ | ✅ |
| View workspace-visible tasks | ✅ | ✅ | ✅ | ✅ |
| Switch active dataset | ✅ | ✅ | ✅ | ✅ |
| Attach visible task | ✅ | ✅ | ✅ | ✅ |
| Submit new task | ❌ | ✅ | ✅ | ✅ |
| Cancel own task | ❌ | ✅ | ✅ | ✅ |
| Cancel any workspace task | ❌ | ❌ | ✅ | ✅ |
| Force terminate stuck task | ❌ | ❌ | ✅ | ✅ |
| Retry own terminal task | ❌ | ✅ | ✅ | ✅ |
| Retry any workspace-visible terminal task | ❌ | ❌ | ✅ | ✅ |

## Related

* [Identity & Workspace Model](identity-workspace-model.md)
* [Resource Ownership & Visibility](resource-ownership-and-visibility.md)
* [Frontend / Header](../frontend/shared-shell/header.md)
* [Frontend / Task Management](../frontend/shared-workflow/task-management.md)
