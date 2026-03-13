---
aliases:
  - Audit Logging
  - Audit Trail
  - 稽核日誌
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: persisted audit trail、separate audit store、query/redaction/retention contract
version: v0.1.0
last_updated: 2026-03-14
updated_by: team
---

# Audit Logging

本頁定義 multi-user app 的 persisted audit logging 契約。

!!! info "App governance surface"
    audit logging 是 App collaboration / governance 的一部分，不是一般 runtime logging 的替代品。

!!! warning "Separate Audit Store"
    audit logs 不得與 app operational database 共用同一個資料庫。

## Required Record Fields

| Field | Meaning |
|---|---|
| `audit_id` | audit row 的唯一識別 |
| `occurred_at` | 事件時間 |
| `actor_user_id` | 執行動作者 |
| `workspace_id` | 對應 workspace |
| `action_kind` | 穩定 machine-readable action |
| `resource_kind` | `task`, `dataset`, `definition`, `user`, `workspace` 等 |
| `resource_id` | 被操作資源識別 |
| `outcome` | `accepted`, `rejected`, `completed`, `failed` |
| `payload` | redaction-safe structured payload |

## Related

* [Authentication & Authorization](authentication-and-authorization.md)
* [Task Runtime & Processors](task-runtime-and-processors.md)
* [Backend / Tasks & Execution](../backend/tasks-execution.md)
