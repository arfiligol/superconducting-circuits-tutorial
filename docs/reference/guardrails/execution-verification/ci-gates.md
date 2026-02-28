---
aliases:
  - "CI 品質關卡 (CI Gates)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# CI 品質關卡 (CI Gates)

本文件說明程式碼合併前必須通過的品質檢查。

## 品質關卡

所有 Pull Request 必須通過以下檢查才能合併：

### 1. Pre-commit Hooks

在本地執行 `git commit` 時，Pre-commit 會自動執行：

- **Ruff Check**: Linting (程式碼品質)
- **Ruff Format**: Formatting (程式碼格式)
- **BasedPyright**: Type Checking (類型檢查)

```bash
# 手動執行所有 Pre-commit 檢查
uv run pre-commit run --all-files
```

### 2. 文檔建置

```bash
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build
uv run --group dev zensical build -f zensical.en.toml

# 正式 CI 入口
./scripts/build_docs_sites.sh
```

!!! note "允許的警告"
    開發伺服器中的 `sitemap.xml 404` 警告是無害的，可以忽略。

### 3. 測試通過

```bash
uv run pytest
```

---

## Agent Rule { #agent-rule }

```markdown
## CI Gates
- **Mandatory Checks**:
    1. **Pre-commit**: `ruff format` + `ruff check` + `basedpyright`.
    2. **Build**: `./scripts/build_docs_sites.sh` must pass.
    3. **Test**: `pytest` must pass.
- **Tolerance**:
    - `zensical build` during docs preview: allow benign `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
```
