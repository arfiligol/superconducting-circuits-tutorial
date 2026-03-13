---
aliases:
  - "sc results 指令參考"
  - "sc results CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/results
status: stable
owner: docs-team
audience: user
scope: "`sc results` persisted task result-reference 查詢指令。"
version: v0.1.0
last_updated: 2026-03-13
updated_by: team
title: sc results
---

# sc results

查詢 persisted task result references、trace payload refs 與 result handles。

!!! info "Command Role"
    `sc results` 顯示的是 persisted result surface，而不是 UI in-memory state。
    它適合確認 task 結束後是否真的已綁定 trace payload 或 result handles。

!!! warning "Absent Result State"
    `trace` 與 `handles` 只在對應 payload 已存在時成功。
    若 task 沒有 trace payload 或 result handles，CLI 會直接報錯而不是回傳空展示。

## Command Map

| Subcommand | Focus | Key inputs |
|---|---|---|
| `show` | result-reference summary | `TASK_ID` |
| `trace` | persisted trace payload ref | `TASK_ID` |
| `handles` | persisted result handles | `TASK_ID` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |

!!! example "Common Usage"
    ```bash
    uv run sc results show 306
    uv run sc results trace 306
    uv run sc results handles 306
    ```

## Backend Pair

| Concern | Authority |
|---|---|
| task result attachment | [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |
| trace payload / result handle semantics | [Backend / Datasets & Results](../app/backend/datasets-results.md) |

## Related

- [sc tasks](sc-tasks.md)
- [sc events](sc-events.md)
