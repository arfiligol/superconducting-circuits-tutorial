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
scope: multi-user session、workspace membership、invitation accept flow、active workspace、capability exposure 與 task-management permission contract
version: v0.3.0
last_updated: 2026-03-14
updated_by: team
---

# Authentication & Authorization

本頁定義 multi-user app 的 identity、workspace membership、capabilities 與 task-management permission 契約。

!!! info "App-shared surface"
    Header 的 user menu、active workspace switch、active dataset switch、task queue actions，以及 backend session surface 都依賴本契約。

!!! warning "Shared Task Queue Needs Auth First"
    只要 task queue 是多人共用 surface，就必須先定義 visibility 與 action permission。

!!! tip "Chosen baseline"
    正式 baseline 採 JWT-based auth transport，但 `workspace role`、`capabilities` 與 `active workspace` 不以 JWT 自行宣稱。
    這些欄位仍由 backend session surface 作為 authority。

## Identity Objects

| Object | Required meaning |
|---|---|
| Authenticated Session | 綁定 `user`、`active workspace`、capabilities 與 active dataset 的有效作業階段 |
| Workspace Membership | 使用者在特定 workspace 內的角色與可見性邊界 |
| Active Workspace | 當前 session 正在操作的單一 workspace |
| Capability Flags | page 與 shared app surfaces 可直接消費的 permission summary |

## Auth Transport Baseline

| Item | Rule |
|---|---|
| Access credential | signed JWT |
| Access token lifetime | 15 minutes |
| Refresh credential | rotating refresh token |
| Refresh lifetime | 14 days |
| Browser storage | HttpOnly + Secure cookie |
| Session authority | active workspace、active dataset、capabilities 由 backend session row 擁有 |
| Logout | 撤銷 refresh token family，並使對應 session 失效 |

!!! warning "JWT Is Not Permission Authority"
    JWT 用來證明 `user identity` 與 `session continuity`。
    workspace role、task-management permission 與 capability flags 必須以 backend session lookup 為準，避免 token 內嵌權限過期。

## Capability Families

| Capability family | Representative flags |
|---|---|
| Workspace context | `can_switch_workspace`, `can_switch_dataset` |
| Workspace collaboration | `can_invite_members`, `can_remove_members`, `can_transfer_workspace_owner` |
| Task management | `can_submit_tasks`, `can_cancel_own_tasks`, `can_cancel_workspace_tasks`, `can_terminate_workspace_tasks`, `can_retry_own_tasks`, `can_retry_workspace_tasks` |
| Governance | `can_view_audit_logs`, `can_manage_platform_settings` |

## Role Model

| Role family | Values |
|---|---|
| Platform roles | `admin`, `user` |
| Workspace roles | `owner`, `member`, `viewer` |

## Workspace Invitation Lifecycle

!!! info "Primary invitation mechanism"
    目前正式採 `email invitation`。
    應用內通知可以作為未來補充能力，但不是 V1 join flow 的 primary path。
    `SMTP` 是正式 baseline；若 deployment 尚未配置 mail transport，僅 local / admin 測試可退回 manual invite link。

| Step | Rule |
|---|---|
| Invite creation | `owner` 或 `admin` 指定 `workspace`、`email`、`role` 建立 invite |
| Delivery | 系統寄送含單次使用 invite token 的 email |
| Token lifetime | 7 days |
| Accept flow | 已登入使用者可直接 accept；未登入使用者先完成登入或註冊，再 accept |
| Membership creation | accept 後建立 workspace membership 並記錄 audit event |
| Revoke | invite issuer、workspace owner、platform admin 可在 accept 前 revoke |

## Invitation State Model

| State | Meaning |
|---|---|
| `pending` | invite 已建立，尚未被接受 |
| `delivered` | invite email 已成功送出，或 manual invite link 已生成 |
| `accepted` | invite 已被有效消耗並建立 membership |
| `revoked` | invite 已被發起者、workspace owner 或 admin 作廢 |
| `expired` | invite token 逾期，不可再建立 membership |
| `delivery_failed` | invite 建立成功，但 mail transport 未完成傳遞 |

## Invitation Acceptance Flow

