---
aliases:
  - "sc session 指令參考"
  - "sc session CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/session
owner: docs-team
audience: user
scope: `sc session` session 與 workspace context 查詢指令。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# sc session

顯示目前 rewrite session、identity 與 workspace context。

## Usage

```bash
uv run sc session show
```

## Commands

| Command | Description |
|---|---|
| `show` | 顯示 session id、auth mode、workspace 與 active dataset |

## Examples

**查看目前 session**

```bash
uv run sc session show
```

## CLI Help

```text
Usage: sc session [OPTIONS] COMMAND [ARGS]...

 Inspect rewrite session state.

Options:
  -h, --help  Show this message and exit.

Commands:
  show  Show the current rewrite session and workspace context.
```
