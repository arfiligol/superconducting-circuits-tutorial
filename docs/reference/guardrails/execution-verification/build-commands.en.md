---
aliases:
  - "Build Commands"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Common build and execution commands"
version: v2.1.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Build Commands

List of commonly used build and execution commands.

## Environment Setup

### Python (uv)

```bash
# First install or sync dependencies (creates .venv)
uv sync

# Update dependencies
uv sync --upgrade
```

### Julia

```bash
# Instantiate environment
julia --project=. -e 'using Pkg; Pkg.instantiate()'

# Update dependencies
julia --project=. -e 'using Pkg; Pkg.update()'
```

## CLI Scripts

Use the unified `sc` entrypoint for CLI commands:

```bash
# Data Preprocessing
uv run sc preprocess admittance data/raw/layout_simulation/admittance/example.csv

# Analysis Fitting
uv run sc analysis fit lc-squid DatasetName

# Plotting
uv run sc plot admittance DatasetName
```

## Documentation

```bash
# Generate locale staging trees first
./scripts/prepare_docs_locales.sh

# Preview zh-TW site (localhost:8000)
uv run --group dev zensical serve

# Preview English site (localhost:8001)
uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001

# Build zh-TW site
uv run --group dev zensical build

# Build English site
uv run --group dev zensical build -f zensical.en.toml

# Canonical static output (emits to `docs/site/`, includes /en asset sync)
./scripts/build_docs_sites.sh
```

### Docs route verification (anti-404)

```bash
# Start docs site first (example: zh-TW)
uv run --group dev zensical serve -f zensical.toml -a localhost:8000

# In another terminal, run Playwright route smoke checks (replace routes)
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

# Scan .md navigation links (warning/diff check, not hard-fail empty in current baseline)
rg -n "href=\"[^\"]+\\.md\"" docs/site

# Verify legacy .md URLs auto-normalize to canonical directory routes (prevents typed-URL 404s)
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

!!! warning "URL format"
    Validate directory routes (for example `/foo/bar/`), not source-file URLs (`.../bar.md`).

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
    - Build (static artifact, emits to `docs/site/`): `./scripts/build_docs_sites.sh`
    - Serve (zh-TW): `uv run --group dev zensical serve`
    - Serve (en): `uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001`
    - Route smoke: Playwright check (HTTP 200 + no "404 - Not found")
    - `.md` compatibility route check (legacy `.md` URL auto-redirects to canonical route)
    - Broken nav scan (warning/diff): `rg -n "href=\"[^\"]+\\.md\"" docs/site`
- **Scripts**: `uv run <script_name>` (e.g. `uv run sc-fit-squid`).
- **Clean**: `uv cache clean`
```
