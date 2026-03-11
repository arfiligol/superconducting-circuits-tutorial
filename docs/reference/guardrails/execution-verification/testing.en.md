---
aliases:
  - Testing
  - Test Policy
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: Testing rules for the rewrite branch backend, frontend, desktop, CLI, and docs.
version: v2.1.0
last_updated: 2026-03-11
updated_by: codex
---

# Testing

## Rewrite Root Check

```bash
npm run rewrite:check
```

## Backend / Core

```bash
cd backend && uv run pytest
uv run pytest
```

## Frontend

```bash
npm run test --prefix frontend
npm run test:e2e --prefix frontend
```

The current rewrite foundation requires deterministic unit tests first.
Do not fake meaningful E2E coverage with placeholder pages.

## Desktop Foundation

```bash
npm run lint --prefix desktop
npm run build --prefix desktop
```

## Docs

When docs change, run:

```bash
uv run python scripts/check_docs_nav_routes.py --check-source
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml
./scripts/build_docs_sites.sh
uv run python scripts/check_docs_nav_routes.py --check-built
```

## Policy

- Critical workflows need at least one reproducible automated path.
- Prefer pytest first for backend services and CLI workflows.
- Cover frontend components and interactions with unit / E2E tests as the real workflows arrive.
- Docs route validation must use canonical directory routes rather than source `.md` paths.

## Agent Rule { #agent-rule }

```markdown
## Testing Commands
- **Root rewrite check**: `npm run rewrite:check`
- **Backend/core tests**:
    - `cd backend && uv run pytest`
    - `uv run pytest`
- **Frontend unit tests**: `npm run test --prefix frontend`
- **Frontend E2E tests**: `npm run test:e2e --prefix frontend`
- **Desktop foundation checks**:
    - `npm run lint --prefix desktop`
    - `npm run build --prefix desktop`
- **Docs checks**:
    - `uv run python scripts/check_docs_nav_routes.py --check-source`
    - `./scripts/prepare_docs_locales.sh`
    - `uv run --group dev zensical build -f zensical.toml`
    - `uv run --group dev zensical build -f zensical.en.toml`
    - `./scripts/build_docs_sites.sh`
    - `uv run python scripts/check_docs_nav_routes.py --check-built`
- Add tests for critical workflows instead of relying on manual verification only.
- Use canonical directory routes for docs route checks instead of source `.md` paths.
```
