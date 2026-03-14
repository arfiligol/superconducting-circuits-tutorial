---
aliases:
  - Linting & Formatting
  - Lint 與格式化
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的 Python 與 frontend lint / format / type-check 規範。
version: v2.1.0
last_updated: 2026-03-14
updated_by: docs-team
---

# Linting & Formatting

!!! info "How to use this page"
    這頁只回答格式化、lint、type-check 的日常執行方式。需要測試層級或 merge gate 時，分別看 `Testing` 與 `CI Gates`。

## Tooling

- Python: Ruff + BasedPyright
- Frontend: project-local lint / format / typecheck commands
- Repo gate: pre-commit（若 hook 已設置）

## Command Map

=== "Python / Repo"

    ```bash
    uv run ruff format .
    uv run ruff check .
    uv run basedpyright src
    uv run pre-commit run --all-files
    ```

=== "Frontend"

    ```bash
    npm run lint --prefix frontend
    npm run format --prefix frontend
    npm run typecheck --prefix frontend
    ```

## Policy

| 規則 | 說明 |
| --- | --- |
| touched files 不接受新增 lint error | 不可把既有噪音當成新增問題的遮羞布 |
| 型別錯誤優先修正 | 不以忽略規則掩蓋結構問題 |
| frontend 未建立前維持 Python/docs baseline | 建立後即納入常規 gate |

!!! tip "Good default"
    小範圍改動至少應先跑 touched area 對應的 format、lint 與 type-check；不要把整個 repo gate 留到 commit 前才第一次發現問題。

## Agent Rule { #agent-rule }

```markdown
## Lint / Format Commands
- **Python format**: `uv run ruff format .`
- **Python lint**: `uv run ruff check .`
- **Python type check**: `uv run basedpyright src`
- **Pre-commit**: `uv run pre-commit run --all-files`
- **Frontend lint**: `npm run lint --prefix frontend`
- **Frontend format**: `npm run format --prefix frontend`
- **Frontend typecheck**: `npm run typecheck --prefix frontend`
- **Policy**: no new lint or type errors in touched areas.
```
