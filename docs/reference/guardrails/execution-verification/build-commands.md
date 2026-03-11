---
aliases:
  - Build Commands
  - 執行指令
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的 frontend、backend、desktop、CLI、docs 與 repo-root orchestration 常用指令。
version: v2.2.0
last_updated: 2026-03-11
updated_by: codex
---

# Build Commands

本文件列出 rewrite branch 目前可用的 repo-root orchestration 與 workspace 指令。
rewrite foundation 必須使用獨立於 legacy NiceGUI runtime 的 entrypoints。

## Current Baseline

```bash
uv sync
julia --project=. -e 'using Pkg; Pkg.instantiate()'
./scripts/prepare_docs_locales.sh
```

## Rewrite Root Orchestration

```bash
npm run rewrite:install
npm run rewrite:check
npm run rewrite:build
npm run rewrite:dev
npm run rewrite:stop
```

## Rewrite Workspaces

### Frontend

```bash
npm install --prefix frontend
npm run dev --prefix frontend
npm run test --prefix frontend
npm run lint --prefix frontend
npm run typecheck --prefix frontend
npm run build --prefix frontend
```

### Backend

```bash
cd backend && uv sync
cd backend && uv run pytest
cd backend && uv run uvicorn src.app.main:app --reload --port 8000
```

### Desktop

```bash
npm install --prefix desktop
npm run dev --prefix desktop
npm run lint --prefix desktop
npm run build --prefix desktop
```

### CLI

```bash
uv run sc --help
```

## Docs

```bash
uv run python scripts/check_docs_nav_routes.py --check-source
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml
./scripts/build_docs_sites.sh
uv run python scripts/check_docs_nav_routes.py --check-built
```

## Agent Rule { #agent-rule }

```markdown
## Run / Build Commands
- **Rewrite root orchestration**:
    - `npm run rewrite:install`
    - `npm run rewrite:check`
    - `npm run rewrite:build`
    - `npm run rewrite:dev`
    - `npm run rewrite:stop`
- **Python install**: `uv sync`
- **Julia install**: `julia --project=. -e 'using Pkg; Pkg.instantiate()'`
- **Frontend**:
    - `npm install --prefix frontend`
    - `npm run dev --prefix frontend`
    - `npm run test --prefix frontend`
    - `npm run lint --prefix frontend`
    - `npm run typecheck --prefix frontend`
    - `npm run build --prefix frontend`
- **Backend**:
    - `cd backend && uv sync`
    - `cd backend && uv run pytest`
    - `cd backend && uv run uvicorn src.app.main:app --reload --port 8000`
- **Desktop**:
    - `npm install --prefix desktop`
    - `npm run dev --prefix desktop`
    - `npm run lint --prefix desktop`
    - `npm run build --prefix desktop`
- **CLI**: `uv run sc --help`
- **Docs**:
    - `uv run python scripts/check_docs_nav_routes.py --check-source`
    - `./scripts/prepare_docs_locales.sh`
    - `uv run --group dev zensical build -f zensical.toml`
    - `uv run --group dev zensical build -f zensical.en.toml`
    - `./scripts/build_docs_sites.sh`
    - `uv run python scripts/check_docs_nav_routes.py --check-built`
```
