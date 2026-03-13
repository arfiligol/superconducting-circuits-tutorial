---
aliases:
  - "sc session 指令參考"
  - "sc session CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/session
status: stable
owner: docs-team
audience: user
scope: "`sc session` session 與 workspace context 查詢指令。"
version: v0.2.0
last_updated: 2026-03-13
updated_by: team
title: sc session
---

# sc session

顯示或更新目前 rewrite session、workspace 與 active dataset context。

!!! info "Command Role"
    `sc session` 是 CLI 取得 session scope 的正式入口。
    其他接受 `--dataset-id` 的命令若省略該參數，通常會回退到這裡定義的 active dataset。

!!! warning "Mutation Rule"
    `set-active-dataset` 必須二選一：
    提供 `DATASET_ID`，或使用 `--clear` 清除 active dataset。

## Command Map

=== "Read"

    | Subcommand | Focus |
    |---|---|
    | `show` | session、workspace、active dataset 的完整 snapshot |
    | `whoami` | 目前 session identity 與 auth context |
    | `workspace` | workspace scope 與可見性上下文 |
    | `active-dataset` | 目前 active dataset context |

=== "Mutate"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `set-active-dataset` | 更新目前 session 的 active dataset | `DATASET_ID` 或 `--clear` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |

!!! example "Common Usage"
    ```bash
    uv run sc session show
    uv run sc session active-dataset
    uv run sc session set-active-dataset DATASET-001
    uv run sc session set-active-dataset --clear
    ```

## Backend Pair

| Concern | Authority |
|---|---|
| session identity / workspace scope | [Backend / Session & Workspace](../app/backend/session-workspace.md) |
| active dataset fallback | [Backend / Session & Workspace](../app/backend/session-workspace.md) |

## Related

- [CLI Options](index.md)
- [Backend / Session & Workspace](../app/backend/session-workspace.md)
