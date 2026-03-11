---
aliases:
  - "Error Handling"
  - "錯誤模型"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: team
scope: "定義 API、CLI、worker 與 recovery flow 的統一錯誤分類與處理規範"
version: v1.1.0
last_updated: 2026-03-12
updated_by: codex
---

# Error Handling

本專案的錯誤處理必須可被 frontend、backend、CLI、worker 共用理解，而不是每一層各自發明一套訊息。

## Required Error Categories

- `auth_required`
- `permission_denied`
- `validation_error`
- `not_found`
- `conflict`
- `task_not_ready`
- `task_execution_failed`
- `persistence_error`
- `trace_store_error`
- `internal_error`

## Public Error Envelope

所有 public-facing contract 至少要能映射到這組欄位：

| 欄位 | 說明 |
| --- | --- |
| `error_code` | 穩定 machine-readable code |
| `category` | 高階分類，例如 `validation_error` |
| `message` | user-safe message |
| `retryable` | `true/false` |
| `details` | 可選的 structured detail；不得洩漏 adapter internals |
| `debug_ref` | log correlation id 或 task id；可選 |

## Surface Mapping

- backend API：回傳穩定 HTTP status + error envelope
- CLI：stderr message 應保留 `error_code` 或等價 machine-readable signal
- worker：structured log / result error payload 必須可對應到 public category
- frontend：以 `error_code` 與 `retryable` 驅動 UI，而不是靠 message text

## Retryability Rules

| 類型 | 預設 retryable |
| --- | --- |
| `validation_error` | 否 |
| `auth_required` | 否 |
| `permission_denied` | 否 |
| `not_found` | 否 |
| `conflict` | 視情況；需明確標記 |
| `task_not_ready` | 是 |
| `task_execution_failed` | 視 execution detail；需標記 |
| `persistence_error` | 視 storage 層；需標記 |
| `trace_store_error` | 視 storage 層；需標記 |
| `internal_error` | 否，除非明確標記可重試 |

## Recovery-specific Rules

- task submit 失敗、result attach 失敗、recovery attach 失敗必須有獨立 `error_code`
- 不可把 reconnect / recovery 失敗全部折疊成 generic `internal_error`
- `debug_ref` 優先重用 `task_id`、request id 或 trace/result ref

## Agent Rule { #agent-rule }

```markdown
## Error Handling
- Use stable error categories/codes, not only free-form messages.
- Separate user-safe messages from debug/internal details.
- Mark execution/storage/task errors as retryable or non-retryable.
- Do not leak raw adapter internals (paths, SQL fragments, raw exceptions) into public UI/API/CLI contracts.
- Frontend logic must key off stable error codes, not message text matching.
- Task submission, execution, result attach, and recovery attach failures must have explicit error categories.
```
