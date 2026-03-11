---
aliases:
  - "sc circuit-definition 指令參考"
  - "sc circuit-definition CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/circuit-definition
owner: docs-team
audience: user
scope: `sc circuit-definition` 檢查本地 netlist draft 與已持久化 definition 的指令。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# sc circuit-definition

用 `sc_core` 檢查本地 circuit definition draft，或讀取 backend 中已持久化的 circuit definition。

## Usage

```bash
uv run sc circuit-definition inspect <SOURCE_FILE>
uv run sc circuit-definition inspect --definition-id <ID>
```

## Arguments

| Argument | Description |
|---|---|
| `SOURCE_FILE` | 要檢查的本地 circuit-definition 檔案 |

## Options

| Option | Description | Default |
|---|---|---|
| `--definition-id INTEGER` | 改為檢查 backend 中已持久化的 definition | `None` |

## Examples

**檢查本地 YAML draft**

```bash
uv run sc circuit-definition inspect ./drafts/demo.yaml
```

**查看 id 18 的 persisted definition**

```bash
uv run sc circuit-definition inspect --definition-id 18
```

## Notes

!!! warning "二選一"
    `SOURCE_FILE` 與 `--definition-id` 必須二選一，不能同時提供，也不能同時省略。

## CLI Help

```text
Usage: sc circuit-definition [OPTIONS] COMMAND [ARGS]...

 Inspect canonical circuit-definition inputs via sc_core.

Options:
  -h, --help  Show this message and exit.

Commands:
  inspect  Inspect a draft file through sc_core or a persisted rewrite definition by id.
```
