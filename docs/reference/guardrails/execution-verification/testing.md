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
scope: rewrite branch 的 backend、frontend、CLI 與 docs 測試規範。
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

文件變更必跑：

```bash
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml
./scripts/build_docs_sites.sh
```

## Policy

- 關鍵 workflow 至少要有一條可重現測試路徑
- backend service 與 CLI workflow 優先寫 pytest
- frontend component 與互動流程分別用 unit / E2E 覆蓋

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
