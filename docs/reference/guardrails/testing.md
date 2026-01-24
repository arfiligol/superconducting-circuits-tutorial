# 測試規範 (Testing)

本文件說明專案的自動化測試方法與執行指令。

## Python 測試

我們使用 **Pytest** 作為 Python 測試框架。

### 執行測試

```bash
uv run pytest
```

### 測試檔案位置

測試檔案位於 `tests/` 目錄下，結構與 `src/sc_analysis/` 對應：

```
tests/
├── domain/
│   └── test_xxx.py
├── application/
│   └── test_yyy.py
└── infrastructure/
    └── test_zzz.py
```

### 測試命名規範

- 檔案名：`test_<module>.py`
- 函式名：`test_<function_name>_<scenario>`

## Julia 測試

```bash
julia --project=. -e 'using Pkg; Pkg.test()'
```

---

## Agent Rule { #agent-rule }

```markdown
## Testing Commands
- **Framework**: `pytest`
- **Command**: `uv run pytest` (Runs all tests in `tests/`)
- **Naming**:
    - Files: `test_*.py`
    - Funcs: `test_*()`
- **Structure**: `tests/` mirrors `src/sc_analysis/` structure.
    - e.g. `src/sc_analysis/domain/model.py` -> `tests/domain/test_model.py`.
- **Julia Tests**: `julia --project=. -e 'using Pkg; Pkg.test()'`
```
