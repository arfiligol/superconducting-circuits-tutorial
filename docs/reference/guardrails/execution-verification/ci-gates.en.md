---
aliases:
  - "CI Gates"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Quality gates and CI checks"
version: v1.1.0
last_updated: 2026-02-27
updated_by: docs-team
---

# CI Gates

Quality checks that must pass before merging code.

## Quality Gates

All Pull Requests must pass the following:

### 1. Pre-commit Hooks

Automatically run on `git commit`:

- **Ruff Check**: Linting
- **Ruff Format**: Formatting
- **BasedPyright**: Type Checking

```bash
# Run manually
uv run pre-commit run --all-files
```

### 2. Documentation Build

```bash
uv run --group dev zensical build
```

!!! note "Allowed Warnings"
    `sitemap.xml 404` warnings in dev server are harmless.

### 3. Tests

```bash
uv run pytest
```

---

## Agent Rule { #agent-rule }

```markdown
## CI Gates
- **Mandatory Checks**:
    1. **Pre-commit**: `ruff format` + `ruff check` + `basedpyright`.
    2. **Build**: `uv run --group dev zensical build` must pass.
    3. **Test**: `pytest` must pass.
- **Tolerance**:
    - `uv run --group dev zensical build`: Allow `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
```
