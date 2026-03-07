---
aliases:
  - "Tech Stack"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Tech Stack

This project is converging toward a **Python + Julia + Zarr Trace Store** scientific data platform.

## Languages and Responsibilities

### Python

| Tool | Purpose |
|---|---|
| `uv` | environment and dependency management |
| `numpy`, `pandas` | numeric and tabular processing |
| `plotly` | interactive visualization |
| `nicegui` | Web UI and local app shell |
| `CodeMirror` (via `nicegui.ui.codemirror`) | schema editor |
| `Ruff WebAssembly` (`@astral-sh/ruff-wasm`) | browser-side formatting |
| `Panzoom` | SVG zoom/pan interaction |
| `rich` | colored logging and CLI output |
| `typer` | CLI framework |
| `zensical` | documentation build |
| `ruff`, `basedpyright` | lint / type check |
| `pytest`, `Playwright` | automation and E2E verification |
| `zarr` | trace numeric payload storage (chunked ND arrays) |
| `fsspec`, `s3fs` | TraceStore backend abstraction (local / S3-compatible) |
| `sqlmodel`, `sqlalchemy` | metadata DB and repository/UoW |

### Julia

| Tool | Purpose |
|---|---|
| `juliaup` | Julia version management |
| `JosephsonCircuits.jl` | core superconducting-circuit simulation engine |

## Storage Strategy

The target storage direction is:

1. **Metadata DB**
   - current: `SQLite`
   - future server/deployment: `PostgreSQL`
2. **Numeric Trace Store**
   - current: local filesystem `Zarr`
   - future storage extension: `S3-compatible Zarr` (for example MinIO / S3 endpoints)

## Storage Responsibility Split

| Layer | Target Technology | Responsibility |
|---|---|---|
| Metadata | `SQLite` / `PostgreSQL` | `DesignRecord`, `TraceRecord`, `TraceBatchRecord`, `AnalysisRunRecord`, `DerivedParameterRecord` |
| Numeric payload | `Zarr` | S/Y/Z traces, sweep ND arrays, axes arrays |
| Object backend | local FS / MinIO / S3 | TraceStore backend (located via `TraceStoreRef.backend + store_key`; local path layout stays internal) |

## Dependency Management

- **Python**: `pyproject.toml` (managed by `uv`)
- **Julia**: `Project.toml` + `Manifest.toml`

---

## Agent Rule { #agent-rule }

```markdown
## Tech Stack
- **Python** (managed by `uv`):
    - **Data / Numeric**: `numpy`, `pandas`
    - **Trace Storage**: `zarr`
    - **Storage Backends**: `fsspec`, `s3fs`
    - **DB / ORM**: `sqlmodel`, `sqlalchemy`
    - **Vis**: `plotly`
    - **WebUI**: `nicegui`, `ui.codemirror`, `Ruff WebAssembly`, `Panzoom`
    - **CLI**: `typer`
    - **Logging**: `rich`
    - **Testing**: `pytest`, `Playwright`
- **Julia** (managed by `juliaup`):
    - **Sim**: `JosephsonCircuits.jl`
- **Docs**: `zensical`
- **Metadata DB direction**:
    - current: `SQLite`
    - deployment target: `PostgreSQL`
- **Numeric Trace Store direction**:
    - current: local `Zarr`
    - extension target: S3-compatible `Zarr` (for example MinIO / S3 endpoint)
- **Config files**:
    - Python: `pyproject.toml`
    - Julia: `Project.toml`
```
