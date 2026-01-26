---
aliases:
  - "Folder Structure"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Project directory structure and layering"
version: v1.0.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Folder Structure

This project follows **Clean Architecture** principles.

## Core Directory

```
superconducting-circuits-tutorial/
├── src/
│   ├── core/                 # Domain & Application Logic
│   │   ├── analysis/         # Analysis Logic (Clean Architecture)
│   │   ├── simulation/       # Circuit Simulation (JuliaCall ↔ Julia)
│   │   └── shared/           # Shared Utilities (visualization, utils)
│   ├── app/                  # [Planned] NiceGUI App
│   └── scripts/              # CLI Entry Points
│       ├── analysis/         # Analysis Scripts (admittance_fit.py etc)
│       └── simulation/       # Simulation Scripts (run_lc.py etc)
├── data/                     # Data Lifecycle
│   ├── raw/                  # Read-Only Input (HFSS/VNA)
│   ├── preprocessed/         # Intermediate JSON
│   └── processed/            # Analysis Results & Reports
├── docs/                     # Documentation (MkDocs)
├── examples/                 # Usage Examples
├── tests/                    # Tests
├── sandbox/                  # Experimental / Legacy Code
├── pyproject.toml            # Python Dependencies (uv)
├── uv.lock                   # Python Lock File
├── juliapkg.json             # Julia Dependencies (JosephsonCircuits.jl)
├── Project.toml              # Julia Project Settings
├── Manifest.toml             # Julia Lock File
└── .gitignore                # Git Ignore Rules
```

## Layering Principles

1.  **Domain** (Inner): Pure business logic, Pydantic schemas. No external dependencies.
2.  **Application**: Use Case orchestration. Depends only on Domain.
3.  **Infrastructure** (Outer): Framework integration (CLI, Web App), I/O. Depends on Application and Domain.

Dependency direction is always **Inward**.

---

## Agent Rule { #agent-rule }

```markdown
## Folder Structure
- **Source Code (`src/`)**:
    - `core/analysis/`: **Data Analysis** (Pydantic models, Fitting, Extraction). NO Print here, use `logging`.
    - `core/simulation/`: **Circuit Simulation** (JuliaCall adapter to JosephsonCircuits.jl).
    - `core/shared/`: **Shared Utilities** (logging, visualization, persistence, units).
    - `app/`: **NiceGUI Native App**.
    - `scripts/analysis/`: **Analysis CLI Entry Points**. Use `argparse`. ONLY layer allowed to `print()`.
    - `scripts/simulation/`: **Simulation CLI Entry Points**.
    - `scripts/database/`: **Database CLI Entry Points**.
- **Data (`data/`)**:
    - `raw/`: **READ-ONLY**. HFSS/VNA files.
    - `preprocessed/`: Intermediate JSON (Legacy).
    - `processed/`: Final Reports/Plots.
    - `database.db`: SQLite database.
- **Config** (Root):
    - `pyproject.toml`: Python Dependencies (uv).
    - `juliapkg.json`: Julia Dependencies (JosephsonCircuits.jl).
    - `Project.toml`: Julia Project Settings.
- **Decision Tree**:
    - IF "simulation CLI" -> `src/scripts/simulation/`
    - IF "analysis CLI" -> `src/scripts/analysis/`
    - IF "database CLI" -> `src/scripts/database/`
    - IF "reusable analysis logic" -> `src/core/analysis/`
    - IF "simulation interop" -> `src/core/simulation/`
    - IF "shared plotting/utils/logging/persistence" -> `src/core/shared/`
    - IF "UI" -> `src/app/`
```
