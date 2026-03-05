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
version: v1.2.0
last_updated: 2026-03-05
updated_by: codex
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

### 2. Documentation Build and Route Checks

```bash
uv run python scripts/check_docs_nav_routes.py --check-source
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build
uv run --group dev zensical build -f zensical.en.toml

# Canonical CI entrypoint (emits `docs/site/`)
./scripts/build_docs_sites.sh
uv run python scripts/check_docs_nav_routes.py --check-built
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
    2. **Docs Route Source Check**: `uv run python scripts/check_docs_nav_routes.py --check-source` must pass.
    3. **Build**: `./scripts/build_docs_sites.sh` must pass.
    4. **Docs Route Built Check**: `uv run python scripts/check_docs_nav_routes.py --check-built` must pass.
    5. **Test**: `pytest` must pass.
- **Tolerance**:
    - `zensical build` during docs preview: allow benign `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
```
