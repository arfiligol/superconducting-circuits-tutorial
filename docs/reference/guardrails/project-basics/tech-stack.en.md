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
| `fsspec`, `s3fs` | TraceStore backend abstraction (currently local-only; future extension-safe) |
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
   - future storage extension (deferred): `S3-compatible Zarr` (for example MinIO / S3 endpoints)

## Storage Responsibility Split

| Layer | Target Technology | Responsibility |
|---|---|---|
| Metadata | `SQLite` / `PostgreSQL` | `DesignRecord`, `TraceRecord`, `TraceBatchRecord`, `AnalysisRunRecord`, `DerivedParameterRecord` |
| Numeric payload | `Zarr` | S/Y/Z traces, sweep ND arrays, axes arrays |
| Object backend | local FS (current) | TraceStore backend (located via `TraceStoreRef.backend + store_key`; local path layout stays internal) |

## TraceStore Runtime Config

Current runtime config contract:

- `SC_TRACE_STORE_BACKEND`
  - `local_zarr` (the only active backend right now)
- `SC_TRACE_STORE_ROOT`
  - root path for the local backend

If object-storage extension work resumes later, add:

- `SC_TRACE_STORE_S3_BUCKET`
- `SC_TRACE_STORE_S3_PREFIX`
- `SC_TRACE_STORE_S3_ENDPOINT_URL`

The application / UI layer must not parse local `store_uri` paths directly. Backend locator resolution must go through the persistence `TraceStore` abstraction.

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
- **DB schema convergence**:
    - no historical-data migration in the current program
    - when physical schema convergence begins, cut directly to the new schema
- **Numeric Trace Store direction**:
    - current: local `Zarr`
    - extension target (deferred): S3-compatible `Zarr` (for example MinIO / S3 endpoint)
- **Config files**:
    - Python: `pyproject.toml`
    - Julia: `Project.toml`
```
