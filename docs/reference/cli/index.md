---
aliases:
- CLI Reference
- CLI 指令參考
tags:
- audience/team
status: draft
owner: docs-team
audience: team
scope: 目前正式支援的 `sc` 命令列介面，涵蓋 shared core、session、datasets、tasks 與 circuit definition 檢查。
version: v0.2.0
last_updated: 2026-03-12
updated_by: codex
---

# CLI Reference

本區只記錄目前正式支援的 `sc` 命令列介面。

## Command Groups

- [sc core](sc-core.md)
  共享 `sc_core` 邊界的最小 proof command，目前提供 `preview-artifacts`。
- [sc session](sc-session.md)
  顯示目前 rewrite session、identity 與 workspace context。
- [sc datasets](sc-datasets.md)
  查詢 rewrite dataset catalog，支援 family/status/sort 條件。
- [sc tasks](sc-tasks.md)
  查詢 rewrite task list 與單筆 task detail。
- [sc circuit-definition](sc-circuit-definition.md)
  以 `sc_core` 檢查 netlist draft，或讀取已持久化的 circuit definition。

## Root Command

```bash
uv run sc --help
```

目前 root command 會公開以下群組：

- `core`
- `session`
- `datasets`
- `tasks`
- `circuit-definition`

## Notes

!!! note "目前範圍"
    目前 CLI 處於 minimal operational stage，重點是 session、dataset、task 與 circuit definition 的檢查能力。

!!! warning "舊指令已移除"
    本頁不再維護舊的 `sc preprocess`、`sc analysis`、`sc plot`、`sc db`、`sc sim` 指令文件。

## Related

- [How-to Guides](../../how-to/index.md) - 操作指南
