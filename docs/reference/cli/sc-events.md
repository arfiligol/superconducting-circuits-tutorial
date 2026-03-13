---
aliases:
  - "sc events 指令參考"
  - "sc events CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/tasks
status: stable
owner: docs-team
audience: user
scope: "`sc events` persisted task event history 查詢指令。"
version: v0.1.0
last_updated: 2026-03-13
updated_by: team
title: sc events
---

# sc events

查詢 persisted task event history。

!!! info "Command Role"
    `sc events` 只看已持久化的 event rows。
    它不是 live log stream，也不會自行推導不存在於 backend 的執行事件。

## Command Map

| Subcommand | Focus | Key inputs |
|---|---|---|
| `show` | 顯示符合條件的 persisted event history | `TASK_ID`, `--event-type`, `--level`, `--limit` |
| `latest` | 顯示符合條件的最新 persisted event | `TASK_ID`, `--event-type`, `--level` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |

## Filters

| Option | Values | Default |
|---|---|---|
| `--event-type` | `task_submitted`, `task_running`, `task_completed`, `task_failed` | `None` |
| `--level` | `info`, `warning`, `error` | `None` |
| `--limit` | integer >= 1 | `None` (`show` only) |

!!! example "Common Usage"
    ```bash
    uv run sc events show 306
    uv run sc events show 306 --event-type task_running --limit 5
    uv run sc events latest 306 --level error
    ```

## Backend Pair

| Concern | Authority |
|---|---|
| persisted task event history | [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |

## Related

- [sc tasks](sc-tasks.md)
- [sc results](sc-results.md)
