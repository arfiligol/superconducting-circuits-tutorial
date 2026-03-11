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
scope: rewrite branch 的 frontend、backend、desktop、CLI 與 docs 常用指令。
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Build Commands

## Current Baseline

```bash
uv sync
julia --project=. -e 'using Pkg; Pkg.instantiate()'
./scripts/prepare_docs_locales.sh
```

## Rewrite Target Commands

### Frontend

```bash
npm install --prefix frontend
npm run dev --prefix frontend
npm run build --prefix frontend
```

### Desktop

```bash
npm install --prefix desktop
npm run dev --prefix desktop
npm run build --prefix desktop
```

### Backend

```bash
uv sync
uv run uvicorn backend.src.app.main:app --reload --port 8000
```

### CLI

```bash
uv run sc --help
```

### Docs

```bash
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml
./scripts/build_docs_sites.sh
```

## Agent Rule { #agent-rule }

```markdown
## Run / Build Commands
- **Python install**: `uv sync`
- **Julia install**: `julia --project=. -e 'using Pkg; Pkg.instantiate()'`
- **Frontend install**: `npm install --prefix frontend`
- **Frontend dev**: `npm run dev --prefix frontend`
- **Frontend build**: `npm run build --prefix frontend`
- **Desktop install**: `npm install --prefix desktop`
- **Desktop dev**: `npm run dev --prefix desktop`
- **Desktop build**: `npm run build --prefix desktop`
- **Backend dev**: `uv run uvicorn backend.src.app.main:app --reload --port 8000`
- **CLI**: `uv run sc --help`
- **Docs prepare**: `./scripts/prepare_docs_locales.sh`
- **Docs build**:
    - `uv run --group dev zensical build -f zensical.toml`
    - `uv run --group dev zensical build -f zensical.en.toml`
    - `./scripts/build_docs_sites.sh`
```
