# Migration Master Plan

最後更新：2026-03-12

這份文件是目前 rewrite branch 的集中式開發計畫。目標只有一個：

**legacy NiceGUI + 既有 CLI 能做到的事，重構後都能做到。**

本文件不取代 `docs/reference/` 裡的 source-of-truth，而是把目前分散的 architecture / guardrails / parity / contract 文件收斂成一份可執行的 master plan，讓 Contributor Agent 與 Integration Agent 都能先看這份再開工。

## Source Of Truth

若本文件與其他規格衝突，依下列順序裁決：

1. `docs/reference/data-formats/*`
2. `docs/reference/ui/*`
3. `docs/reference/cli/*`
4. `docs/reference/architecture/*`
5. `docs/reference/guardrails/*`
6. code implementation
7. legacy `src/app/` / 舊 scripts 行為

參考：

- `../docs/reference/guardrails/project-basics/source-of-truth-order.md`
- `../docs/reference/architecture/parity-matrix.md`
- `../docs/reference/architecture/canonical-contract-registry.md`

## Current Target Layout

```text
superconducting-circuits-tutorial/

# ── Application Layer (Rewrite Stack) ──────────────────
├── frontend/                   # Next.js App Router frontend
├── backend/                    # FastAPI backend
├── cli/                        # Typer CLI
├── desktop/                    # Electron shell

# ── Shared Core ───────────────────────────────────────
├── src/
│   ├── core/                   # installable scientific core (sc_core)
│   ├── worker/                 # task worker / runtime
│   └── julia/                  # Julia helper code (plotting, utils)

# ── Data Layer ────────────────────────────────────────
├── data/
│   ├── raw/                    # 原始數據 (HFSS/VNA)
│   ├── processed/              # 分析結果
│   ├── trace_store/            # Zarr numeric traces
│   └── database.db             # SQLite metadata DB

# ── Documentation ─────────────────────────────────────
├── docs/
│   ├── reference/              # architecture, guardrails, data-formats (SoT)
│   ├── overrides/              # Zensical theme overrides
│   └── site/                   # build output (gitignored)

# ── Legacy (migration-only) ───────────────────────────
├── src/app/                    # NiceGUI code, migration reference only

# ── Supporting Infrastructure ─────────────────────────
├── Plans/                      # migration planning and execution notes
├── scripts/                    # repo helpers (docs build, rewrite orchestration)
├── tests/                      # repo-level tests
├── examples/                   # executable tutorial examples
└── sandbox/                    # scratch / non-product experiments
```

根目錄允許存在的設定檔：

| File | Reason |
|---|---|
| `README.md` | repo 入口 |
| `pyproject.toml` + `uv.lock` | Python project root |
| `package.json` | npm workspace root scripts |
| `.gitignore` | repo config |
| `.pre-commit-config.yaml` | repo config |
| `.env.example` | repo config |
| `Project.toml` + `Manifest.toml` | Julia project root (慣例) |
| `juliapkg.json` | juliacall dependency config |
| `zensical.toml` | Docs site config |

**任何不在上述列表或 Target Layout 中的根目錄檔案/目錄，都應在 Phase 1.5 處理。**

參考：

- `../docs/reference/guardrails/project-basics/folder-structure.md`
- `../docs/reference/guardrails/project-basics/project-overview.md`

## Workstream Boundaries

### Frontend

責任：

- app shell
- app-state
- authentication-aware UI
- active dataset context
- task/recovery-aware workspace UI
- CodeMirror-based circuit definition editing
- schemdraw / simulation / characterization user workflows

不得承擔：

- canonical computation state
- persistence details
- worker/runtime orchestration

主要位置：

- `frontend/src/app/`
- `frontend/src/components/`
- `frontend/src/features/`
- `frontend/src/lib/`

### Backend

責任：

- API contracts
- session / identity / workspace context
- metadata CRUD
- TraceStore-facing contracts
- task submission / status / result access
- service orchestration

不得承擔：

- UI state
- Electron-specific behavior
- duplicated scientific rules that belong in `sc_core`

主要位置：

- `backend/src/app/api/`
- `backend/src/app/services/`
- `backend/src/app/domain/`
- `backend/src/app/infrastructure/`

### Core

責任：

