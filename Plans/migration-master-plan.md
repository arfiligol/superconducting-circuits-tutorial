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
├── Plans/                      # migration planning and execution notes
├── frontend/                   # Next.js App Router frontend
├── backend/                    # FastAPI backend
├── cli/                        # Typer CLI
├── desktop/                    # Electron shell
├── src/core/                   # shared scientific core during migration
├── src/app/                    # legacy NiceGUI, migration-only
├── src/worker/                 # worker/runtime
├── src/julia/                  # Julia helper code
├── docs/                       # source-of-truth docs and guardrails
├── scripts/                    # repo helpers
├── data/                       # local data, DB, trace-store
├── tests/                      # repo-level tests
└── sandbox/                    # scratch / non-product experiments
```

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

## Phases

### Phase 0: Planning Baseline

目的：

- 定義 project goal
- 固定 stack / folder structure
- 固定 source-of-truth order
- 固定 contributor roles

完成標準：

- guardrails 已建立
- architecture docs 已建立
- parity matrix / contract registry 已存在

狀態：

- `done`

### Phase 1: Workspace Foundations

目的：

- 建立 `frontend/`, `backend/`, `cli/`, `desktop/`
- 建立 `sc_core` package boundary
- 建立 root-level orchestration

完成標準：

- 各 workspace 可安裝、可 build、可基本驗證

狀態：

- `done`

### Phase 2: Contract Scaffolds

目的：

- 建立 datasets / circuit-definitions / session / tasks 的最小 contract
- 建立 frontend app-state foundation
- 建立 CLI scaffold

完成標準：

- frontend shell state 有 provider foundation
- backend 有基礎 API contract
- CLI 有最小 package scaffold

狀態：

- `done`

### Phase 3: Metadata / Schema Parity

目的：

- 把 metadata / schema workflow 接上真 contract

範圍：

- Data Browser
- Circuit Definition Editor
- Schemdraw read path
- definition inspect CLI

完成標準：

- dataset list/detail/update 可用
- circuit definition list/detail/create/update/delete 可用
- schemdraw 可依 canonical definition 讀取
- CLI 可 inspect definition

狀態：

- `in_progress`

目前已達成：

- Data Browser 真 API
- Circuit Definition Editor 真 API
- Schemdraw read-first integration
- minimal CLI inspect/browse baseline

### Phase 4: Identity + Workspace Context Foundation

目的：

- 統一 current user / session / workspace / active dataset / task visibility semantics

範圍：

- backend session model
- frontend app session / shell state
- task visibility semantics
- active dataset persistence / restore semantics

完成標準：

- frontend refresh 後可從 backend session 重建 identity/workspace context
- task visibility 不只靠 frontend 過濾
- active dataset 是 backend-aware state，不只是 local UI state

狀態：

- `in_progress`

目前已達成：

- backend session/task foundation
- frontend shell 已接 backend-backed session/tasks
- recovery-oriented app-state hardening 已開始

### Phase 4.5: Minimal Operational CLI

目的：

- 讓 CLI 成為最早可用的 integration harness

範圍：

- `sc session show`
- `sc datasets list`
- `sc tasks list`
- `sc tasks show`
- `sc circuit-definition inspect`

完成標準：

- commands 可實跑
- structured error handling 一致
- 不使用 repo-layout hacks

狀態：

- `in_progress`

目前已達成：

- minimal commands 已有
- structured error path 已補齊

### Phase 5A: Storage Foundation

目的：

- 穩定 metadata / trace / result / provenance contracts

範圍：

- SQLite-style metadata contracts
- TraceStore / Zarr-style payload locator contracts
- result handle / provenance refs
- storage-facing backend API semantics

完成標準：

- metadata 與 payload 責任清楚分離
- trace/result/provenance linkage 有穩定 contract
- backend 與 `sc_core` 對 storage semantics 不再各自漂移

狀態：

- `in_progress`

目前已達成：

- `sc_core.storage`
- backend storage-facing contracts
- storage presenter / factory
- shared result/storage adoption 開始進入 backend/worker

### Phase 5B: Execution Foundation

目的：

- 建立真實 task lifecycle 與 worker execution path

範圍：

- task submit / running / completed / failed / cancelled
- logs / retry / cancellation semantics
- worker integration
- result attach / recovery attach

完成標準：

- `POST /tasks` 不再只是 scaffold record
- worker / backend / frontend / CLI 對 task lifecycle 語意一致
- result 可由 persisted refs 重建

狀態：

- `planned`

### Phase 6: Workflow Parity + Recovery Parity

目的：

- 將主要研究工作流搬完，並確保 recovery parity

範圍：

- CodeMirror netlist editing
- schemdraw write/render flow
- simulation submit/status/log/result
- characterization workflow
- recovery / re-attach / refresh rebuild

完成標準：

- page refresh 後可重建 active dataset / task / result views
- workflow 不依賴 in-memory UI state 才能恢復

狀態：

- `planned`

### Phase 7: Full CLI + Desktop + Sign-off

目的：

- 完整 CLI parity
- Electron desktop parity
- final migration sign-off

範圍：

- full CLI commands
- desktop shell integration
- parity matrix final sign-off
- legacy retirement decision

完成標準：

- reference CLI 對等
- reference UI 對等
- desktop local runtime 可用
- legacy 不再是必要依賴

狀態：

- `planned`

## Current Checkpoint

截至 2026-03-12，目前 branch 大致位於：

- `Phase 3` 後段
- `Phase 4` 進行中
- `Phase 4.5` 進行中
- `Phase 5A` 已開始建立 shared contracts

可以理解為：

> shell / session / task / metadata / schema / storage contracts 已經在成形，但 simulation execution、full characterization workflow、full CLI parity、desktop parity 尚未完成。

## Phase Gates

每個 phase 不只看功能，也看最低驗收：

- Phase 4：auth/session/workspace tests、frontend app-state integration tests
- Phase 4.5：CLI command tests
- Phase 5A：repository/persistence tests、TraceStore/provenance linkage tests
- Phase 5B：task lifecycle / worker / retry / failure tests
- Phase 6：workflow integration tests、recovery/reattach tests
- Phase 7：full CLI parity checks、desktop smoke tests

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

## Success Definition

整個 migration 只有在下面全部成立時才算完成：

- UI 對等於 reference UI
- CLI 對等於 reference CLI
- backend 可獨立提供 auth / CRUD / trace / task / execution contract
- `sc_core` 擁有 canonical invariants 與 shared compute contracts
- worker / execution / result / provenance 可追蹤
- recovery parity 成立
- desktop 只是 shell，不改變核心責任邊界
