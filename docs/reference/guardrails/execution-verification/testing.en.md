---
aliases:
  - Testing
  - Testing Standards
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: Testing rules for backend, frontend, CLI, and docs in the rewrite branch.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Testing

## Backend / Core

```bash
uv run pytest
```

## Frontend

```bash
npm run test --prefix frontend
npm run test:e2e --prefix frontend
```

## Docs

Docs changes must run:

```bash
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml
./scripts/build_docs_sites.sh
```

## Policy

- every critical workflow needs at least one reproducible test path
- backend services and CLI workflows should prefer pytest coverage
- frontend components and interactions should split between unit and E2E coverage

## Agent Rule { #agent-rule }

```markdown
## Testing Commands
- **Backend/core tests**: `uv run pytest`
- **Frontend unit tests**: `npm run test --prefix frontend`
- **Frontend E2E tests**: `npm run test:e2e --prefix frontend`
- **Docs checks**:
    - `./scripts/prepare_docs_locales.sh`
    - `uv run --group dev zensical build -f zensical.toml`
    - `uv run --group dev zensical build -f zensical.en.toml`
    - `./scripts/build_docs_sites.sh`
- Add tests for critical workflows instead of relying on manual verification only.
```