- canonical invariants
- circuit definition validation / normalization
- task routing / execution contracts
- storage / provenance contracts
- scientific compute orchestration
- JuliaCall / Python-side shared analysis rules

不得承擔：

- FastAPI / Next.js / Typer / Electron transport concerns

主要位置：

- `src/core/sc_core/`
- `src/core/shared/`
- `src/julia/`

### CLI

責任：

- thin operational adapter
- reusable researcher workflows
- automation-friendly entrypoints
- machine-consumable output where needed

不得承擔：

- duplicated backend/service/core business logic
- repo-layout hacks
- direct dependence on frontend

主要位置：

- `cli/src/sc_cli/`
- `cli/tests/`

### Docs / Site Infrastructure

責任：

- zh-TW source-of-truth docs content
- Zensical config and build pipeline
- theme overrides and custom JS/CSS
- nav route integrity
- guardrails as source-of-truth

不得承擔：

- app-level UI or API logic

主要位置：

- `docs/`
- `scripts/` (docs helper scripts)

## Cross-Cutting Contracts

這些是所有 phase 都要遵守的硬契約：

- Identity / Workspace model
- Task semantics
- Error model
- Contract versioning
- Parity matrix
- Canonical contract registry

參考：

- `../docs/reference/architecture/identity-workspace-model.md`
- `../docs/reference/architecture/task-semantics.md`
- `../docs/reference/guardrails/code-quality/error-handling.md`
- `../docs/reference/guardrails/code-quality/contract-versioning.md`
- `../docs/reference/architecture/parity-matrix.md`
- `../docs/reference/architecture/canonical-contract-registry.md`
- `../docs/reference/guardrails/execution-verification/phase-gates.md`

## Risk & Rollback Strategy

- 每個 phase 開始前在 `Plans/` 建立 phase-specific notes（可選）
- 所有 structural change 使用 `git mv` 確保 rename tracking
- Legacy NiceGUI (`src/app/`) 在 Phase 7 sign-off 前 **不得刪除**，作為 fallback reference
- 雙軌期間：新功能 **只做在 rewrite stack**，legacy 只做 bugfix / migration-support patch
- 若某 phase 做到一半需 rollback，以 git branch/tag 為回退點，不做 manual undo

## Sub-Plans

下列獨立計畫文件提供特定領域的實作細節：

| Plan | 說明 | 對應 Phase |
|---|---|---|
| [Logging & Observability](logging-observability-plan.md) | structured logging、correlation ID、log points | Phase 5A–7 |
| [Frontend-Backend Contract Sync](frontend-backend-contract-sync-plan.md) | OpenAPI-first type sync + CI gate | Phase 3–7 |
| [Secret Management](secret-management-plan.md) | secret lifecycle、rotation、desktop/local storage baseline | Phase 4–7 |
| [TraceStore Schema Evolution](tracestore-schema-evolution-plan.md) | Zarr/TraceStore version markers、read compatibility、rebuild policy | Phase 5A–7 |

## Phases

### Phase 0: Planning Baseline `done`

目的：

- 定義 project goal
- 固定 stack / folder structure
- 固定 source-of-truth order
- 固定 contributor roles

Checklist：

- [x] guardrails 已建立
- [x] architecture docs 已建立
- [x] parity matrix 已存在
- [x] canonical contract registry 已存在
- [x] source-of-truth order 已定義

### Phase 1: Workspace Foundations `done`

目的：

- 建立 `frontend/`, `backend/`, `cli/`, `desktop/`
- 建立 `sc_core` package boundary
- 建立 root-level orchestration

Checklist：

- [x] `frontend/` 可安裝、可 build
- [x] `backend/` 可安裝、可 run
- [x] `cli/` 可安裝、`sc --help` 可用
- [x] `desktop/` Electron shell scaffold 已建立
- [x] `sc_core` package boundary 已建立
- [x] root `package.json` orchestration scripts 已建立

### Phase 1.5: Root Cleanup `done`

目的：

- 把根目錄整理成符合 Target Layout 的乾淨狀態
- 移除散落的 stray files、清理 generated artifacts、更新 `.gitignore`

Checklist：

