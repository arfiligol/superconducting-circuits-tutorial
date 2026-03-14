---
aliases:
  - Build Commands
  - 執行指令
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的 frontend、backend、desktop、CLI、docs 與 repo-root orchestration 常用指令。
version: v2.3.0
last_updated: 2026-03-14
updated_by: codex
---

# Build Commands

本文件列出 rewrite branch 目前可用的 repo-root orchestration 與 workspace 指令。
rewrite foundation 必須使用獨立於 legacy NiceGUI runtime 的 entrypoints。

!!! info "How to use this page"
    先決定你是在跑 `repo baseline`、單一 workspace、還是 docs build。
    不要每次都從頭到尾把所有命令跑一遍；依 touched area 挑最小必要集合。

## Command Map

| Situation | Open this section |
| --- | --- |
| 初次進 repo 或補齊基礎依賴 | `Current Baseline` |
| 要啟動 rewrite 全域協調流程 | `Rewrite Root Orchestration` |
| 只改單一 workspace | `Rewrite Workspaces` |
| 只改 docs / nav / frontmatter | `Docs` |

## Current Baseline

!!! tip "Run this first on a fresh checkout"

```bash
uv sync
julia --project=. -e 'using Pkg; Pkg.instantiate()'
./scripts/prepare_docs_locales.sh
```

## Rewrite Root Orchestration

!!! info "Use these when you want repo-level orchestration"

```bash
npm run rewrite:install
npm run rewrite:check
npm run rewrite:build
npm run rewrite:dev
npm run rewrite:stop
```

## Rewrite Workspaces

=== "Frontend"

    ```bash
    npm install --prefix frontend
    npm run dev --prefix frontend
    npm run test --prefix frontend
    npm run lint --prefix frontend
    npm run typecheck --prefix frontend
    npm run build --prefix frontend
    ```

=== "Backend"

    ```bash
    cd backend && uv sync
    cd backend && uv run pytest
    cd backend && uv run uvicorn src.app.main:app --reload --port 8000
    ```

=== "Desktop"

    ```bash
    npm install --prefix desktop
    npm run dev --prefix desktop
    npm run lint --prefix desktop
    npm run build --prefix desktop
    ```

=== "CLI"

    ```bash
    uv run sc --help
    ```

## Docs

!!! warning "Docs build always needs prepare first"
    若你改了 docs 內容、導覽或 frontmatter，先跑 `./scripts/prepare_docs_locales.sh`，再做 build / route check。

```bash
uv run python scripts/check_docs_nav_routes.py --check-source
./scripts/prepare_docs_locales.sh
uv run --group dev zensical build -f zensical.toml
./scripts/build_docs_sites.sh
uv run python scripts/check_docs_nav_routes.py --check-built
```

??? info "Why both source and built checks exist"
    `--check-source` 先驗證來源樹與 nav 是否一致。
    `--check-built` 再驗證最終 build 出來的路徑是否能被站點正確解析。

## Agent Rule { #agent-rule }

```markdown
## Run / Build Commands
- **Rewrite root orchestration**:
    - `npm run rewrite:install`
    - `npm run rewrite:check`
    - `npm run rewrite:build`
    - `npm run rewrite:dev`
    - `npm run rewrite:stop`
- **Python install**: `uv sync`
- **Julia install**: `julia --project=. -e 'using Pkg; Pkg.instantiate()'`
- **Frontend**:
    - `npm install --prefix frontend`
    - `npm run dev --prefix frontend`
    - `npm run test --prefix frontend`
    - `npm run lint --prefix frontend`
    - `npm run typecheck --prefix frontend`
    - `npm run build --prefix frontend`
- **Backend**:
    - `cd backend && uv sync`
    - `cd backend && uv run pytest`
    - `cd backend && uv run uvicorn src.app.main:app --reload --port 8000`
- **Desktop**:
    - `npm install --prefix desktop`
    - `npm run dev --prefix desktop`
    - `npm run lint --prefix desktop`
    - `npm run build --prefix desktop`
- **CLI**: `uv run sc --help`
- **Docs**:
    - `uv run python scripts/check_docs_nav_routes.py --check-source`
    - `./scripts/prepare_docs_locales.sh`
    - `uv run --group dev zensical build -f zensical.toml`
    - `./scripts/build_docs_sites.sh`
    - `uv run python scripts/check_docs_nav_routes.py --check-built`
```
