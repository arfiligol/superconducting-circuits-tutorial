---
aliases:
  - "sc core 指令參考"
  - "sc core CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/core
owner: docs-team
audience: user
scope: `sc core` 群組目前提供的 shared core proof commands。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# sc core

檢查 `sc_core` 目前公開的最小 shared boundary。

## Usage

```bash
uv run sc core <command>
```

## Commands

| Command | Description |
|---|---|
| `preview-artifacts` | 顯示 `sc_core` 目前公開的 preview artifact 名稱 |

## Examples

**列出 preview artifacts**

```bash
uv run sc core preview-artifacts
```

## CLI Help

```text
Usage: sc core [OPTIONS] COMMAND [ARGS]...

 Inspect the shared core package boundary.

Options:
  -h, --help  Show this message and exit.

Commands:
  preview-artifacts  Show the preview artifacts published by sc_core.
```
