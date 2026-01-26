---
aliases:
  - "Build Commands"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "Common build and execution commands"
version: v2.0.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Build Commands

List of commonly used build and execution commands.

## Environment Setup

### Python (uv)

```bash
# First install or sync dependencies (creates .venv)
uv sync

# Update dependencies
uv sync --upgrade
```

### Julia

```bash
# Instantiate environment
julia --project=. -e 'using Pkg; Pkg.instantiate()'

# Update dependencies
julia --project=. -e 'using Pkg; Pkg.update()'
```

## CLI Scripts

All scripts are executed via `uv run <script-name>`:

```bash
# Data Preprocessing
uv run sc-preprocess-admittance --input data.csv

# Analysis Fitting
uv run sc-fit-squid

# Plotting
uv run sc-plot-admittance
```

## Documentation

```bash
# Preview (localhost:8000)
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

---

## Agent Rule { #agent-rule }

```markdown
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
```
