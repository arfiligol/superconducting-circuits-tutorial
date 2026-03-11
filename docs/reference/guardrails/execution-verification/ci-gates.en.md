---
aliases:
  - CI Gates
  - CI Quality Gates
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: PR quality gates for the rewrite branch, including desktop shell and docs route validation.
version: v2.2.0
last_updated: 2026-03-11
updated_by: codex
---

# CI Gates

Every PR must pass the required checks for the touched areas before merge.

## Mandatory Gates

- rewrite root orchestration: `npm run rewrite:install`, `npm run rewrite:check`, `npm run rewrite:build`
- backend foundation: startup smoke plus `cd backend && uv run pytest`
- frontend: `npm run lint --prefix frontend`, `npm run typecheck --prefix frontend`, `npm run test --prefix frontend`, `npm run build --prefix frontend`
- desktop: `npm run lint --prefix desktop`, `npm run build --prefix desktop`
- docs: `uv run python scripts/check_docs_nav_routes.py --check-source`, `./scripts/build_docs_sites.sh`, and `uv run python scripts/check_docs_nav_routes.py --check-built` when docs are touched
- at least one reviewer approval

## Notes

- benign `404` warnings during docs preview builds do not fail CI on their own
- a dedicated backend lint / type-check gate can be added later; the current foundation gate is startup smoke plus pytest

## Branch Policy

- `main` must not receive direct pushes
- rewrite-branch rule changes must keep `.agent/rules` in sync

## Agent Rule { #agent-rule }

```markdown
## CI Gates
- Mandatory checks include:
    - `npm run rewrite:install`
    - `npm run rewrite:check`
    - `npm run rewrite:build`
    - backend startup smoke and `cd backend && uv run pytest`
    - `npm run lint --prefix frontend`
    - `npm run typecheck --prefix frontend`
    - `npm run test --prefix frontend`
    - `npm run build --prefix frontend`
    - `npm run lint --prefix desktop`
    - `npm run build --prefix desktop`
    - `uv run python scripts/check_docs_nav_routes.py --check-source` when docs are touched
    - `./scripts/build_docs_sites.sh` when docs are touched
    - `uv run python scripts/check_docs_nav_routes.py --check-built` when docs are touched
- `main` must not receive direct pushes.
- Guardrail source changes must keep `.agent/rules` in sync.
- Benign `404` warnings from docs preview builds do not fail CI by themselves.
- Any failing required check blocks merge.
```
