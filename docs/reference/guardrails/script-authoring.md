---
aliases:
  - "Script Authoring Rules"
  - "腳本撰寫規範"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "CLI 腳本撰寫規範：位置、入口、文件"
version: v0.2.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Script Authoring

CLI 腳本撰寫規範。

## Location

將工具腳本放在 `src/scripts/`，並依功能分類：

```
src/scripts/
├── analysis/              # 分析相關腳本
│   ├── admittance_fit.py
│   └── flux_dependence_plot.py
└── simulation/            # 模擬相關腳本
    └── run_lc.py
```

## Entry Points

在 `pyproject.toml` 註冊入口：

```toml
[project.scripts]
# Analysis
sc-fit-squid = "scripts.analysis.admittance_fit:run_no_ls"
flux-dependence-plot = "scripts.analysis.flux_dependence_plot:run"

# Simulation
sc-simulate-lc = "scripts.simulation.run_lc:main"
```

## Execution

腳本必須可透過模組方式執行：

```bash
uv run python -m scripts.analysis.admittance_fit
uv run python -m scripts.simulation.run_lc
```

## Help Message

實作 `--help` 描述：

```python
parser = argparse.ArgumentParser(
    description="Fit SQUID LC model to admittance data",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
```

## Documentation

新增腳本時：
1. 在 [CLI Reference](../cli/index.md) 新增對應頁面
2. 在對應的 [How-to](../../how-to/index.md) 新增使用指南
3. 更新 README.md（如有必要）

## Related

- [Data Handling](data-handling.md) - 輸出路徑規範
- [CLI Reference](../cli/index.md) - 指令參考
- [Folder Structure](folder-structure.md) - 目錄結構

---

## Agent Rule { #agent-rule }

```markdown
## Script Authoring
- **Location**: 
    - Analysis scripts: `src/scripts/analysis/`
    - Simulation scripts: `src/scripts/simulation/`
- **Naming**: `kebab-case` (e.g. `sc-simulate-lc`, `sc-fit-squid`).
- **Structure**:
    - MUST have `def main():`.
    - MUST use `argparse` for arguments.
    - MUST use `if __name__ == "__main__": main()`.
- **Logic**: 
    - Analysis CLI: minimal wrappers around `core/analysis` logic.
    - Simulation CLI: minimal wrappers around `core/simulation` logic.
- **I/O**: Print to stdout is allowed here (and only here).
```

