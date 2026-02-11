---
aliases:
  - "Tech Stack"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Technology stack and tools"
version: v2.0.0
last_updated: 2026-02-08
updated_by: docs-team
---

# Tech Stack

The project uses a **Python + Julia** hybrid architecture.

## Languages & Tools

### Python

| Tool | Usage |
| :--- | :--- |
| `uv` | Environment & dependency management |
| `pandas`, `numpy` | Data processing & numerical analysis |
| `plotly` | Interactive visualization |
| `rich` | Colored logging & CLI output |
| `typer` | CLI framework (built on Click) |
| `zensical` | Documentation generation |
| `ruff`, `basedpyright` | Linting, Formatting, Type Checking |
| `pytest` | Automated testing |

### Julia

| Tool | Usage |
| :--- | :--- |
| `juliaup` | Julia version management |
| `JosephsonCircuits.jl` | Core simulation engine |

## Dependency Management

- **Python**: `pyproject.toml` (managed by `uv`)
- **Julia**: `Project.toml` + `Manifest.toml`

---

## Agent Rule { #agent-rule }

```markdown
## Tech Stack
- **Python** (Managed by `uv`):
    - **Data**: `pandas`, `numpy` (Core).
    - **Vis**: `plotly` (Interactive), `matplotlib` (Static).
    - **CLI**: `typer` (Framework).
    - **Logging**: `rich` (Colored output).
    - **GUI**: `nicegui` (Native App).
- **Julia** (Managed by `juliaup`):
    - **Sim**: `JosephsonCircuits.jl` (Core Engine).
- **Docs**: `zensical` (Static Site).
- **Config Files**:
    - Python: `pyproject.toml`
    - Julia: `Project.toml`
```
