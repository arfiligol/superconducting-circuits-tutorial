---
aliases:
  - "Build Commands"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Common build and execution commands"
version: v2.1.0
last_updated: 2026-02-27
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

Use the unified `sc` entrypoint for CLI commands:

```bash
# Data Preprocessing
uv run sc preprocess admittance data/raw/layout_simulation/admittance/example.csv

# Analysis Fitting
uv run sc analysis fit lc-squid DatasetName

# Plotting
uv run sc plot admittance DatasetName
```

## Documentation

```bash
# Preview (localhost:8000)
uv run --group dev zensical serve

# Build static site
uv run --group dev zensical build
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
    - Build: `uv run --group dev zensical build -c`
    - Serve: `uv run --group dev zensical serve`
- **Scripts**: `uv run <script_name>` (e.g. `uv run sc-fit-squid`).
- **Clean**: `uv cache clean`
```