=== "Authenticated User"

    1. 使用者點擊 invitation email 或 invite link。
    2. backend 驗證 token 仍為 `pending` / `delivered` 且未過期。
    3. 若該 email 與目前登入帳號不相符，系統必須要求使用者切換帳號或重新登入。
    4. backend 建立 membership，並將 invite 標成 `accepted`。
    5. backend 回傳更新後的 membership list 與 post-accept context suggestion。

=== "Unauthenticated User"

    1. 使用者打開 invite link。
    2. 系統保存 invite token，先導向 `sign in` 或 `sign up`。
    3. 完成登入後再重新驗證 invite token。
    4. 成功後建立 membership，並寫入 audit log。

=== "Post-accept Context Policy"

    | Situation | Rule |
    |---|---|
    | session 尚無 active workspace | 自動切到受邀 workspace |
    | session 已有 active workspace | 不靜默切換；回傳 `switch_available` 提示，讓 Header 顯式切換 |
    | invite 已過期 / revoked | 不建立 membership，回傳 rejection reason |

!!! tip "Why not auto-switch every time"
    接受 invite 不應在使用者已有 active workspace 與未儲存 page context 時靜默切換。
    正式 baseline 是建立 membership 後，讓 Header 明確提供 `Switch to workspace`。

## Outbound Delivery Baseline

| Concern | Rule |
|---|---|
| Primary transport | SMTP |
| Local fallback | 可生成 manual invite link，但僅限 local / admin-controlled environment |
| Failure handling | `delivery_failed` 不應建立 membership，也不得靜默吞掉錯誤 |
| Audit coverage | invite created / sent / failed / accepted / revoked 都必須 audit |
| Detailed transport contract | 由 [Outbound Email Delivery](outbound-email-delivery.md) 定義 |

## Join / Leave / Removal Rules

| Action | Rule |
|---|---|
| Join workspace | 只能透過有效 invite token 建立 membership |
| Leave workspace | `viewer` / `member` 可自行 leave |
| Owner leave | 只有在 workspace 仍有另一位 `owner` 時才允許；否則必須先 transfer ownership |
| Remove member | `owner` 或 `admin` 可移除其他 membership |
| Active session rebinding | 若使用者被移出目前 active workspace，session 必須立即清除 active workspace、active dataset 與 queue context |

## Workspace Collaboration Permission Matrix

| Action | `viewer` | `member` | `owner` | `admin` |
|---|---|---|---|---|
| Accept valid invite for self | ✅ | ✅ | ✅ | ✅ |
| Leave current workspace | ✅ | ✅ | ✅ with ownership rule | ✅ |
| Invite new member | ❌ | ❌ | ✅ | ✅ |
| Revoke pending invite | ❌ | ❌ | ✅ | ✅ |
| Remove other member | ❌ | ❌ | ✅ | ✅ |
| Transfer workspace ownership | ❌ | ❌ | ✅ | ✅ |

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

## Bootstrap Admin Provisioning

!!! info "Local deployment baseline"
    目前預設 only-on-startup bootstrap admin，適合 local DB 與單機部署起步。
    正式規則是：只有在 system 尚未存在任何 platform admin 時，才允許 bootstrap。

| Environment variable | Meaning |
|---|---|
| `SC_BOOTSTRAP_ADMIN_EMAIL` | 初始 admin email |
| `SC_BOOTSTRAP_ADMIN_PASSWORD` | 初始 admin password |
| `SC_BOOTSTRAP_ADMIN_DISPLAY_NAME` | 初始 admin display name |

| Rule | Meaning |
|---|---|
| One-time bootstrap | 第一個 platform admin 建立後，不再重複 bootstrap |
| Audit required | bootstrap 成功與失敗都應留下 audit record |
| Local-only baseline | 若 deployment 仍是 local DB，這是正式 baseline；更進階 provisioning 可之後擴充 |

## Deferred

??? info "Deferred in current milestone"
    `Account Recovery` 暫不納入目前正式 contract。
    後續若補入 password reset / recovery flow，需同步更新 session surface、audit logging 與 admin policy。

## Related

* [Identity & Workspace Model](identity-workspace-model.md)
* [Resource Ownership & Visibility](resource-ownership-and-visibility.md)
* [Outbound Email Delivery](outbound-email-delivery.md)
* [Backend / Session & Workspace](../backend/session-workspace.md)
* [Frontend / Header](../frontend/shared-shell/header.md)
* [Frontend / Task Management](../frontend/shared-workflow/task-management.md)
