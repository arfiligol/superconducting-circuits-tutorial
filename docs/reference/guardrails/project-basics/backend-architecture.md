---
aliases:
  - Backend Architecture
  - 後端架構藍圖
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/project-basics
status: stable
owner: docs-team
audience: contributor
scope: 定義 rewrite backend 的責任邊界、模組分層與對 sc_core 的依賴方向。
version: v1.0.0
last_updated: 2026-03-12
updated_by: codex
---

# Backend Architecture

rewrite backend 的目標不是單純 CRUD API，而是可獨立運作的 headless application backend。
即使 frontend 尚未完成，backend 也應能提供穩定的 auth、CRUD、TraceStore、task、result 與 execution contracts。

## Responsibilities

backend 必須承擔：

- auth / session / workspace context
- metadata CRUD
- TraceStore-facing contracts 與 payload locator
- task submission / status / result access
- execution orchestration 與 service composition
- 對 `sc_core` canonical contracts 的 adapter 與 transport mapping

backend 不得承擔：

- UI state
- Electron-specific behavior
- duplicated scientific invariants
- frontend-only display state

## Target Internal Structure

```text
backend/src/app/
├── api/
│   ├── router.py
│   ├── routers/
│   ├── schemas/
│   └── presenters/
├── services/
├── domain/
└── infrastructure/
    ├── runtime.py
    ├── repositories/
    ├── persistence/
    ├── tracestore/
    └── execution/
```

## Layer Boundaries

### API

責任：

- request parsing
- auth / permission gate
- service invocation
- response mapping
- transport-layer error translation

不得承擔：

- business workflow
- persistence details
- duplicated data shaping already owned by presenters / `sc_core`

### Services

責任：

- use case orchestration
- repository coordination
- task submission flow
- service-level validation與 framework-agnostic application errors

不得承擔：

- FastAPI transport exceptions
- direct web concerns
- duplicated canonical rules already owned by `sc_core`

### Domain

責任：

- backend-owned models for auth/session/task/storage adapters
- service-facing rule boundaries that are not yet elevated to `sc_core`

不得承擔：

- HTTP schema concerns
- framework bootstrapping

### Infrastructure

責任：

- persistence adapters
- TraceStore adapters
- execution/runtime adapters
- composition root wiring

不得承擔：

- canonical scientific contracts
- frontend/UI workflow state

## Dependency Direction

1. API 依賴 inward services/domain
2. services 依賴 abstractions、`sc_core` 與 infrastructure 注入物
3. infrastructure 依賴外部系統與 runtime
4. backend 可依賴 `sc_core`
5. `sc_core` 不得依賴 backend

## Integration With sc_core

backend 應把下列 canonical concerns 優先視為 `sc_core` 的 owner：

- circuit definition invariants
- task routing / execution contracts
- storage / provenance canonical handles
- shared scientific compute orchestration

backend 的角色是：

- 暴露 API contract
- 管理 persistence / auth / task / workspace semantics
- 將 backend-owned adapter state 映射到 `sc_core` canonical surfaces

## Agent Rule { #agent-rule }

```markdown
## Backend Architecture
- Treat backend as a headless application backend, not just a thin CRUD API.
- Keep API handlers limited to parsing, auth, service invocation, response mapping, and transport error translation.
- Keep service errors framework-agnostic; FastAPI-specific exceptions belong in the API layer.
- Keep persistence, TraceStore, and execution adapters in infrastructure.
- Reuse `sc_core` for canonical scientific contracts instead of duplicating them in backend adapters.
- Do not let frontend state, Electron concerns, or transport-only display state leak into backend services or domain.
```
