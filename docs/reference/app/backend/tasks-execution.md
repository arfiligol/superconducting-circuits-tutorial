---
aliases:
  - Backend Tasks Execution Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Backend task queue read model、control actions、worker summary、event history 與 result attachment surface
version: v0.7.0
last_updated: 2026-03-14
updated_by: team
---

# Tasks & Execution

本頁定義 shared task management、simulation 與 characterization 依賴的 backend task surface。

!!! info "Surface Boundary"
    本頁負責 task submission、queue read model、task detail、control actions、event history、result attachment 與 worker summary pairing。
    analysis-specific artifact layout 不屬於本頁責任。

!!! warning "Queue Is A Backend-owned Read Model"
    Header `Tasks Queue` 不是 frontend 自行組裝的列表。
    queue rows、control-action availability、worker summary 與 persisted lifecycle 都必須由 backend authority 提供。

## Coverage

| Surface | Meaning |
|---|---|
| Task submission | 建立新 persisted task，回傳可 attach 的 `task_id` |
| Queue read model | 供 Header queue 直接消費的 summary rows |
| Task detail | 附加後可供 page body 重建 execution context |
| Control actions | `cancel`, `terminate`, `retry` 等 lifecycle mutations |
| Event history | append-only task events |
| Result attachment | 透過 `result_ref` 連到 persisted result surface |

## Submission Contract

task submit response 至少必須提供：

| Field | Meaning |
|---|---|
| `task_id` | persisted primary key |
| `task_kind` | simulation / characterization / processing 等 |
| `lane` | workflow lane |
| `status` | 初始 lifecycle status |
| `visibility_scope` | `workspace` / `owned` |
| `owner_user_id` | task owner |
| `dataset_id` / `definition_id` / design context | 與 page context 相關的 binding |

## Shared Task Lifecycle

!!! warning "Primary Recovery Key"
    `task_id` 是 attach、inspect、wait、refresh recovery 的 primary key。
    `dataset_id`、`definition_id`、design labels 只能當輔助索引。

```text
queued
-> dispatching
-> running
-> completed | failed

running
-> cancellation_requested
-> cancelling
-> cancelled

running | cancelling
-> termination_requested
-> terminated
```

## Queue Read Model

Header queue rows 至少必須能讀到：

| Field | Meaning |
|---|---|
| `task_id` | attach / inspect / recover key |
| `summary` | 人類可讀的 task label |
| `status` | queue row 狀態 |
| `lane` / `task_kind` | workflow lane summary |
| `owner_display_name` | 多使用者 queue 辨識 |
| `visibility_scope` | queue filter 與共享語意 |
| `updated_at` | 排序與最近活動 |
| `result_availability` | terminal 後是否有 persisted result |
| `allowed_actions` | 當前使用者可見的 row actions |

## Control Actions

| Action | Input | Immediate response rule | Terminal rule |
|---|---|---|---|
| `cancel` | `task_id` | 立即把 task 標成 `cancellation_requested` 或等價 control state | 最終由 runtime 決定 `cancelled` |
| `terminate` | `task_id` | 立即把 task 標成 `termination_requested` | 最終由 runtime 決定 `terminated` |
| `retry` | `task_id` | 建立新 task 並回傳新 `task_id`，保留 lineage | 舊 task 不被覆寫 |

!!! tip "Immediate Control Echo"
    使用者在 Header queue 點擊 `Cancel` 或 `Terminate` 後，backend 必須立即回寫 control-request state。
    UI 不應等待 worker 真正結束後才顯示該動作已被接受。

## Task Detail & Events

| Surface | Required meaning |
|---|---|
| task detail | 附加後重建 page body 所需的完整 persisted state |
| task events | append-only lifecycle and execution events |
| execution metadata | worker / processor / result refs / runtime-safe metadata |
| result attachment | terminal task 如何連到 persisted result |

## Worker Summary Pairing

!!! info "Header Worker Status"
    Header queue trigger 旁的 worker status，不應由本頁單獨硬編。
    但 backend task surface 必須能把 queue 與 [Task Runtime & Processors](../shared/task-runtime-and-processors.md) 的 processor summary 對齊。

| Concern | Rule |
|---|---|
| Queue consistency | active task status 與 worker summary 不得互相矛盾 |
| Lane visibility | queue 至少能辨識 task 所屬 lane |
| Control permissions | `allowed_actions` 必須依 [Authentication & Authorization](../shared/authentication-and-authorization.md) 計算 |

## Delivery Rules

| Rule | Meaning |
|---|---|
| Persisted state wins | refresh / reconnect 後以 persisted task state 重建 |
| Queue is globally consumable | Header 在任何頁都能消費同一份 queue read model |
| Detail is attach-ready | simulation / characterization 必須能以 `task_id` 重新附加 |
| Result handoff is explicit | task terminal 後要能分辨 `result ready` 與 `no result` |
| Control actions are auditable | `cancel` / `terminate` / `retry` 必須可進入 audit trail |

## Related

* [Task Management](../frontend/shared-workflow/task-management.md)
* [Header](../frontend/shared-shell/header.md)
* [Shared / Authentication & Authorization](../shared/authentication-and-authorization.md)
* [Shared / Task Runtime & Processors](../shared/task-runtime-and-processors.md)
* [Shared / Audit Logging](../shared/audit-logging.md)