- [x] 根目錄 stray files 已整理（`test_sim.py` → `sandbox/`、`utils.jl` → `src/julia/`）
- [x] 過時檔案已移除（`requirements-docs.txt`、暫存 screenshot）
- [x] 空殼目錄與 generated artifacts 已清理（`src/sc_app/`、`*.egg-info/` 等）
- [x] Julia 程式碼已集中到 `src/julia/`
- [x] `docs/overrides/` 已就位，`zensical.toml` 已更新
- [x] `.gitignore` 已覆蓋 `tmp/`、`output/` 與 generated clutter
- [x] `README.md` 專案結構 section 已更新
- [x] `git status` 可維持乾淨

完成標準：

- 根目錄只含 Target Layout 中列出的目錄 + 允許的設定檔
- `uv sync --dry-run` 無錯
- docs build 無錯

### Phase 2: Contract Scaffolds `done`

目的：

- 建立 datasets / circuit-definitions / session / tasks 的最小 contract
- 建立 frontend app-state foundation
- 建立 CLI scaffold

Checklist：

- [x] frontend shell state 有 provider foundation
- [x] backend 有基礎 API contract
- [x] CLI 有最小 package scaffold

### Phase 3: Metadata / Schema Parity `in_progress`

目的：

- 把 metadata / schema workflow 接上真 contract

範圍：

- Data Browser
- Circuit Definition Editor
- Schemdraw read path
- definition inspect CLI

Checklist：

- [x] Data Browser 接真 API
- [x] Circuit Definition Editor 接真 API
- [x] Schemdraw read-first integration
- [x] minimal CLI inspect/browse baseline
- [ ] dataset list/detail/update 完整 parity
- [ ] circuit definition full CRUD parity
- [ ] schemdraw render 可依 canonical definition 完整渲染
- [ ] backend API contract tests 覆蓋 dataset + definition endpoints
- [ ] frontend build/type/lint 通過
- [ ] OpenAPI export script baseline（見 [Contract Sync Plan](frontend-backend-contract-sync-plan.md)）
- [ ] parity matrix 對應 entries 更新為 `done`

### Phase 4: Identity + Workspace Context Foundation `in_progress`

目的：

- 統一 current user / session / workspace / active dataset / task visibility semantics

範圍：

- backend session model
- frontend app session / shell state
- task visibility semantics
- active dataset persistence / restore semantics

Checklist：

- [x] backend session/task foundation
- [x] frontend shell 已接 backend-backed session/tasks
- [x] recovery-oriented app-state hardening 已整合
- [x] task visibility semantics 已進入 backend contract
- [x] active dataset 已成為 backend-aware session state
- [ ] frontend refresh 後可從 backend session 重建 identity/workspace context
- [ ] auth/session contract tests
- [ ] workspace-context tests
- [ ] frontend app-state integration tests
- [ ] secret management baseline（startup 拒絕 default secrets、`.env` gitignore 驗證）
- [ ] secret rotation / renewal owner 已定義（見 [Secret Management Plan](secret-management-plan.md)）
- [ ] bootstrap admin credential retirement path 已定義
- [ ] desktop/local secret storage baseline 已定義

### Phase 4.5: Minimal Operational CLI `in_progress`

目的：

- 讓 CLI 成為最早可用的 integration harness

範圍：

- `sc session show`
- `sc datasets list`
- `sc tasks list`
- `sc tasks show`
- `sc circuit-definition inspect`

Checklist：

- [x] minimal commands scaffold
- [x] structured error path 已補齊
- [x] 所有 listed commands 可實跑並有正確 output
- [x] CLI command tests（session/dataset/definition/task basics）
- [x] 不使用 repo-layout hacks
- [ ] machine-readable output (JSON) 支援

### Phase 5A: Storage Foundation `in_progress`

目的：

- 穩定 metadata / trace / result / provenance contracts
- 建立 DB schema migration 工具鏈

範圍：

- SQLite-style metadata contracts
- TraceStore / Zarr-style payload locator contracts
- result handle / provenance refs
- storage-facing backend API semantics
- DB schema migration (Alembic)

Checklist：

