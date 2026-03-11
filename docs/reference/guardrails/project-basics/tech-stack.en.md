---
aliases:
  - Tech Stack
  - Rewrite Stack
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/tech-stack
status: stable
owner: docs-team
audience: contributor
scope: Technical choices, desktop-shell direction, and shared tooling for the rewrite branch.
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Tech Stack

The target stack for this branch is **Next.js + FastAPI + CLI + Electron + Julia simulation core**.
UI, API, and CLI should share the same canonical definitions and validation rules rather than diverging into framework-specific behavior.

## Shared Languages

### Python

| Tool | Purpose |
| --- | --- |
| `uv` | dependency and environment management |
| `fastapi` | API framework |
| `pydantic` | schema and validation |
| `sqlmodel`, `sqlalchemy` | metadata persistence |
| `typer` | CLI framework |
| `numpy`, `pandas`, `scipy`, `lmfit` | numerics, analysis, fitting |
| `plotly`, `schemdraw` | charts and circuit-diagram generation |
| `juliacall` | Python ↔ Julia bridge |
| `rich` | logging and CLI output |
| `ruff`, `basedpyright`, `pytest` | lint / type / test |
| `zarr` | numeric trace storage |

### TypeScript / JavaScript

| Tool | Purpose |
| --- | --- |
| `Next.js` (App Router) | frontend framework |
| `React 19` | UI runtime |
| `TypeScript` | frontend language |
| `Tailwind CSS v4` | styling |
| `Radix UI` + `shadcn/ui` | primitives and app components |
| `next-themes` | theme switching |
| `SWR` | server-state fetching and cache |
| `react-hook-form` + `zod` | form state and validation |
| `lucide-react` | icons |
| `Playwright`, `Vitest` | frontend test stack |
| `Electron` | desktop shell for local app packaging |

### Julia

| Tool | Purpose |
| --- | --- |
| `juliaup` | Julia version management |
| `JosephsonCircuits.jl` | core circuit-simulation engine |

## Module Direction

### Frontend

- Next.js App Router
- TypeScript strict mode
- component system based on shadcn/ui + Radix
- no business workflow logic inside components

### Desktop

- Electron may be used as the desktop shell
- the Electron main/preload layers only handle desktop capabilities, window lifecycle, and secure IPC
- business workflow logic must not move into the Electron main process
- desktop packaging must not break the canonical frontend/backend/CLI boundaries

### Backend

- FastAPI + Pydantic
- service layer separated from persistence
- API handlers do I/O, validation, authorization, and response mapping only

### CLI

- Typer as the primary command framework
- CLI calls shared services/core rather than reimplementing API or UI logic
- every critical workflow must stay runnable without the web UI

### Scientific Core

- `JosephsonCircuits.jl` remains the simulation source of truth
- circuit definitions should feed simulation, schemdraw, and analysis from one canonical representation
- characterization / analysis should stay source-agnostic across trace origins

## Storage Direction

- metadata DB:
  - current baseline: `SQLite`
  - service target: `PostgreSQL`
- numeric traces:
  - baseline: `Zarr`
  - backend abstraction required for future extension

## Dependency Management

- Python: `pyproject.toml` + `uv.lock`
- Frontend: `frontend/package.json` + lockfile
- Julia: `Project.toml` / `Manifest.toml`

## Agent Rule { #agent-rule }

```markdown
## Tech Stack
- **Frontend**:
    - Next.js App Router
    - React 19
    - TypeScript
    - Tailwind CSS v4
    - Radix UI + shadcn/ui
    - next-themes
    - SWR
    - react-hook-form + zod
    - Electron is allowed as the desktop shell around the frontend
- **Backend**:
    - FastAPI
    - Pydantic
    - SQLModel / SQLAlchemy
    - Rich-compatible logging
- **CLI**:
    - Typer
    - must remain first-class, not a second-tier wrapper
- **Scientific core**:
    - JosephsonCircuits.jl via juliacall
    - plotly + schemdraw for visualization output
- **Quality tools**:
    - Ruff
    - BasedPyright
    - pytest
    - Vitest / Playwright when frontend exists
- **Storage direction**:
    - metadata DB: SQLite now, PostgreSQL target
    - numeric trace store: Zarr
- New UI work should target Next.js, not NiceGUI.
- Desktop packaging should use Electron around the frontend instead of reviving NiceGUI-native desktop assumptions.
```
