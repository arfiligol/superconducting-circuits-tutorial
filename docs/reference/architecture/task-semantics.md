---
aliases:
  - "Task Semantics"
  - "任務語意契約"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
status: draft
owner: docs-team
audience: team
scope: "task lifecycle、result handle、retry/cancel/recovery attach 的最小語意模型"
version: v0.2.0
last_updated: 2026-03-12
updated_by: codex
---

# Task Semantics

本文件定義 migration 期間 task system 的最小語意模型。它是 frontend、backend、CLI、worker 共用的契約基礎。

## Required Fields

- `task_id`
- `task_kind`
- `lane`
- `owner_user_id`
- `workspace_id`
- `dataset_id`（若適用）
- `definition_id`（若適用）
- `status`
- `submitted_at`
- `updated_at`
- `result_ref` 或明確空值

## Lifecycle

```text
queued -> running -> completed | failed | cancelled
```

可選中介狀態：

- `cancelling`
- `retry_requested`
- `waiting_for_result_persistence`

## Immutable vs Mutable Fields

### Immutable After Submit

- `task_id`
- `task_kind`
- `owner_user_id`
- `workspace_id`
- `submitted_at`
- routing-related `lane`

### Mutable During Execution

- `status`
- `updated_at`
- progress summary
- append-only logs
- `result_ref`
- terminal error payload

## Result / Log Rules

- logs 應為 append-oriented stream，不得依賴 UI-only in-memory log state
- `result_ref` 必須指向 persisted result / trace / analysis handle，而不是 inline UI blob
- `result_ref` 為空值時，必須能區分是「尚未完成」還是「失敗且無結果」

## Retry / Cancel / Attach

- retry 預設建立新 `task_id`，並保留 `retries_from_task_id` 或等價 lineage
- cancel 至少區分：
  - cancel requested
  - cancel acknowledged
  - terminal cancelled
- attach / recovery 主要依賴 `task_id`
- 若 UI / CLI 需要透過 `dataset_id`、`definition_id` 找回 task，也只能作輔助查詢，不能取代 `task_id`

## Recovery Guarantees

要宣稱 workflow parity 達成，至少要保證：

- task 執行中 refresh 後仍能重新 attach
- task 結束後 result view 可由 `task_id -> result_ref` 重建
- worker / backend / frontend / CLI 對 terminal status 語意一致

## Agent Rule { #agent-rule }

```markdown
## Task Semantics
- `task_id` is the primary recovery/attach key and must not be reused.
- `task_kind`, `owner_user_id`, `workspace_id`, `lane`, and `submitted_at` are immutable after submit.
- Logs are append-oriented; `result_ref` points to persisted results, not UI memory state.
- Retry creates a new task by default and must preserve lineage.
- Cancel semantics must distinguish request vs acknowledgement vs terminal cancelled state.
- Recovery parity requires that task status and result views can be rebuilt from persisted contracts after refresh/reconnect.
```
