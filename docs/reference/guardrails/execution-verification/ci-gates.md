---
aliases:
  - CI Gates
  - CI 品質關卡
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的 PR 合併品質門檻，含 desktop shell 與 docs route validation。
version: v2.2.0
last_updated: 2026-03-11
updated_by: codex
---

# CI Gates

所有 PR 在 merge 前必須通過與 touched area 對應的必要檢查。

## Mandatory Gates

- rewrite root orchestration：`npm run rewrite:install`、`npm run rewrite:check`、`npm run rewrite:build`
- backend foundation：startup smoke 與 `cd backend && uv run pytest`
- frontend：`npm run lint --prefix frontend`、`npm run typecheck --prefix frontend`、`npm run test --prefix frontend`、`npm run build --prefix frontend`
- desktop：`npm run lint --prefix desktop`、`npm run build --prefix desktop`
- docs：`uv run python scripts/check_docs_nav_routes.py --check-source`、`./scripts/build_docs_sites.sh`、`uv run python scripts/check_docs_nav_routes.py --check-built`（docs touched 時）
- 至少一位 reviewer approve

## Notes

- `zensical build` 預覽流程中的良性 `404` 警告不視為 CI 失敗
- backend 專用 lint / type-check gate 之後可再提升；目前 foundation gate 先以 startup smoke + pytest 為主

## Branch Policy

- `main` 禁止直接 push
- rewrite branch 的規則變更需同步更新 `.agent/rules`

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
