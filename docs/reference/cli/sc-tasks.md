---
aliases:
  - "sc tasks 指令參考"
  - "sc tasks CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/tasks
status: stable
owner: docs-team
audience: user
scope: "`sc tasks` task list 與 detail 查詢指令。"
version: v0.2.0
last_updated: 2026-03-13
updated_by: team
title: sc tasks
---

# sc tasks

查詢 generic task contract，並對任務做 submit、latest、wait 等操作。

!!! info "Command Role"
    `sc tasks` 是 generic task surface。
    `sc simulation` 與 `sc characterization` 只是 lane-specific wrappers；底層仍依賴同一組 task semantics。

!!! warning "Primary Recovery Key"
    `task_id` 是 attach、inspect、wait 的 primary key。
    `dataset_id` 與 `definition_id` 只能當輔助查詢條件，不可取代 `task_id`。

## Command Map

=== "Browse"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `list` | task list | `--status`, `--lane`, `--scope`, `--dataset-id`, `--limit` |
    | `latest` | 取符合條件的最新 task | `--status`, `--lane`, `--scope`, `--dataset-id` |

=== "Inspect"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `show` | 單筆 task detail | `TASK_ID` |
    | `inspect` | operator-oriented detail，含 event / result summary | `TASK_ID` |

=== "Operate"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `wait` | 輪詢到指定狀態 | `TASK_ID`, `--until-status`, `--interval`, `--timeout` |
    | `submit` | 送出 generic task | `KIND`, `--dataset-id`, `--definition-id`, `--summary` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |

## `list` / `latest` Filters

| Option | Values | Default |
|---|---|---|
| `--status` | `queued`, `running`, `completed`, `failed` | `None` |
| `--lane` | `simulation`, `characterization` | `None` |
| `--scope` | `workspace`, `owned` | `workspace` |
| `--dataset-id` | free text | `None` |
| `--limit` | `1..50` | `20` (`list` only) |

## `submit` Kind

| Value | Meaning |
|---|---|
| `simulation` | definition-driven simulation task |
| `post_processing` | post-processing task |
| `characterization` | dataset-driven characterization task |

!!! example "Common Usage"
    ```bash
    uv run sc tasks list --lane simulation --status running
    uv run sc tasks show 306
    uv run sc tasks inspect 306
    uv run sc tasks submit simulation --definition-id 18 --dataset-id DATASET-001
    uv run sc tasks wait 306 --until-status terminal
    ```

## Authority Pairing

| Concern | Authority |
|---|---|
| task lifecycle、wait semantics、result attachment | [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |
| canonical task semantics | [Architecture / Task Semantics](../architecture/task-semantics.md) |

## Related

- [sc events](sc-events.md)
- [sc results](sc-results.md)
- [sc simulation](sc-simulation.md)
- [sc characterization](sc-characterization.md)
