---
title: "Task Management"
aliases:
  - "Frontend Task Management"
  - "Task Queue"
  - "Task Attachment"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/ui
status: draft
owner: docs-team
audience: team
scope: Frontend shared header task queue、task attachment、worker summary、control actions 與 refresh recovery contract
version: v0.3.0
last_updated: 2026-03-14
updated_by: team
---

# Task Management

本頁定義 frontend shared task management surface：Header `Tasks Queue`、attached task、worker summary、control actions、result handoff 與 refresh recovery。

!!! info "Surface Boundary"
    這裡定義的是 shared task-centric contract，供 `Circuit Simulation` 與 `Characterization` 共用。
    analysis-specific `Run History` 與 artifact-specific result layout 不屬於本頁 owner 範圍。

!!! warning "Persisted Task Authority"
    task queue、attach、refresh recovery 必須以 persisted task state 為準。
    page-local memory 只能做暫時顯示，不可成為 execution authority。

!!! info "Active Workspace Boundary"
    Header queue 只顯示目前 active workspace 中可見的 tasks。
    切換 workspace 後，queue content、allowed actions 與 attached task validity 都必須重新計算。

## Shared Objects

| Object | Responsibility |
|---|---|
| Header Task Trigger | 在所有 app pages 上可直接打開 queue |
| Task Queue Panel | 顯示最近可見的 tasks，支援 filter、attach、cancel、terminate、retry |
| Worker Summary | 顯示每個 lane 的 processor health 與 busy / degraded 狀態 |
| Attached Task | 表示目前 page body 正在關注的單一 persisted task |
| Lifecycle Summary | 顯示 queued / running / completed / failed / cancelled / terminated 與最近 event 概況 |
| Result Handoff | terminal task 完成後，將 page context 切到 persisted result surface |

## Task Queue Panel Contract

| Field / affordance | Required meaning |
|---|---|
| `task_id` | primary recovery / attach key |
| `lane` / `task_kind` | 幫助頁面判定 workflow lane 與 task semantics |
| `status` | lifecycle status summary |
| `summary` | 人類可讀的 task 摘要 |
| `owner_display_name` | 多使用者 queue 中辨識 task owner |
| `visibility_scope` | `workspace` / `owned` 等共享可見性語意 |
| `dataset_id` / `definition_id` / design context | 提供與目前頁面 context 的關聯 |
| `updated_at` | 幫助排序最近活動 |
| `Attach` action | 明確將 page body 切到指定 persisted task |
| `Cancel` / `Terminate` / `Retry` actions | 依 task 狀態與使用者權限顯示 |
| result availability | 表示是否已有 persisted result 可供 handoff |

## Worker Summary Contract

| Field | Required meaning |
|---|---|
| `lane` | 對應 simulation / characterization / processing lane |
| `healthy_processors` | 正常可接任務數量 |
| `busy_processors` | 正在執行任務數量 |
| `degraded_processors` | 狀態異常但仍可見數量 |
| `draining_processors` | 不再接新任務、等待收尾數量 |
| `offline_processors` | 已離線或 heartbeat 超時數量 |

## Management Actions

| Action | Required states | Permission gate | Effect |
|---|---|---|---|
| `Attach` | any visible task | visible to current user | page body 切到指定 task |
| `Cancel` | `queued`, `dispatching`, `running`, `cancellation_requested` | own task or workspace-manage permission | 發出 graceful cancel |
| `Terminate` | `running`, `cancelling`, `termination_requested` | workspace-manage permission | 發出 force terminate |
| `Retry` | `completed`, `failed`, `cancelled`, `terminated` | submit permission + ownership rule | 建立新 task 並保留 lineage |

## Shared States

