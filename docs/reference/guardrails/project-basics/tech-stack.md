---
aliases:
  - "技術堆疊 (Tech Stack)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# 技術堆疊 (Tech Stack)

本專案正在收斂為一個 **Python + Julia + Zarr Trace Store** 的科學資料平台。

## 語言與用途

### Python

| 工具 | 用途 |
|---|---|
| `uv` | 環境與依賴管理 |
| `numpy`, `pandas` | 數值與資料處理 |
| `plotly` | 互動式視覺化 |
| `nicegui` | Web UI 與本地應用 shell |
| `CodeMirror`（透過 `nicegui.ui.codemirror`） | Schema Editor |
| `Ruff WebAssembly`（`@astral-sh/ruff-wasm`） | 瀏覽器端格式化 |
| `Panzoom` | SVG zoom/pan 互動層 |
| `rich` | 彩色日誌與 CLI 輸出 |
| `typer` | CLI 框架 |
| `zensical` | 文檔建置 |
| `ruff`, `basedpyright` | Lint / Type Check |
| `pytest`, `Playwright` | 自動化測試與 E2E 驗證 |
| `zarr` | Trace numeric payload storage（chunked ND arrays） |
| `fsspec`, `s3fs` | TraceStore backend abstraction（local / S3-compatible） |
| `sqlmodel`, `sqlalchemy` | metadata DB 與 repository/UoW |

### Julia

| 工具 | 用途 |
|---|---|
| `juliaup` | Julia 版本管理 |
| `JosephsonCircuits.jl` | 核心超導電路模擬引擎 |

## Storage Strategy

本專案的 target storage direction 為：

1. **Metadata DB**
   - 現階段：`SQLite`
   - 未來 server/deployment：`PostgreSQL`
2. **Numeric Trace Store**
   - 現階段：local filesystem `Zarr`
   - 未來 storage extension：`S3-compatible Zarr`（例如 MinIO / S3 endpoint）

## Storage Responsibility Split

| Layer | Target Technology | Responsibility |
|---|---|---|
| Metadata | `SQLite` / `PostgreSQL` | `DesignRecord`、`TraceRecord`、`TraceBatchRecord`、`AnalysisRunRecord`、`DerivedParameterRecord` |
| Numeric payload | `Zarr` | S/Y/Z traces、sweep ND arrays、axes arrays |
| Object backend | local FS / MinIO / S3 | TraceStore backend |

## 依賴管理

- **Python**: `pyproject.toml`（由 `uv` 管理）
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
