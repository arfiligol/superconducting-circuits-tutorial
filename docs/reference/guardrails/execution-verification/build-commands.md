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

所有 CLI 統一由 `sc` 入口執行：

```bash
# 資料轉換
uv run sc preprocess admittance data/raw/layout_simulation/admittance/example.csv

# 分析擬合
uv run sc analysis fit lc-squid DatasetName

# 繪圖
uv run sc plot admittance DatasetName
```

## 文件

```bash
# 先產生語言 staging tree
./scripts/prepare_docs_locales.sh

# 預覽繁中站 (localhost:8000)
uv run --group dev zensical serve

# 預覽英文站 (localhost:8001)
uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001

# 建置繁中站
uv run --group dev zensical build

# 建置英文站
uv run --group dev zensical build -f zensical.en.toml

# 正式靜態輸出（含 /en 資產同步）
./scripts/build_docs_sites.sh
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
    - Prepare: `./scripts/prepare_docs_locales.sh`
    - Build (zh-TW): `uv run --group dev zensical build`
    - Build (en): `uv run --group dev zensical build -f zensical.en.toml`
    - Build (static artifact): `./scripts/build_docs_sites.sh`
    - Serve (zh-TW): `uv run --group dev zensical serve`
    - Serve (en): `uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001`
- **Scripts**: `uv run <script_name>` (e.g. `uv run sc-fit-squid`).
- **Clean**: `uv cache clean`
```
