# 目錄結構 (Folder Structure)

本專案採用 **Clean Architecture** 原則進行目錄規劃。

## 核心目錄

```
superconducting-circuits-tutorial/
├── src/
│   ├── scripts/              # CLI Scripts (Entry Points)
│   ├── sc_analysis/          # Core Logic (Clean Architecture)
│   └── sc_app/               # [Planned] NiceGUI Native App
├── data/                     # Data Lifecycle
│   ├── raw/                  # Read-Only Input (HFSS/Maxwell)
│   ├── preprocessed/         # Intermediate JSON
│   └── processed/            # Analysis Results & Reports
├── docs/                     # Documentation (MkDocs)
├── examples/                 # Usage Examples
├── tests/                    # Tests
├── sandbox/                  # Experimental / Legacy Code
├── pyproject.toml            # Python Dependencies (uv)
├── uv.lock                   # Python Lock File
├── Project.toml              # Julia Dependencies
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
    - `sc_analysis/`: **Core Domain Logic** (Pydantic models, Algorithms). NO Print/Plot here.
    - `sc_app/`: **NiceGUI Native App**.
    - `scripts/`: **CLI Entry Points**. Use `argparse`. ONLY layer allowed to `print()`.
- **Data (`data/`)**:
    - `raw/`: **READ-ONLY**. HFSS/VNA files.
    - `preprocessed/`: Intermediate JSON.
    - `processed/`: Final Reports/Plots.
- **Config**: `pyproject.toml` (Python), `Project.toml` (Julia) in Root.
- **Decision Tree**:
    - IF "script to run from terminal" -> `src/scripts/`
    - IF "reusable logic" -> `src/sc_analysis/`
    - IF "simulation engine" -> `src/sc_analysis/infrastructure/simulation/`
    - IF "UI" -> `src/sc_app/`
```
