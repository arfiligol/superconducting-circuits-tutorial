---
aliases:
  - Design Patterns
  - 設計模式
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: rewrite branch 的服務邊界、依賴方向與共享邏輯規範。
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Design Patterns

本專案的設計模式重點是把共享規則放在穩定的位置，而不是讓每個入口層各自長出一份邏輯。

## Core Rules

### Dependency Direction

- React component 不能承擔業務流程編排
- FastAPI router 不能直接承擔完整 workflow
- CLI command 不能複製 backend service 邏輯
- 共享規則應集中在 backend service 或 `src/core/`

### Dependency Injection

- service 依賴以建構子或明確 factory 注入
- 禁止在函式內隨手 new repository / client / adapter
- framework-specific 組裝放在 composition root

### Canonical Definition

- circuit definition 應有單一 canonical representation
- schemdraw、simulation、analysis、API response 不應各自維護互相漂移的定義格式

### API Layer Responsibility

- request parsing
- auth / permission checks
- service call
- response mapping

不應包含：

- 長流程業務判斷
- persistence 細節
- 跨多模組重複的轉換邏輯

## Agent Rule { #agent-rule }

```markdown
## Design Patterns
- Keep shared workflow logic in backend services or `src/core/`, not in React components, FastAPI routers, or CLI commands.
- Use dependency injection or explicit factories for services, repositories, and adapters.
- Keep one canonical circuit definition that feeds schemdraw, simulation, analysis, API, and CLI.
- API handlers should do I/O, auth, validation, service invocation, and response mapping only.
- CLI commands should orchestrate user input/output, then delegate to shared services/core.
```
