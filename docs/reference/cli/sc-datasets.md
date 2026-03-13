---
aliases:
  - "sc datasets 指令參考"
  - "sc datasets CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/dataset
owner: docs-team
audience: user
scope: `sc datasets` dataset catalog 查詢指令。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# sc datasets

查詢 rewrite dataset catalog。

## Usage

```bash
uv run sc datasets list [OPTIONS]
```

## Options

| Option | Description | Default |
|---|---|---|
| `--family TEXT` | 依 dataset family 過濾 | `None` |
| `--status [Ready|Queued|Review]` | 依 dataset status 過濾 | `None` |
| `--sort-by [updated_at|name|samples]` | 排序欄位 | `updated_at` |
| `--sort-order [asc|desc]` | 排序方向 | `desc` |

## Examples

**列出所有 datasets**

```bash
uv run sc datasets list
```

**只看 Fluxonium family**

```bash
uv run sc datasets list --family Fluxonium
```

**依 sample 數量升冪排序**

```bash
uv run sc datasets list --sort-by samples --sort-order asc
```

## CLI Help

```text
Usage: sc datasets [OPTIONS] COMMAND [ARGS]...

 Inspect rewrite dataset state.

Options:
  -h, --help  Show this message and exit.

Commands:
  list  List datasets from the rewrite integration scaffold.
```
