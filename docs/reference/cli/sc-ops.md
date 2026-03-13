---
aliases:
  - "sc ops 指令參考"
  - "sc ops CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/tasks
status: stable
owner: docs-team
audience: user
scope: "`sc ops` 研究操作 bundle 指令。"
version: v0.1.0
last_updated: 2026-03-13
updated_by: team
title: sc ops
---

# sc ops

以 connected operator bundle 的角度查看與操作 task。

!!! info "Command Role"
    `sc ops` 不代表一套新的 backend workflow。
    它是把 task、recent events、result attachment 收斂成較適合操作人員的 bundle view。

!!! warning "Bundle Boundary"
    `sc ops` 呈現的是既有 persisted task state 的組合視圖。
    若需要單獨查 event history 或 result refs，仍應回到 [sc events](sc-events.md) 與 [sc results](sc-results.md)。

## Command Map

| Subcommand | Focus | Key inputs |
|---|---|---|
| `inspect` | 單筆 task 的 operator bundle | `TASK_ID`, `--recent-events` |
| `latest` | 依條件取最新 task bundle | `--status`, `--lane`, `--scope`, `--dataset-id`, `--recent-events` |
| `wait` | 等待 task 後再輸出 bundle | `TASK_ID`, `--until-status`, `--interval`, `--timeout`, `--recent-events` |
| `submit` | 送出 task 並輸出 bundle | `KIND`, `--dataset-id`, `--definition-id`, `--summary`, `--wait`, `--until-status`, `--interval`, `--timeout`, `--recent-events` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |
| `--recent-events` | `1..10` | bundle 中附帶的 recent event 數量 |

## Submit Kind

| Value | Meaning |
|---|---|
| `simulation` | definition-driven simulation task |
| `post_processing` | post-processing task |
| `characterization` | dataset-driven characterization task |

!!! example "Common Usage"
    ```bash
    uv run sc ops latest --lane simulation --recent-events 5
    uv run sc ops inspect 306
    uv run sc ops wait 306 --until-status terminal
    uv run sc ops submit simulation --definition-id 18 --wait
    ```

## Authority Pairing

| Concern | Authority |
|---|---|
| task / event / result bundle source | [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |
| result attachment semantics | [Backend / Datasets & Results](../app/backend/datasets-results.md) |

## Related

- [sc tasks](sc-tasks.md)
- [sc events](sc-events.md)
- [sc results](sc-results.md)
