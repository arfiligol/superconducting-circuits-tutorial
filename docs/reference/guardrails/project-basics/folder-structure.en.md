---
aliases:
  - Folder Structure
  - Repository Layout
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/project-basics
status: stable
owner: docs-team
audience: contributor
scope: Defines placement boundaries for frontend, backend, CLI, desktop shell, and shared core code in the rewrite branch.
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Folder Structure

The target structure of this branch supports a separated frontend/backend stack while preserving the existing scientific core and documentation system.
The old NiceGUI app remains as migration legacy only.

## Target Layout

```text
superconducting-circuits-tutorial/
├── frontend/                  # Next.js App Router frontend
│   ├── src/app/               # routes, layouts, pages
│   ├── src/components/        # shared UI components
│   ├── src/features/          # feature-local UI modules
│   ├── src/lib/               # API clients, schemas, utilities
│   └── tests/                 # Vitest / Playwright
├── desktop/                   # Electron shell
│   ├── src/main/              # Electron main process
│   ├── src/preload/           # secure preload bridge
│   └── resources/             # desktop packaging assets
├── backend/                   # FastAPI service
│   ├── src/app/api/           # routers, request/response mapping
│   ├── src/app/services/      # use cases / orchestration
│   ├── src/app/domain/        # domain models and rules
│   ├── src/app/infrastructure/# DB and external integrations
│   └── tests/                 # pytest unit / integration tests
├── cli/                       # Typer commands
│   ├── src/cli/commands/
│   └── tests/
├── src/core/                  # shared scientific kernels during migration
│   ├── simulation/
│   ├── analysis/
│   └── shared/
├── docs/                      # bilingual docs and guardrails
├── data/                      # raw / processed / trace-store / local DB
├── scripts/                   # repo helpers only
└── src/app/                   # legacy NiceGUI code during migration only
```

## Placement Rules

| If you are changing | Put it in |
| --- | --- |
| Next.js page, layout, or component | `frontend/` |
| Electron main / preload / packaging work | `desktop/` |
| API router, service, or persistence logic | `backend/` |
| CLI command or batch workflow | `cli/` |
| Shared scientific logic reusable by API / CLI / simulation | `src/core/` |
| Repo automation, docs helper, or migration helper | `scripts/` |
| Old NiceGUI patches | `src/app/`, clearly marked as migration-only |

## Dependency Direction

1. frontend depends on API contracts, not backend internals
2. desktop depends on frontend outputs and controlled IPC, not business logic ownership
3. backend API depends inward on services/domain
4. CLI reuses shared services/core rather than duplicating business logic
5. `src/core/` must remain framework-agnostic from Next.js, FastAPI, Electron, and CLI frameworks

## Agent Rule { #agent-rule }

```markdown
## Folder Structure
- **Frontend** work goes to `frontend/`.
- **Desktop shell** work goes to `desktop/`.
- **Backend** work goes to `backend/`.
- **CLI** work goes to `cli/`.
- **Shared scientific logic** goes to `src/core/`.
- **Docs and guardrails** go to `docs/`.
- Existing `src/app/` NiceGUI code is legacy and should only receive migration-support fixes.
- Dependency direction:
    - frontend depends on API contracts, not backend internals
    - desktop depends on frontend outputs and secure IPC, not business logic ownership
    - backend API layer depends inward on services/domain
    - CLI reuses shared services/core instead of duplicating workflow logic
    - `src/core/` must stay framework-agnostic
```