- [x] `sc_core.storage` module 已建立
- [x] backend storage-facing contracts
- [x] storage presenter / factory
- [x] shared result/storage adoption 開始進入 backend/worker
- [x] metadata 與 payload 責任已在 contract 層明確分離
- [x] trace/result/provenance linkage 已有穩定 contract baseline
- [x] TraceStore/provenance linkage tests 已開始建立
- [ ] backend 與 `sc_core` 對 storage semantics 不再各自漂移
- [ ] repository/persistence tests
- [ ] 真實 SQLite / TraceStore persistence tests
- [ ] Alembic 設定完成（`alembic init`、baseline migration）
- [ ] 現有 `data/database.db` schema 有 baseline migration script
- [ ] CI 可驗證 migration 正確性
- [ ] TraceStore version marker / schema metadata 已定義（見 [TraceStore Schema Evolution](tracestore-schema-evolution-plan.md)）
- [ ] TraceStore read-compat fallback 或 rebuild strategy 已定義
- [ ] TraceStore schema migration / rebuild 驗證流程已建立

### Phase 5B: Execution Foundation `planned`

目的：

- 建立真實 task lifecycle 與 worker execution path
- 建立 logging/observability baseline

範圍：

- task submit / running / completed / failed / cancelled
- logs / retry / cancellation semantics
- RQ worker integration (Redis-backed)
- result attach / recovery attach
- structured logging + correlation ID propagation

Checklist：

- [ ] `POST /tasks` 不再只是 scaffold record
- [ ] RQ worker 可接收並執行 task（Redis 已在 `.env.example` 配置）
- [ ] task lifecycle 可追蹤（submit → running → completed/failed）
- [ ] result attach / recovery attach 可運作
- [ ] worker / backend / frontend / CLI 對 task lifecycle 語意一致
- [ ] Redis dependency health check（worker startup 驗證 Redis 連線）
- [ ] stale task cleanup 機制（`SC_WORKER_STALE_TIMEOUT_SECONDS` 已配置）
- [ ] task lifecycle tests
- [ ] worker/execution tests
- [ ] retry/failure classification tests
- [ ] logging baseline 完成（見 [Logging Plan](logging-observability-plan.md)）
- [ ] correlation ID middleware（backend + worker + CLI）

### Phase 6: Workflow Parity + Recovery Parity `planned`

目的：

- 將主要研究工作流搬完，並確保 recovery parity

範圍：

- CodeMirror netlist editing
- schemdraw write/render flow
- simulation submit/status/log/result
- characterization workflow
- recovery / re-attach / refresh rebuild

Checklist：

- [ ] CodeMirror editor 可編輯 netlist
- [ ] schemdraw write/render flow 完整
- [ ] simulation 完整 workflow（submit → status → logs → result）
- [ ] characterization 完整 workflow
- [ ] page refresh 後可重建 active dataset / task / result views
- [ ] workflow 不依賴 in-memory UI state 才能恢復
- [ ] `examples/` tutorial smoke tests 通過
- [ ] frontend-backend contract sync CI gate（見 [Contract Sync Plan](frontend-backend-contract-sync-plan.md)）
- [ ] workflow integration tests
- [ ] recovery/reattach tests
- [ ] parity matrix workflow entries sign-off

### Phase 7: Full CLI + Desktop + CI + Sign-off `planned`

目的：

- 完整 CLI parity
- Electron desktop parity
- CI/CD pipeline completion
- final migration sign-off

範圍：

- full CLI commands
- desktop shell integration
- CI pipeline for all workstreams
- `examples/` tutorial content finalization
- parity matrix final sign-off
- legacy retirement decision

Checklist：

- [ ] 所有 reference CLI commands 對等
- [ ] 所有 reference UI pages 對等
- [ ] desktop local runtime 可用
- [ ] Electron 安全 baseline（`contextIsolation: true`、CSP 設定、IPC channel allowlist）
- [ ] CI pipeline 覆蓋所有 workstreams：
  - [ ] frontend build/lint/test CI
  - [ ] backend test CI
  - [ ] CLI test CI
  - [ ] contract sync CI（見 [Contract Sync Plan](frontend-backend-contract-sync-plan.md)）
  - [ ] desktop build CI (if applicable)
  - [ ] docs build + route integrity CI (已有基礎)
- [ ] `examples/` 教學範例可正常執行
- [ ] logging production readiness（見 [Logging Plan](logging-observability-plan.md)）
- [ ] dependency management policy 已記錄：
  - [ ] Python (`uv`) / npm / Julia 定期更新 cadence
  - [ ] `npm audit` + Python vulnerability scanning 已納入 CI
