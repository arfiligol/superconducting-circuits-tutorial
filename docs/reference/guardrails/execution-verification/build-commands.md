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

## App / Worker Startup

WS10 之後的本地開發拓樸固定為三個進程：

- `uv run sc-app`
- `uv run sc-worker-simulation`
- `uv run sc-worker-characterization`

常用環境變數：

- `SC_APP_HOST`（default `127.0.0.1`）
- `SC_APP_PORT`（default `8080`）
- `SC_DATABASE_PATH`
- `SC_TRACE_STORE_ROOT`
- `SC_RQ_REDIS_URL`（preferred）
- `SC_REDIS_URL`（fallback alias）
- `SC_SIMULATION_QUEUE_NAME`
- `SC_CHARACTERIZATION_QUEUE_NAME`
- `SC_SESSION_SECRET`
- `SC_BOOTSTRAP_ADMIN_USERNAME`
- `SC_BOOTSTRAP_ADMIN_PASSWORD`
- `SC_WORKER_STALE_TIMEOUT_SECONDS`
- `SC_CLI_USERNAME`

!!! note "RQ backend"
    worker lanes 現在使用 `RQ + Redis`。正式 runtime 應提供可達的 Redis，
    例如設定 `SC_RQ_REDIS_URL=redis://127.0.0.1:6379/0`。

可選的一鍵 helper：

```bash
./scripts/dev_start.sh
./scripts/dev_stop.sh
```

!!! warning "Bootstrap admin"
    `.env.example` 只提供 placeholder。第一次啟動時系統可能依照
    `SC_BOOTSTRAP_ADMIN_USERNAME` / `SC_BOOTSTRAP_ADMIN_PASSWORD`
    建立或恢復 bootstrap admin；實際操作環境必須覆寫預設值。

## Integrator Smoke

```bash
# 必跑 runtime-first smoke
./scripts/run_integrator_smoke_suite.sh

# 把 repo-wide baseline checks 也改成 fatal gate
SC_SMOKE_STRICT=1 ./scripts/run_integrator_smoke_suite.sh

# 含 Playwright extended smoke
SC_SMOKE_INCLUDE_EXTENDED=1 ./scripts/run_integrator_smoke_suite.sh
```

`run_integrator_smoke_suite.sh` 目前包含：

- `uv run sc-worker-simulation --max-tasks 0`
- `uv run sc-worker-characterization --max-tasks 0`
- `uv run sc-app` startup probe（透過 `/login` readiness smoke）
- focused runtime validation:
  - `uv run pytest tests/app/pages/test_unaffected_page_routes.py tests/scripts/test_runtime_smokes.py tests/scripts/cli/test_sim_tasks.py -q`
- report-only baseline checks in default mode:
  - `uv run ruff format . --check`
  - `uv run ruff check .`
  - `uv run basedpyright`
  - `uv run pytest tests/core tests/app tests/scripts`

!!! note "Default vs strict"
    預設模式先完成 app + dual-worker runtime smoke，再報告 whole-repo red baseline。
    若要把 repo-wide format/type/test baseline 視為 fatal gate，請加上
    `SC_SMOKE_STRICT=1`。

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
- **App / Workers**:
    - App: `uv run sc-app`
    - Simulation worker: `uv run sc-worker-simulation`
    - Characterization worker: `uv run sc-worker-characterization`
    - Dev helpers: `./scripts/dev_start.sh`, `./scripts/dev_stop.sh`
- **Integrator Smoke**:
    - Required smoke: `./scripts/run_integrator_smoke_suite.sh`
    - Strict repo-wide gate: `SC_SMOKE_STRICT=1 ./scripts/run_integrator_smoke_suite.sh`
    - Extended smoke: `SC_SMOKE_INCLUDE_EXTENDED=1 ./scripts/run_integrator_smoke_suite.sh`
- **Clean**: `uv cache clean`
```
