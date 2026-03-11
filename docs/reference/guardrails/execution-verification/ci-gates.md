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
scope: rewrite branch 的 PR 合併品質門檻，含 desktop shell。
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# CI Gates

所有 PR 在 merge 前必須通過與 touched area 對應的必要檢查。

## Mandatory Gates

- Python format / lint / type-check
- backend/core pytest
- frontend lint / typecheck / tests / build（frontend 存在後）
- desktop lint / build（desktop workspace 存在後）
- docs build（若變更 docs）
- 至少一位 reviewer approve

## Branch Policy

- `main` 禁止直接 push
- rewrite branch 的規則變更需同步更新 `.agent/rules`

## Agent Rule { #agent-rule }

```markdown
## CI Gates
- Mandatory checks include:
    - Python format / lint / type-check
    - backend/core pytest
    - frontend lint / typecheck / tests / build when the frontend workspace exists
    - desktop lint / build when the desktop workspace exists
    - docs build when docs are touched
- `main` must not receive direct pushes.
- Guardrail source changes must keep `.agent/rules` in sync.
- Any failing required check blocks merge.
```
