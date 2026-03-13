---
aliases:
  - "sc simulation 指令參考"
  - "sc simulation CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/simulation
status: stable
owner: docs-team
audience: user
scope: "`sc simulation` simulation-lane task 操作指令。"
version: v0.1.0
last_updated: 2026-03-13
updated_by: team
title: sc simulation
---

# sc simulation

操作 simulation lane 上的 task。

!!! info "Lane Wrapper"
    `sc simulation` 是 generic task contract 的 lane-specific wrapper。
    它保留 `show / inspect / latest / wait` 這些 task behaviors，但會自動限制在 `simulation` lane。

!!! warning "Submit Requirement"
    `submit` 必須提供 `--definition-id`。
    `dataset_id` 可以顯式提供，或回退到目前 session 的 active dataset。

## Command Map

=== "Submit"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `submit` | 送出 simulation-lane task | `--definition-id`, `--dataset-id`, `--summary` |

=== "Inspect"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `show` | 顯示單筆 simulation-lane task detail | `TASK_ID` |
    | `inspect` | 顯示 operator-oriented detail | `TASK_ID` |
    | `latest` | 顯示符合條件的最新 simulation-lane task | `--status`, `--scope`, `--dataset-id` |
    | `wait` | 等待單筆 task 達到目標狀態 | `TASK_ID`, `--until-status`, `--interval`, `--timeout` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |

## Filters

| Option | Values | Default |
|---|---|---|
| `--status` | `queued`, `running`, `completed`, `failed` | `None` (`latest`) |
| `--scope` | `workspace`, `owned` | `workspace` (`latest`) |
| `--dataset-id` | free text | `None` |

!!! example "Common Usage"
    ```bash
    uv run sc simulation submit --definition-id 18 --dataset-id DATASET-001
    uv run sc simulation latest --status running
    uv run sc simulation inspect 306
    uv run sc simulation wait 306 --until-status terminal
    ```

## Authority Pairing

| Concern | Authority |
|---|---|
| simulation-lane task lifecycle | [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |
| definition requirement for submit | [Backend / Circuit Definitions](../app/backend/circuit-definitions.md) |

## Related

- [sc tasks](sc-tasks.md)
- [sc ops](sc-ops.md)
