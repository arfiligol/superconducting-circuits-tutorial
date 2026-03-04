---
aliases:
  - "測試規範 (Testing)"
  - "執行驗證測試"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/governance
status: stable
owner: docs-team
audience: team
scope: "自動化測試與文件更新驗證流程（含 Zensical 路由防 404）"
version: v1.2.0
last_updated: 2026-03-04
updated_by: docs-team
---

# 測試規範 (Testing)

本文件定義程式測試與文件更新驗證流程。  
重點：**任何文件異動都必須驗證不會產生 404。**

## Python 測試

我們使用 **Pytest**。

### 全量測試

```bash
uv run pytest
```

### 命名規範

- 檔案名：`test_<module>.py`
- 函式名：`test_<function_name>_<scenario>`

## Lint / Format（建議一併執行）

```bash
uv run ruff check .
uv run pre-commit run --all-files
```

## 文件更新驗證（防 404，必做）

只要變更任何 `docs/` 內容、`zensical*.toml` 導覽或頁面路徑，必須執行以下流程：

1. 同步 locale staging trees
2. 建置 zh-TW / en 站
3. 產出正式靜態站
4. 啟動本地站，驗證新頁路由
5. 確認沒有遺留失效 `.md` URL 導覽

### 標準指令

```bash
# 1) 同步文件來源
./scripts/prepare_docs_locales.sh

# 2) 建置（雙語）
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml

# 3) 靜態輸出（CI 對齊）
./scripts/build_docs_sites.sh
```

### 路由驗證（Playwright，推薦）

```bash
uv run python - <<'PY'
from playwright.sync_api import sync_playwright

routes = [
    "http://localhost:8000/superconducting-circuits-tutorial/",
    # 追加本次新增或移動的路由（不要含 .md）
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
```

### 導覽連結掃描（告警/差異檢查）

```bash
# 用於偵測本次變更是否引入新的 .md 型導覽鏈結
# 注意：目前站內存在歷史 .md 導覽，不能要求輸出為空。
rg -n "href=\"[^\"]+\\.md\"" docs/site
```

!!! warning "路由格式規則"
    UI/Browser 驗證時，頁面路徑必須用目錄路由（例如 `/notebooks/foo/`），  
    不可拿來源檔路徑（`.../foo.md`）當最終站點 URL。

## Julia 測試（需要時）

```bash
julia --project=. -e 'using Pkg; Pkg.test()'
```

---

## Agent Rule { #agent-rule }

```markdown
## Testing Commands
- **Python tests**: `uv run pytest`
- **Lint**: `uv run ruff check .`
- **Docs-change required checks**:
    1) `./scripts/prepare_docs_locales.sh`
    2) `uv run --group dev zensical build -f zensical.toml`
    3) `uv run --group dev zensical build -f zensical.en.toml`
    4) `./scripts/build_docs_sites.sh`
    5) Playwright route smoke (HTTP 200 + no "404 - Not found")
    6) `rg -n "href=\"[^\"]+\\.md\"" docs/site` for warning/diff review (not hard-fail in current baseline)
- **Route rule**: final docs URL uses directory routes (`/.../page/`), not source `.md` paths.
- **Julia tests (if touched)**: `julia --project=. -e 'using Pkg; Pkg.test()'`
```
