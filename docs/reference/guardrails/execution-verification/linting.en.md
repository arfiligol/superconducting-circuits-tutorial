---
aliases:
  - Linting & Formatting
  - Code Checks
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: Python and frontend lint / format / type-check rules for the rewrite branch.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Linting & Formatting

## Tooling

- Python: Ruff + BasedPyright
- Frontend: project-local lint / format / typecheck commands
- Repo gate: pre-commit when hooks are configured

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

- touched files must not introduce new lint errors
- prefer repairing type issues over suppressing them
- if the frontend workspace is not present yet, keep enforcing the Python/docs baseline; once it exists, it joins the standard gate

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
