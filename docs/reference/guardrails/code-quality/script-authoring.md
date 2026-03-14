---
aliases:
  - Script Authoring
  - CLI 規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: CLI 指令的放置位置、責任邊界與文件規範。
version: v1.1.0
last_updated: 2026-03-14
updated_by: docs-team
---

# Script Authoring

CLI 在本專案中不是附屬工具，而是正式產品介面之一。

!!! info "Use this page for CLI boundary decisions"
    這頁回答新 command 應放哪裡、command 本身該負責什麼，以及 legacy script 只應保留到什麼程度。

## Placement Map

| 如果要做 | 應放位置 |
| --- | --- |
| 新的正式 CLI workflow | `cli/` |
| migration bridge 或舊入口維護 | legacy `src/scripts/`，且不得繼續長新 workflow |
| 真正業務邏輯 | shared service 或 `src/core/` |

## Placement

- 新的 CLI 指令應優先落在 `cli/`
- migration 期間若仍需接舊入口，可保留 bridge，但不要把新 workflow 持續寫進 legacy `src/scripts/`

## Structure

- 使用 `typer`
- 每個 command 只處理參數、輸入/輸出、錯誤顯示
- 真正的 workflow 呼叫共享 service 或 `src/core/`
- command 名稱使用 `kebab-case`

!!! warning "Do not duplicate workflow logic"
    CLI command 可以組裝輸入與輸出，但不能把 API handler 或 service 內部的業務流程整段複製過來。

## Rules

- 必須提供 `--help`
- 必須有明確的 exit behavior
- 不可把 API handler 的內部邏輯整段複製到 CLI
- 若某功能只在 UI 可用、CLI 無法觸發，視為功能缺口

## Agent Rule { #agent-rule }

```markdown
## Script Authoring
- CLI is a first-class interface, not a leftover utility layer.
- New CLI work should go to `cli/`; avoid growing new workflows inside legacy `src/scripts/`.
- Use Typer for commands.
- Commands handle argument parsing, user I/O, and error presentation only.
- Real workflow logic must live in shared services or `src/core/`.
- Command names use `kebab-case`, and every command must have usable `--help`.
```
