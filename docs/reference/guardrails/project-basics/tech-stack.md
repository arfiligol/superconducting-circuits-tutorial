---
aliases:
  - "技術堆疊 (Tech Stack)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# 技術堆疊 (Tech Stack)

本專案採用 **Python + Julia** 雙語言架構，各有明確分工。

## 語言與用途

### Python

| 工具 | 用途 |
|---|---|
| `uv` | 環境與依賴管理 (取代 pip, venv) |
| `pandas`, `numpy` | 資料處理與數值計算 |
| `plotly` | 互動式可視化 |
| `nicegui` | WebUI 框架（頁面與互動元件） |
| `CodeMirror`（透過 `nicegui.ui.codemirror`） | WebUI Code Editor（Schema Editor 即時編輯器） |
| `Ruff WebAssembly`（`@astral-sh/ruff-wasm`） | 在瀏覽器端直接執行 Python 格式化（Schema Editor） |
| `Panzoom`（前端 JS） | Live Preview 的 SVG 縮放與平移互動層 |
| `rich` | 彩色日誌與 CLI 輸出 |
| `typer` | CLI 框架 (基於 Click) |
| `zensical` | 文檔生成 |
| `ruff`, `basedpyright` | Lint, Format, Type Check |
| `pytest` | 自動化測試 |

### Julia

| 工具 | 用途 |
|---|---|
| `juliaup` | Julia 版本管理 |
| `JosephsonCircuits.jl` | 核心超導模擬引擎 |

## 依賴管理

- **Python**: `pyproject.toml` (由 `uv` 管理)
- **Julia**: `Project.toml` + `Manifest.toml`

---

## Agent Rule { #agent-rule }

```markdown
## Tech Stack
- **Python** (Managed by `uv`):
    - **Data**: `pandas`, `numpy` (Core).
    - **Vis**: `plotly` (Interactive), `matplotlib` (Static).
    - **WebUI**: `nicegui` (UI framework), `ui.codemirror` / CodeMirror (Code Editor), `Ruff WebAssembly` (browser formatter), `Panzoom` (SVG zoom/pan interaction).
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
