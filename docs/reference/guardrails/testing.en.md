---
aliases:
  - "Testing Standards"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "Testing methods and commands"
version: v1.0.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Testing Standards

Automated testing methods and command execution.

## Python Testing

We use **Pytest**.

### Run Tests

```bash
uv run pytest
```

### File Structure

Tests are located in `tests/`, mirroring `src/sc_analysis/`:

```
tests/
├── domain/
│   └── test_xxx.py
├── application/
│   └── test_yyy.py
└── infrastructure/
    └── test_zzz.py
```

### Naming Conventions

- File: `test_<module>.py`
- Function: `test_<function_name>_<scenario>`

## Julia Testing

```bash
julia --project=. -e 'using Pkg; Pkg.test()'
```

---

## Agent Rule { #agent-rule }

```markdown
## Testing Commands
- **Framework**: `pytest`
- **Command**: `uv run pytest` (Runs all tests in `tests/`)
- **Naming**:
    - Files: `test_*.py`
    - Funcs: `test_*()`
- **Structure**: `tests/` mirrors `src/sc_analysis/` structure.
    - e.g. `src/sc_analysis/domain/model.py` -> `tests/domain/test_model.py`.
- **Julia Tests**: `julia --project=. -e 'using Pkg; Pkg.test()'`
```
