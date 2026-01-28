---
aliases:
  - "執行指令 (Build Commands)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# 執行指令 (Build Commands)

本文件列出所有常用的建置與執行指令。

## 環境建置

### Python (uv)

```bash
# 首次安裝或同步依賴 (自動建立 .venv)
uv sync

# 更新依賴
uv sync --upgrade
```

### Julia

```bash
# 首次安裝或同步依賴
julia --project=. -e 'using Pkg; Pkg.instantiate()'

# 更新依賴
julia --project=. -e 'using Pkg; Pkg.update()'
```

## CLI 腳本執行

所有腳本皆由 `uv run <script-name>` 執行：

```bash
# 資料轉換
uv run sc-preprocess-admittance --input data.csv

# 分析擬合
uv run sc-fit-squid

# 繪圖
uv run sc-plot-admittance
```

## 文件

```bash
# 預覽 (localhost:8000)
uv run mkdocs serve

# 建置靜態網站
uv run mkdocs build
```

---

## Agent Rule { #agent-rule }

```markdown
## Run / Build Commands
- **Python Install**: `uv sync` (Creates .venv + dependencies).
- **Julia Install**:
    - `julia --project=. -e 'using Pkg; Pkg.instantiate()'`
    - `julia --project=. -e 'using Pkg; Pkg.update()'`
- **Docs**:
    - Build: `uv run mkdocs build --clean`
    - Serve: `uv run mkdocs serve`
- **Scripts**: `uv run <script_name>` (e.g. `uv run sc-fit-squid`).
- **Clean**: `uv cache clean`
```
