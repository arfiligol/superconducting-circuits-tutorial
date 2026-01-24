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
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Script Authoring

CLI 腳本撰寫規範。

## Location

將工具腳本放在 `src/scripts/`：

```
src/scripts/
├── admittance_fit.py
├── flux_dependence_plot.py
└── ...
```

## Entry Points

在 `pyproject.toml` 註冊入口：

```toml
[project.scripts]
squid-model-fit = "src.scripts.admittance_fit:run_no_ls"
flux-dependence-plot = "src.scripts.flux_dependence_plot:run"
```

## Execution

腳本必須可透過模組方式執行：

```bash
uv run python -m src.scripts.admittance_fit
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

---

## Agent Rule { #agent-rule }

```markdown
## Script Authoring
- **Location**: `src/scripts/`
- **Naming**: `kebab-case` (e.g. `sc-convert-hfss`).
- **Structure**:
    - MUST have `def main():`.
    - MUST use `argparse` for arguments.
    - MUST use `if __name__ == "__main__": main()`.
- **Logic**: CLI scripts should be minimal wrappers around `sc_analysis` logic.
- **I/O**: Print to stdout is allowed here (and only here).
```
