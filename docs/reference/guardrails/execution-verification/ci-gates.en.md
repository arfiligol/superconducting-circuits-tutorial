---
aliases:
  - CI Gates
  - Merge Gates
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: Required merge gates for the rewrite branch, including the desktop shell.
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# CI Gates

Every PR must pass the required checks for the areas it touches before merge.

## Mandatory Gates

- Python format / lint / type-check
- backend/core pytest
- frontend lint / typecheck / tests / build once the frontend workspace exists
- desktop lint / build once the desktop workspace exists
- docs build when docs are touched
- at least one reviewer approval

## Branch Policy

- no direct pushes to `main`
- guardrail source changes must keep `.agent/rules` synchronized

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
