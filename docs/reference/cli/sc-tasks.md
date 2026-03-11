---
aliases:
  - "sc tasks 指令參考"
  - "sc tasks CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/tasks
owner: docs-team
audience: user
scope: `sc tasks` task list 與 detail 查詢指令。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# sc tasks

查詢 rewrite task queue 的可見任務與單筆 detail。

## Usage

```bash
uv run sc tasks list [OPTIONS]
uv run sc tasks show <TASK_ID>
```

## Commands

### `list`

| Option | Description | Default |
|---|---|---|
| `--status [queued|running|completed|failed]` | 依 task status 過濾 | `None` |
| `--lane [simulation|characterization]` | 依 task lane 過濾 | `None` |
| `--scope [workspace|owned]` | task visibility scope | `workspace` |
| `--dataset-id TEXT` | 依 dataset id 過濾 | `None` |
| `--limit INTEGER` | 顯示筆數上限 | `20` |

### `show`

| Argument | Description |
|---|---|
| `TASK_ID` | 要查詢的 task id |

## Examples

**列出目前可見任務**

```bash
uv run sc tasks list
```

**只看 simulation lane**

```bash
uv run sc tasks list --lane simulation
```

**查看單筆 task detail**

```bash
uv run sc tasks show 301
```

## CLI Help

```text
Usage: sc tasks [OPTIONS] COMMAND [ARGS]...

 Inspect rewrite task state.

Options:
  -h, --help  Show this message and exit.

Commands:
  list  List tasks from the rewrite integration scaffold.
  show  Show one task from the rewrite integration scaffold.
```
