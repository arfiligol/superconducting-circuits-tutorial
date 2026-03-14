---
aliases:
  - Tech Stack
  - 技術堆疊
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/tech-stack
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的技術選型、desktop 包裝方向與共享工具規範。
version: v2.2.0
last_updated: 2026-03-14
updated_by: codex
---

# Tech Stack

本 branch 的目標技術棧是 **Next.js + FastAPI + CLI + Electron + Julia simulation core**。
原則上，UI、API、CLI 必須共用同一套核心定義與驗證規則，不再把 NiceGUI 作為主要實作方向。

## Shared Languages

### Python

| 工具 | 用途 |
| --- | --- |
| `uv` | 依賴與虛擬環境管理 |
| `fastapi` | API framework |
| `pydantic` | schema / validation |
| `sqlmodel`, `sqlalchemy` | metadata persistence |
| `casbin` | app backend authorization baseline |
| `typer` | CLI framework |
| `numpy`, `pandas`, `scipy`, `lmfit` | 數值、分析、擬合 |
| `plotly`, `schemdraw` | 視覺化與電路圖生成 |
| `juliacall` | Python ↔ Julia bridge |
| `rich` | logging 與 CLI 輸出 |
| `ruff`, `basedpyright`, `pytest` | lint / type / test |
| `zarr` | numeric trace storage |

### TypeScript / JavaScript

| 工具 | 用途 |
| --- | --- |
| `Next.js` (App Router) | frontend framework |
| `React 19` | UI runtime |
| `TypeScript` | frontend language |
| `Tailwind CSS v4` | styling |
| `Radix UI` + `shadcn/ui` | UI primitives 與 app components |
| `next-themes` | theme switching |
| `SWR` | server-state fetching and cache |
| `react-hook-form` + `zod` | form state and validation |
| `lucide-react` | icons |
| `Playwright`, `Vitest` | frontend test stack |
| `Electron` | desktop shell for local app packaging |

### Julia

| 工具 | 用途 |
| --- | --- |
| `juliaup` | Julia version management |
| `JosephsonCircuits.jl` | 核心電路模擬引擎 |

## Module Direction

### Frontend

- Next.js App Router
- TypeScript strict mode
- component system based on shadcn/ui + Radix
- 不在 component 內直接實作業務流程或硬編碼 API contract

### Desktop

- Electron 可作為 desktop shell
- Electron main/preload 層只處理桌面能力、視窗生命週期與安全 IPC
- 不可把業務流程塞進 Electron main process
- desktop 包裝不改變 canonical frontend/backend/CLI 邊界

### Backend

- FastAPI + Pydantic
- 服務層與資料存取分離
- API 層只做 I/O、驗證、mapping、授權與回應
- multi-user app authorization baseline 採 `Casbin`
- `JWT` / refresh token 負責 authentication；capabilities 與 allowed actions 由 backend authorization engine materialize

### CLI

- Typer 作為主要命令列框架
- CLI 直接呼叫共享 service / core，而非複製 API 或 UI 邏輯
- 所有關鍵工作流都需要可由 CLI 觸發

### Scientific Core

- `JosephsonCircuits.jl` 仍是 simulation source of truth
- circuit definition 應能同時餵給 simulation、schemdraw、analysis
- characterization / analysis 對 trace source 保持 source-agnostic

## Storage Direction

- metadata DB：
  - current baseline: `SQLite`
  - service target: `PostgreSQL`
- numeric traces：
  - baseline: `Zarr`
  - backend abstraction required for future extension

## Dependency Management

- Python: `pyproject.toml` + `uv.lock`
- Frontend: `frontend/package.json` + lockfile
- Julia: `Project.toml` / `Manifest.toml`

## Agent Rule { #agent-rule }

```markdown
## Tech Stack
- **Frontend**:
    - Next.js App Router
    - React 19
    - TypeScript
    - Tailwind CSS v4
    - Radix UI + shadcn/ui
    - next-themes
    - SWR
    - react-hook-form + zod
    - Electron is allowed as the desktop shell around the frontend
- **Backend**:
    - FastAPI
    - Pydantic
    - SQLModel / SQLAlchemy
    - Casbin as the backend authorization baseline for the multi-user app
    - Rich-compatible logging
- **CLI**:
    - Typer
    - must remain first-class, not a second-tier wrapper
- **Scientific core**:
    - JosephsonCircuits.jl via juliacall
    - plotly + schemdraw for visualization output
- **Quality tools**:
    - Ruff
    - BasedPyright
    - pytest
    - Vitest / Playwright when frontend exists
- **Storage direction**:
    - metadata DB: SQLite now, PostgreSQL target
    - numeric trace store: Zarr
- New UI work should target Next.js, not NiceGUI.
- Desktop packaging should use Electron around the frontend instead of reviving NiceGUI-native desktop assumptions.
```
