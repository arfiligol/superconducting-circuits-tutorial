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
version: v0.3.0
last_updated: 2026-03-14
updated_by: codex
---

# Resource Ownership & Visibility

本頁定義 multi-user app 中主要資源的歸屬、可見性與跨 workspace 分享規則。

!!! info "App collaboration boundary"
    dataset、schema、task、result、artifact 都必須有一致的 workspace model。

!!! warning "Single Workspace Per Resource"
    每一筆 persisted resource 在任一時刻只能屬於一個 workspace。
    不允許同一筆 mutable resource 同時掛在多個 workspaces。

!!! tip "Safe default"
    V1 的預設應採 `private-first`。
    使用者明確 publish 前，dataset、schema 與其他 mutable research assets 預設不自動共享給整個 workspace。

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
| `lifecycle_state` | `active`、`archived`、`deleted` |
| `created_at` / `updated_at` | lifecycle timing |

## Resource Families

| Resource | Ownership rule |
|---|---|
| Dataset | 屬於一個 workspace；可為 `private` 或 `workspace` |
| Design scope | 屬於單一 dataset；不單獨擁有另一組 workspace visibility |
| Circuit Schema | 屬於一個 workspace；預設繼承建立時的 active workspace |
| Task | 預設繼承提交時的 active workspace 與來源資源 scope |
| Result / Artifact | 預設繼承 source task 的 workspace 與 visibility |

## Creation Defaults

| Resource | Default `workspace_id` | Default `visibility_scope` | Notes |
|---|---|---|---|
| Dataset import | current active workspace | `private` | import 完成後可顯式 publish |
| Circuit Schema | current active workspace | `private` | 適合 draft-first editing |
| Task | current active workspace | most restrictive inherited scope | 若任一來源資源為 `private`，task 也必須是 `private` |
| Result / Artifact | source task workspace | inherit from task | 不可手動放寬 visibility |

## Visibility Inheritance

| Rule | Meaning |
|---|---|
| Private source stays private | dataset / schema 任一來源若是 `private`，衍生 task / result 不能升格成 `workspace` |
| Result follows task | result / artifact 不可比 source task 更公開 |
| Publish is explicit | `private -> workspace` 只能由明確 publish action 觸發 |
| Published resources do not silently revert | 已被 publish 的共享資源不應靜默退回 private |

## Visibility Model

| Scope | Meaning |
|---|---|
| `private` | 只有 owner、workspace owner、platform admin 可見 |
| `workspace` | 該 workspace 內有權使用者可見 |

## Lifecycle States

| State | Meaning |
|---|---|
| `active` | 正常可見、可被工作流引用 |
| `archived` | 預設不出現在主列表，但可 restore |
| `deleted` | 不再可由一般 workflow 使用；只保留 tombstone / audit lineage |

## Lifecycle Operations

| Operation | Rule |
|---|---|
| Create / Import | 建立於 current active workspace，預設 `private` |
| Publish to Workspace | 允許 `private -> workspace`，並要求 audit record |
| Clone / Copy with lineage | 建立一筆新資源，保留 `lineage_parent_id` |
| Archive | 將 `active` 轉成 `archived`；不再作為預設 workflow 輸入 |
| Restore | `archived -> active`，保留原 `workspace_id` 與 lineage |
| Delete | 只能對不再作為 active workflow input 的資源執行；必須留下 tombstone / audit |

!!! warning "Use copy instead of unpublish"
    已共享的 resource 若要回到 private editing，正式作法是建立 private copy。
    不以 `workspace -> private` 直接回退，避免破壞既有 shared task / result lineage。

## Cross-workspace Sharing

| Sharing mode | Allowed | Meaning |
|---|---|---|
| Export / Import | ✅ | 用於跨 workspace、對外分享、封存 |
| Publish / Copy with lineage | ✅ future | 建立新資源，保留 lineage |
| Multi-workspace mutable object | ❌ | 不允許 |

## Required Audit Hooks

| Action | Must be audited |
|---|---|
| import dataset / create schema | ✅ |
| publish to workspace | ✅ |
| archive / restore / delete | ✅ |
| export bundle | ✅ |
| copy with lineage | ✅ |

## Related

* [Identity & Workspace Model](identity-workspace-model.md)
* [Authentication & Authorization](authentication-and-authorization.md)
* [Audit Logging](audit-logging.md)
* [Backend / Session & Workspace](../backend/session-workspace.md)
