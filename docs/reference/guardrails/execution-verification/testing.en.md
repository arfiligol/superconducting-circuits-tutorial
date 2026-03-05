---
aliases:
  - "Testing Standards"
  - "Execution Verification Testing"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/governance
status: stable
owner: docs-team
audience: team
scope: "Automated testing and docs-update verification flow (with Zensical anti-404 checks)"
version: v1.3.0
last_updated: 2026-03-05
updated_by: codex
---

# Testing Standards

This document defines code-test and documentation-update verification flow.
Core rule: **every docs change must verify no 404 regression**.

## Python Testing

We use **Pytest**.

### Full test run

```bash
uv run pytest
```

### Naming conventions

- File: `test_<module>.py`
- Function: `test_<function_name>_<scenario>`

## Lint / Format (recommended with tests)

```bash
uv run ruff check .
uv run pre-commit run --all-files
```

## Docs Update Verification (anti-404, required)

Whenever you change any `docs/` content, `zensical*.toml` navigation, or page paths, run this flow:

1. sync locale staging trees
2. build both zh-TW and en sites
3. produce canonical static artifacts
4. run local route checks
5. ensure no stale `.md` navigation links remain

### Standard commands

```bash
# One-shot full docs integrity check (recommended)
./scripts/verify_docs_integrity.sh

# 0) Validate nav routes against docs source files first
uv run python scripts/check_docs_nav_routes.py --check-source

# 1) Sync docs locales
./scripts/prepare_docs_locales.sh

# 2) Build both locales
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml

# 3) Canonical static output (CI-aligned)
./scripts/build_docs_sites.sh

# 4) Validate nav routes against built html files
uv run python scripts/check_docs_nav_routes.py --check-built
```

### Route smoke check (Playwright, recommended)

```bash
uv run python - <<'PY'
from playwright.sync_api import sync_playwright

routes = [
    "http://localhost:8000/superconducting-circuits-tutorial/",
    # Append newly added or moved routes (without .md)
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

### `.md` compatibility route check (required)

```bash
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

### Navigation-link scan (warning/diff check)

```bash
# Use this to detect whether this change introduced new .md-style nav links.
# Note: current site baseline already contains legacy .md links; do not hard-fail on non-empty output.
rg -n "href=\"[^\"]+\\.md\"" docs/site
```

!!! warning "Route format rule"
    Browser verification must use directory routes (for example `/notebooks/foo/`),
    never source-file URLs like `.../foo.md`.

## Julia tests (when applicable)

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
    1) `uv run python scripts/check_docs_nav_routes.py --check-source`
    2) `./scripts/prepare_docs_locales.sh`
    3) `uv run --group dev zensical build -f zensical.toml`
    4) `uv run --group dev zensical build -f zensical.en.toml`
    5) `./scripts/build_docs_sites.sh`
    6) `uv run python scripts/check_docs_nav_routes.py --check-built`
    7) Playwright route smoke (HTTP 200 + no "404 - Not found")
    8) `.md` compatibility route check (legacy `.md` URL auto-normalizes to canonical route)
    9) `rg -n "href=\"[^\"]+\\.md\"" docs/site` for warning/diff review (not hard-fail against current baseline)
- **Route rule**: final docs URL uses directory routes (`/.../page/`), not source `.md` paths.
- **Julia tests (if touched)**: `julia --project=. -e 'using Pkg; Pkg.test()'`
```
