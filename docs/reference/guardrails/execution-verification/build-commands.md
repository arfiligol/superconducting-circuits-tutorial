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
# 一鍵完整檢查（建議）
./scripts/verify_docs_integrity.sh

# 檢查 nav 是否有指向不存在的來源檔
uv run python scripts/check_docs_nav_routes.py --check-source

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

# 正式靜態輸出（輸出到 `docs/site/`，含 /en 資產同步）
./scripts/build_docs_sites.sh

# 檢查 nav 是否有指向不存在的 built html
uv run python scripts/check_docs_nav_routes.py --check-built
```

### 文件路由驗證（防 404）

```bash
# 先啟動站點（範例：zh-TW）
uv run --group dev zensical serve -f zensical.toml -a localhost:8000

# 另開終端，用 Playwright 檢查關鍵路由（自行替換 routes）
uv run python - <<'PY'
from playwright.sync_api import sync_playwright
routes = [
    "http://localhost:8000/superconducting-circuits-tutorial/",
]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    for url in routes:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        assert resp is not None and resp.status == 200, f"Route failed: {url}"
        assert "404 - Not found" not in page.content(), f"404 body found: {url}"
    b.close()
PY

# 掃描 .md 導覽鏈結（用於告警/差異檢查，非硬性必須為空）
rg -n "href=\"[^\"]+\\.md\"" docs/site

# 驗證 legacy .md 路由會自動導向 canonical 目錄路由（避免使用者手打 URL 404）
uv run python - <<'PY'
from playwright.sync_api import sync_playwright
legacy_url = "http://localhost:8000/superconducting-circuits-tutorial/explanation/physics/schur-complement-kron-reduction.md"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    page.goto(legacy_url, wait_until="domcontentloaded", timeout=30000)
    assert page.locator("h1").first.inner_text().strip() != "404 - Not found"
    assert page.url.endswith("/explanation/physics/schur-complement-kron-reduction/")
    b.close()
PY
```

!!! warning "網址格式"
    實際驗證路由請用目錄 URL（例如 `/foo/bar/`），不要用來源檔 URL（`.../bar.md`）。

---

## Agent Rule { #agent-rule }

```markdown
## Run / Build Commands
- **Python Install**: `uv sync` (Creates .venv + dependencies).
- **Julia Install**:
    - `julia --project=. -e 'using Pkg; Pkg.instantiate()'`
    - `julia --project=. -e 'using Pkg; Pkg.update()'`
- **Docs**:
    - Route source check: `uv run python scripts/check_docs_nav_routes.py --check-source`
    - Prepare: `./scripts/prepare_docs_locales.sh`
    - Build (zh-TW): `uv run --group dev zensical build`
    - Build (en): `uv run --group dev zensical build -f zensical.en.toml`
    - Build (static artifact, outputs to `docs/site/`): `./scripts/build_docs_sites.sh`
    - Route built-html check: `uv run python scripts/check_docs_nav_routes.py --check-built`
    - Serve (zh-TW): `uv run --group dev zensical serve`
    - Serve (en): `uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001`
    - Route smoke: Playwright check (HTTP 200 + no "404 - Not found")
    - `.md` compatibility route check (legacy `.md` URL auto-redirects to canonical route)
    - Broken nav scan (warning/diff): `rg -n "href=\"[^\"]+\\.md\"" docs/site`
- **Scripts**: `uv run <script_name>` (e.g. `uv run sc-fit-squid`).
- **Clean**: `uv cache clean`
```
