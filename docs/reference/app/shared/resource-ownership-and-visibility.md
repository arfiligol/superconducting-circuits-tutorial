---
aliases:
  - Resource Ownership and Visibility
  - Workspace Resource Model
  - 資源歸屬與可見性
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: dataset / schema / task / result / artifact 的 workspace ownership、visibility 與 cross-workspace sharing 規則
version: v0.1.0
last_updated: 2026-03-14
updated_by: team
---

# Resource Ownership & Visibility

本頁定義 multi-user app 中主要資源的歸屬、可見性與跨 workspace 分享規則。

!!! info "App collaboration boundary"
    dataset、schema、task、result、artifact 都必須有一致的 workspace model。

!!! warning "Single Workspace Per Resource"
    每一筆 persisted resource 在任一時刻只能屬於一個 workspace。
    不允許同一筆 mutable resource 同時掛在多個 workspaces。

## Core Rules

| Rule | Meaning |
|---|---|
| Users may join multiple workspaces | 同一 user 可以是多個 workspaces 的成員 |
| One active workspace per session | 一次 session 只在一個 active workspace 中操作 |
| One workspace per resource | 每筆 resource 只有一個 `workspace_id` |
| Visibility is separate from ownership | `visibility_scope` 不等於多 workspace 掛載 |

## Resource Envelope

| Field | Meaning |
|---|---|
| `owner_user_id` | 建立或目前持有該資源的 user |
| `workspace_id` | 該資源所屬的唯一 workspace |
| `visibility_scope` | `private` 或 `workspace` |
| `created_at` / `updated_at` | lifecycle timing |

## Resource Families

| Resource | Ownership rule |
|---|---|
| Dataset | 屬於一個 workspace；可為 `private` 或 `workspace` |
| Circuit Schema | 屬於一個 workspace；預設繼承建立時的 active workspace |
| Task | 預設繼承提交時的 active workspace 與來源資源 scope |
| Result / Artifact | 預設繼承 source task 的 workspace 與 visibility |

## Visibility Model

| Scope | Meaning |
|---|---|
| `private` | 只有 owner、workspace owner、platform admin 可見 |
| `workspace` | 該 workspace 內有權使用者可見 |

## Cross-workspace Sharing

| Sharing mode | Allowed | Meaning |
|---|---|---|
| Export / Import | ✅ | 用於跨 workspace、對外分享、封存 |
| Publish / Copy with lineage | ✅ future | 建立新資源，保留 lineage |
| Multi-workspace mutable object | ❌ | 不允許 |

## Related

* [Identity & Workspace Model](identity-workspace-model.md)
* [Authentication & Authorization](authentication-and-authorization.md)
* [Backend / Session & Workspace](../backend/session-workspace.md)
