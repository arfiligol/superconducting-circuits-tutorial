---
trigger: always_on
---

## Lint / Format Commands
- **Format (Python)**: `uv run ruff format .` (Run first)
- **Lint (Python)**: `uv run ruff check . --fix` (Run second)
- **Type Check**: `uv run basedpyright`
- **Pre-commit**: `uv run pre-commit run --all-files` (Master check)
- **Config Loc**: `pyproject.toml` (`[tool.ruff]`, `[tool.basedpyright]`).
- **Policy**: No lint errors allowed in `src/`.