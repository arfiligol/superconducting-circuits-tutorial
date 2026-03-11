---
aliases:
  - Testing
  - 測試規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的 backend、frontend、desktop、CLI 與 docs 測試規範。
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

rewrite foundation 目前只要求 deterministic unit tests。
不要用 placeholder E2E 假裝覆蓋尚未遷移的真實 workflow。

## Desktop Foundation

```bash
npm run lint --prefix desktop
npm run build --prefix desktop
```

## Docs

文件變更必跑：

```bash
uv run python scripts/check_docs_nav_routes.py --check-source
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml
./scripts/build_docs_sites.sh
uv run python scripts/check_docs_nav_routes.py --check-built
```

## Policy

- 關鍵 workflow 至少要有一條可重現測試路徑
- backend service 與 CLI workflow 優先寫 pytest
- frontend component 與互動流程分別用 unit / E2E 覆蓋
- docs route 驗證必須用 canonical directory routes，而不是來源 `.md` 路徑

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
