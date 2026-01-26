---
aliases:
  - "目錄結構 (Folder Structure)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# 目錄結構 (Folder Structure)

本專案採用 **Clean Architecture** 原則進行目錄規劃。

## 核心目錄

```
superconducting-circuits-tutorial/
├── src/
│   ├── core/                 # Domain & Application Logic
│   │   ├── analysis/         # 數據分析 (Clean Architecture)
│   │   ├── simulation/       # 電路模擬 (JuliaCall ↔ Julia)
│   │   └── shared/           # 共用工具 (visualization, utils)
│   ├── app/                  # [Planned] NiceGUI App
│   └── scripts/              # CLI Entry Points
│       ├── analysis/         # 分析腳本 (admittance_fit.py 等)
│       └── simulation/       # 模擬腳本 (run_lc.py 等)
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

## 分層原則

1.  **Domain** (最內層): 純粹的業務邏輯、Pydantic schemas。不依賴任何外部層。
2.  **Application**: Use Cases 編排，只依賴 Domain。
3.  **Infrastructure** (最外層): 框架整合 (CLI, Web App)、File I/O。依賴 Application 和 Domain。

依賴方向永遠是**由外向內**。

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
