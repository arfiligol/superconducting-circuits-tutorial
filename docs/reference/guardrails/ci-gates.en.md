---
aliases:
  - "CI Gates"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "Quality gates and CI checks"
version: v1.0.0
last_updated: 2026-01-24
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
uv run mkdocs build
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
    2. **Build**: `mkdocs build` must pass.
    3. **Test**: `pytest` must pass.
- **Tolerance**:
    - `mkdocs build`: Allow `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
```
