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
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build
uv run --group dev zensical build -f zensical.en.toml

# Canonical CI entrypoint (emits `docs/site/`)
./scripts/build_docs_sites.sh
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
    2. **Build**: `./scripts/build_docs_sites.sh` must pass.
    3. **Test**: `pytest` must pass.
- **Tolerance**:
    - `zensical build` during docs preview: allow benign `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
```
