---
aliases:
  - Type Checking
  - Typing Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Type-checking rules for Python and TypeScript.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Type Checking

The purpose of typing rules is not cosmetic zero-warning output. It is to keep data contracts stable across UI, API, CLI, and the scientific core.

## Python

- tool: `basedpyright`
- baseline: `basic`, treated as mandatory
- all functions need typed parameters and return values
- use `list[str]`, `dict[str, float]`, `str | None`
- avoid `Any` unless necessary

### Allowed Exceptions

- if a third-party scientific library is untyped, use the smallest possible `# type: ignore`
- every ignore needs a reason

## TypeScript

- use `strict: true`
- services, schemas, component props, and hook return values must be typed
- never treat unvalidated API payloads as trusted data
- only data parsed by `zod` or an equivalent schema should enter UI business flow

## Fix Policy

- fix the code first when type errors appear
- only accept local suppressions when the problem is truly third-party and not cost-effective to repair

## Agent Rule { #agent-rule }

```markdown
## Type Checking
- **Python**:
    - use BasedPyright
    - treat `basic` mode as mandatory
    - type all function parameters and return values
    - use modern syntax like `list[str]` and `str | None`
    - avoid `Any` unless dealing with untyped third-party code
- **TypeScript**:
    - use strict mode
    - do not trust raw API payloads without schema validation
    - keep service, schema, hook, and component contracts typed
- **Fix policy**:
    - fix the code first
    - use `# type: ignore` only in the smallest justified scope
```
