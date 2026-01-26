---
aliases:
  - "Commit Standards"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "Commit timing, granularity, and format standards"
version: v1.0.0
last_updated: 2026-01-27
updated_by: docs-team
---

# Commit Standards

Defines **when** and **how** to commit code.

## When to Commit

1.  **Logical Unit Complete** - A single feature, bugfix, or refactor.
2.  **All Checks Pass** - `uv run pre-commit run --all-files` must pass.
3.  **Independently Revertible** - The commit can be reverted without breaking other functionality.

## When NOT to Commit

1.  **Work in Progress** - Code that doesn't compile, has type errors, or fails tests.
2.  **Mixed Changes** - Combining bug fixes + new features + reformatting.
3.  **Incomplete Work** - Unless explicitly prefixed with `WIP:`.

## Commit Granularity

| Type | Granularity | Example |
| :--- | :--- | :--- |
| `feat:` | A complete feature | `feat: add SQLite persistence layer` |
| `fix:` | A bug fix | `fix: handle empty dataset in fit` |
| `docs:` | Documentation update | `docs: add logging guardrails` |
| `refactor:` | Code restructuring | `refactor: extract repositories` |
| `style:` | Formatting changes | `style: apply ruff formatting` |
| `test:` | Adding/modifying tests | `test: add unit tests for UoW` |
| `chore:` | Maintenance tasks | `chore: update dependencies` |

## Commit Message Format

```
<type>: <short description>

[Optional: detailed description]

[Optional: Closes #issue]
```

**Example:**

```
feat: add colored logging with Rich

- Created core/shared/logging.py setup function
- Updated tech-stack.md with Rich dependency
- Added logging.md guardrails

Closes #42
```

---

## Agent Rule { #agent-rule }

```markdown
## Commit Standards
- **When to Commit**:
    - Single logical unit complete (one feature, one fix, one refactor).
    - All checks pass: `uv run pre-commit run --all-files`.
    - Independently revertable.
- **When NOT to Commit**:
    - Code doesn't compile/type-check.
    - Mixed changes (bug fix + feature + formatting).
    - Incomplete work (unless `WIP:` prefix).
- **Commit Format**: `<type>: <description>`
    - Types: `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`.
- **Before Commit**: ALWAYS run `uv run pre-commit run --all-files`.
```