| State | Meaning |
|---|---|
| `Queue Closed` | Header queue 尚未展開 |
| `Queue Open` | Header queue 已展開並可進行 task management |
| `Loading` | task list / task detail / worker summary 請求中 |
| `Workspace Switching` | shell 正在切換 active workspace，queue 需暫停舊內容 |
| `Attached` | 頁面已附加到一筆 persisted task |
| `Stale` | page body 顯示的是舊結果，等待新 task state 或 render 更新 |
| `Cancellation Requested` | 已發出 graceful stop，等待 runtime 回應 |
| `Termination Requested` | 已發出 force terminate，等待 runtime 回應 |
| `Terminal / No Result` | task 已終止，但沒有可讀取的 result surface |
| `Terminal / Result Ready` | task 已終止，且已可切換到 persisted result surface |

## Interaction Rules

=== "Submit And Attach"

    1. page 提交新 task
    2. 立即取得 persisted `task_id`
    3. Header queue 立即出現該 task
    4. page body 自動附加到該 task
    5. lifecycle summary 與 result area 轉為 task-driven state

=== "Attach Existing"

    1. 從 Header task queue 或 `Attach Latest` 選擇既有 task
    2. page body 切換到該 task
    3. 以 persisted task detail / events / result refs 重建畫面

=== "Cancel / Terminate"

    1. 從 Header queue row 點擊 `Cancel` 或 `Terminate`
    2. backend 立即回寫 control request
    3. 頁面顯示 `Cancellation Requested` 或 `Termination Requested`
    4. terminal status 與 result availability 由 persisted task state 決定

=== "Refresh Recovery"

    1. refresh / reconnect 後，若 URL 或 page state 仍指向既有 `task_id`
    2. frontend 必須能重讀 persisted task state
    3. 不得因刷新而退回尚未附加的初始畫面

=== "Workspace Switch"

    1. Header 切換 active workspace
    2. queue rows 改為新 workspace 中可見的 persisted tasks
    3. 若目前 attached task 不再可見，前端必須解除附著並提示原因
    4. 之後再依新 workspace 重新選擇 dataset / task

## Page Variants

=== "Circuit Simulation"

    | Aspect | Requirement |
    |---|---|
    | Queue entry | queue 由 Header 提供，頁面不重複造一份全域 queue |
    | Result handoff | 任務完成後切到 raw / post-processing result surface |
    | Context binding | task 與 active definition、dataset 必須可同時被看見 |

=== "Characterization"

    | Aspect | Requirement |
    |---|---|
    | Queue entry | 透過 Header queue 觀察 shared task activity 與 worker status |
    | Run history relation | `Run History` 是 analysis artifact surface，不取代 shared task semantics |
    | Result handoff | completed task 之後切到 persisted characterization results |

!!! tip "Run History 不是 Task Queue"
    `Run History` 回答的是「這個 analysis 曾經跑過什麼」；
    `Task Queue` 回答的是「目前有哪些 persisted task 可以 attach、追蹤、取消、終止或恢復」。

## Authority Pair

| Concern | Authority |
|---|---|
| task submission / detail / latest / control actions | [Backend / Tasks & Execution](../../backend/tasks-execution.md) |
| result attachment / persisted result availability | [Backend / Tasks & Execution](../../backend/tasks-execution.md), [Backend / Datasets & Results](../../backend/datasets-results.md) |
| workspace-scoped resource visibility | [App / Shared / Resource Ownership & Visibility](../../shared/resource-ownership-and-visibility.md) |
| control-action permission | [App / Shared / Authentication & Authorization](../../shared/authentication-and-authorization.md) |
| worker summary / terminate semantics | [App / Shared / Task Runtime & Processors](../../shared/task-runtime-and-processors.md) |

## Primary Consumers

| Consumer | Why it depends on Task Management |
|---|---|
| [Circuit Simulation](../research-workflow/circuit-simulation.md) | 需要 task submission、attach、recovery、result handoff |
| [Characterization](../research-workflow/characterization.md) | 需要 live run attach、refresh recovery、result handoff |

## Related

- [Header](../shared-shell/header.md)
- [Sidebar](../shared-shell/sidebar.md)
- [Backend / Tasks & Execution](../../backend/tasks-execution.md)
- [App / Shared / Authentication & Authorization](../../shared/authentication-and-authorization.md)
- [App / Shared / Task Runtime & Processors](../../shared/task-runtime-and-processors.md)
