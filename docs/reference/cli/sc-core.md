---
aliases:
  - "sc core 指令參考"
  - "sc core CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/core
status: stable
owner: docs-team
audience: user
scope: "`sc core` 群組目前提供的 shared core proof commands。"
version: v0.2.0
last_updated: 2026-03-13
updated_by: team
title: sc core
---

# sc core

檢查 installable `sc_core` 邊界目前公開的 shared surface。

!!! info "Command Role"
    `sc core` 不是 workflow command group。
    這組命令用來確認 standalone CLI 目前看得到哪些 `sc_core` contract surface，適合做 boundary proof 與 automation smoke check。

!!! warning "Output Contract"
    `sc core preview-artifacts` 目前只提供 text output。
    它不是 generic `--output text|json` contract 的代表頁。

## Published Subcommands

| Subcommand | Focus | Notes |
|---|---|---|
| `preview-artifacts` | 顯示 `sc_core` 目前公開的 preview artifact 名稱 | 對齊 `DEFAULT_PREVIEW_ARTIFACTS` installable surface |

!!! example "Usage"
    ```bash
    uv run sc core preview-artifacts
    ```

## Authority Pairing

| 想確認的事情 | 應查看 |
|---|---|
| `sc_core` 目前有哪些 preview artifact 名稱？ | `sc core preview-artifacts` |
| preview artifact 名稱由誰定義？ | [Core / Python Core](../core/python-core.md) |

## Related

- [CLI Options](index.md)
- [Python Core](../core/python-core.md)