- [ ] post-migration API versioning 策略已記錄
- [ ] parity matrix 所有 entries 為 `done`，recovery parity 為 `yes`
- [ ] legacy NiceGUI 退役決策已做出並記錄
- [ ] `src/app/` legacy code 退役或封存

## Current Checkpoint

截至 2026-03-12，目前 branch 大致位於：

- `Phase 0–2`：`done`
- `Phase 1.5`：`done`
- `Phase 3`：後段，大部分 baseline 已接通
- `Phase 4`：進行中
- `Phase 4.5`：進行中
- `Phase 5A`：已開始建立 shared contracts
- `Phase 5B–7`：`planned`

可以理解為：

> shell / session / task / metadata / schema / storage contracts 已經在成形，且根目錄與 docs layout 已整理完成；但 simulation execution、full characterization workflow、full CLI parity、desktop parity、與完整 CI pipeline 仍未完成。

## Phase Gates

每個 phase 不只看功能，也看最低驗收：

| Phase | 最低必過項目 |
|---|---|
| Phase 1.5 | 根目錄符合 target layout、`uv sync` + docs build 無錯 |
| Phase 3 | backend API contract tests、frontend build/type/test、OpenAPI export baseline、parity entries 更新 |
| Phase 4 | auth/session contract tests、workspace-context tests、frontend app-state integration tests、secret management baseline |
| Phase 4.5 | CLI command tests for session/dataset/definition/task basics |
| Phase 5A | repository/persistence tests、TraceStore contract tests、provenance linkage tests、Alembic baseline migration |
| Phase 5B | task lifecycle tests、worker/execution tests、retry/failure tests、Redis health check、logging baseline |
| Phase 6 | workflow integration tests、recovery/reattach tests、examples smoke tests、contract sync CI、parity matrix workflow sign-off |
| Phase 7 | full CLI parity checks、desktop smoke tests (含安全 baseline)、CI pipeline green、dependency policy、migration sign-off |

參考：

- `../docs/reference/guardrails/execution-verification/phase-gates.md`

## Contributor Workflow

所有 Contributors 開工前都應先看：

1. 這份 master plan
2. parity matrix
3. canonical contract registry
4. identity/workspace model
5. task semantics
6. 對應領域 guardrails

Integration Agent 負責：

- 收回 Contributor reports
- 做 merge / conflict resolution
- 跑 cross-workspace verification
- 拒收破壞 clean boundaries 的 handoff

## Plan Governance

這份 master plan 同時是 execution tracker，因此需要固定治理規則，避免再次過時。

### Ownership

- `Integration Agent` 是 phase status 與 checklist 狀態的預設維護者
- `Contributor Agent` 可以提出狀態變更建議，但不直接宣告 phase 完成
- 若狀態變更涉及 source-of-truth contract，必須同步更新相關 architecture/guardrails 文件

### Evidence Required For Status Changes

任何 checklist 從 pending 改為 done，至少要有下列其一，且最好在同一交付線完成：

- 實際 merge commit
- contributor report
- 對應測試綠燈
- 已更新的 parity matrix / contract registry

### Review Cadence

- 每完成一批 contributor integrations，應重新檢查本文件的 phase/checklist 狀態
- 至少在每次 phase gate 接近完成前，做一次完整 review
- 若發現 master plan 與 repo 實況漂移，優先修 plan，再繼續派工

### Commit Hygiene

- 若 commit 主要目的是更新 phase/checklist 狀態，commit message 應明確包含 `plan`, `phase`, 或等價標記
- sub-plans 一旦被 master plan 引用，就必須納入 git 追蹤，不能只存在 local working tree

## Success Definition

整個 migration 只有在下面全部成立時才算完成：

- UI 對等於 reference UI
- CLI 對等於 reference CLI
- backend 可獨立提供 auth / CRUD / trace / task / execution contract
- `sc_core` 擁有 canonical invariants 與 shared compute contracts
- worker (RQ + Redis) / execution / result / provenance 可追蹤
- recovery parity 成立
- desktop 只是 shell，不改變核心責任邊界，安全 baseline 已通過
- CI pipeline 覆蓋所有 workstreams 的 build/lint/test + contract sync
- structured logging + correlation ID 跨層可追蹤
- DB schema migration (Alembic) 工具鏈就位
- dependency management policy 已記錄並納入 CI
- 根目錄結構符合 target layout
- legacy NiceGUI 不再是必要依賴
