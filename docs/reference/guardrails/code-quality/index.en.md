---
aliases:
  - Code Quality
  - Engineering Quality
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Index for code quality, typing, architecture boundaries, and CLI rules.
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Code Quality

This section defines the code-quality rules for the rewrite branch.
The goal is not framework cleverness; it is stable co-evolution across UI, API, CLI, and the scientific core.

- [Code Style](./code-style.en.md)
- [Type Checking](./type-checking.en.md)
- [Design Patterns](./design-patterns.en.md)
- [Script Authoring](./script-authoring.en.md)
- [Data Handling](./data-handling.en.md)
- [Logging](./logging.en.md)

## Agent Rule { #agent-rule }

```markdown
## Code Quality
- Follow Clean Code: clear naming, small functions, single responsibility.
- UI, API, and CLI must not each duplicate business workflows; shared rules belong in backend services or `src/core/`.
- Prefer fixing the code over adding exceptions or suppressions.
- Load sub-rules as needed: Code Style / Type Checking / Design Patterns / Script Authoring / Data Handling / Logging.
```
