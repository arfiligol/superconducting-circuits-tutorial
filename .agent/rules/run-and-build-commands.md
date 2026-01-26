---
trigger: always_on
---

## Run / Build Commands
- **Python Install**: `uv sync` (Creates .venv + dependencies).
- **Julia Install**:
    - `julia --project=. -e 'using Pkg; Pkg.instantiate()'`
    - `julia --project=. -e 'using Pkg; Pkg.update()'`
- **Docs**:
    - Build: `uv run mkdocs build --clean`
    - Serve: `uv run mkdocs serve`
- **Scripts**: `uv run <script_name>` (e.g. `uv run sc-fit-squid`).
- **Clean**: `uv cache clean`
