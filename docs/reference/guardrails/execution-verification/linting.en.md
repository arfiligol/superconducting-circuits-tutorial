---
aliases:
  - "Linting & Formatting Guardrails"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Linting & Formatting Guardrails

We use industry-standard tools to enforce code quality and style.

## Toolchain

### 1. Ruff (Linting & Formatting)
[Ruff](https://docs.astral.sh/ruff/) is an extremely fast Python Linter and Formatter written in Rust.
- **Why?**:
    - **Speed**: 10-100x faster than traditional tools (Flake8, Black).
    - **All-in-one**: Replaces Flake8 (lint), Black (format), isort (import sorting), pyupgrade (syntax modernization).
    - **Standard**: Widely adopted by the Python community (Pandas, FastAPI, SciPy).

### 2. Pre-commit (Automation)
[Pre-commit](https://pre-commit.com/) is a framework for managing multi-language pre-commit hooks.
- **Why?**:
    - **Enforcement**: Runs checks automatically at `git commit`, preventing non-compliant code from entering version control.
    - **Consistency**: Ensures all developers use the same version of checks.

### 3. BasedPyright (Type Checking)
[BasedPyright](https://github.com/DetachHead/basedpyright) creates a stationary snapshot of the Microsoft Pyright type checker.
- **Why?**:
    - **Compatibility**: The standard Pyright (and Pylance) often relies on proprietary VS Code extensions. BasedPyright ensures consistent CLI behavior across different IDEs and Agentic environments (like Antigravity).
    - **Strictness**: Provides stricter defaults than standard Pyright.

## Usage

### Setup
After cloning the repository, install the git hooks:
```bash
uv run pre-commit install
```

### Daily Workflow
Checks run automatically on `git commit`. If they fail, the tool may auto-fix issues (like formatting) or report errors.
To run manually:
```bash
# Run all hooks
uv run pre-commit run --all-files

# Run only Ruff
uv run ruff check .
uv run ruff format .
```

## Configuration
See `pyproject.toml` sections `[tool.ruff]` and `[tool.basedpyright]`.

---

## Agent Rule { #agent-rule }

```markdown
## Lint / Format Commands
- **Format (Python)**: `uv run ruff format .` (Run first)
- **Lint (Python)**: `uv run ruff check . --fix` (Run second)
- **Type Check**: `uv run basedpyright`
- **Pre-commit**: `uv run pre-commit run --all-files` (Master check)
- **Config Loc**: `pyproject.toml` (`[tool.ruff]`, `[tool.basedpyright]`).
- **Policy**: No lint errors allowed in `src/`.
```
