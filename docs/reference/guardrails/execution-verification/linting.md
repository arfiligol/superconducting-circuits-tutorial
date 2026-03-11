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
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Linting & Formatting

## Tooling

- Python: Ruff + BasedPyright
- Frontend: project-local lint / format / typecheck commands
- Repo gate: pre-commit（若 hook 已設置）

## Commands

```bash
uv run ruff format .
uv run ruff check .
uv run basedpyright src
uv run pre-commit run --all-files
npm run lint --prefix frontend
npm run format --prefix frontend
npm run typecheck --prefix frontend
```

## Policy

- touched files 不接受新增 lint error
- 型別錯誤優先修正，不以忽略規則掩蓋
- frontend 若尚未建立，先維持 Python/docs baseline；建立後即納入常規 gate

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
