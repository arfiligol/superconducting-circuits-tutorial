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
version: v0.8.0
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

## Mutation Surfaces

| Mutation | Responsibility |
|---|---|
| `switch_active_workspace(workspace_id)` | 變更 session active workspace，回傳新 session envelope 與 rebind outcome |
| `activate_dataset(dataset_id | null)` | 設定 active dataset，並驗證該 dataset 對目前 active workspace 可見 |
| `accept_workspace_invitation(invite_token)` | 驗證 invite、建立 membership，並回傳 post-accept context suggestion |
| `leave_workspace(workspace_id)` | 讓目前使用者主動退出 membership，並重新繫結 session context |

## Workspace Switch Response

| Field | Meaning |
|---|---|
| `workspace.id` / `name` / `role` | 新的 active workspace |
| `active_dataset_resolution` | `preserved`, `rebound`, `cleared` |
| `active_dataset` | 重新繫結後的 dataset summary，或 `null` |
| `detached_task_ids[]` | 因 visibility 失效而解除附著的 task ids |
| `capabilities` | 新 workspace 下的 capability summary |
| `memberships[]` | 供 Header 重新渲染 switcher |

## Active Dataset Activation Rules

| Rule | Meaning |
|---|---|
| Must belong to active workspace | dataset 若不屬於或不可見於 active workspace，mutation 必須被拒絕 |
| Explicit clear allowed | 允許把 active dataset 設為 `null`，供空 workspace 或等待手動選取使用 |
| Session-wide propagation | mutation 成功後，所有 page consumers 看到同一 active dataset |
| Rejection must explain why | 至少區分 `not_found`、`not_visible_in_workspace`、`archived` 等原因 |

## Invitation Acceptance Surface

| Field | Meaning |
|---|---|
| `invite.status` | `accepted`, `revoked`, `expired`, `rejected_account_mismatch` |
| `workspace` | 受邀 workspace summary |
| `membership.role` | 新 membership role |
| `switch_available` | 若目前已有其他 active workspace，提示 frontend 顯示切換 CTA |
| `recommended_next_action` | `switch_workspace`, `stay_current`, `reopen_invite` 等 |

## Request / Response Examples

!!! example "Switch active workspace"
    Request:
    ```json
    {
      "workspace_id": "ws_lab_a"
    }
    ```

    Response:
    ```json
    {
      "ok": true,
      "data": {
        "workspace": {
          "id": "ws_lab_a",
          "name": "Lab A",
          "role": "member"
        },
        "active_dataset_resolution": "rebound",
        "active_dataset": {
          "id": "ds_xy_001",
          "name": "FloatingQubitWithXYLine Post 0308_1819"
        },
        "detached_task_ids": ["task_402"],
        "capabilities": {
          "can_switch_workspace": true,
          "can_switch_dataset": true,
          "can_submit_tasks": true
        }
      },
      "meta": {
        "memberships_count": 3
      }
    }
    ```

!!! example "Accept workspace invitation"
    Request:
    ```json
    {
      "invite_token": "inv_4d7c8f"
    }
    ```

    Response:
    ```json
    {
      "ok": true,
      "data": {
        "invite": {
          "status": "accepted"
        },
        "workspace": {
          "id": "ws_lab_b",
          "name": "Lab B"
        },
        "membership": {
          "role": "viewer"
        },
        "switch_available": true,
        "recommended_next_action": "switch_workspace"
      }
    }
    ```

## Error Code Contract

| Code | Category | When it applies |
|---|---|---|
| `auth_required` | `auth_required` | session 無效或未登入 |
| `workspace_membership_required` | `permission_denied` | 目標 workspace 不屬於目前 memberships |
| `dataset_not_visible_in_workspace` | `permission_denied` | activate dataset 指向不可見 dataset |
| `dataset_archived` | `conflict` | active dataset 已 archive，不能作為 current context |
| `workspace_invite_expired` | `conflict` | invite token 已過期 |
| `workspace_invite_revoked` | `conflict` | invite 已撤銷 |
| `workspace_invite_account_mismatch` | `permission_denied` | invite email 與目前帳號不符 |
| `context_rebind_required` | `conflict` | session 切換後需重新選 dataset / task |

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
