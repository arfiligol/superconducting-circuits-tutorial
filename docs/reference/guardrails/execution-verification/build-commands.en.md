---
aliases:
  - Build Commands
  - Run Commands
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: Common repo-root and workspace commands for the rewrite branch frontend, backend, desktop, CLI, and docs.
version: v2.2.0
last_updated: 2026-03-11
updated_by: codex
---

# Build Commands

This page lists the current repo-root orchestration and workspace commands for the rewrite branch.
The rewrite foundation must use entrypoints that are separate from the legacy NiceGUI runtime.

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
