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
version: v1.1.0
last_updated: 2026-03-14
updated_by: docs-team
---

# Design Patterns

本專案的設計模式重點是把共享規則放在穩定的位置，而不是讓每個入口層各自長出一份邏輯。

!!! info "Use this page for boundary and ownership decisions"
    這頁回答 workflow logic、dependency injection、canonical definition 與 API layer responsibility 應該放在哪裡。它不取代 folder structure 或 backend architecture，而是補 owner pattern。

## Pattern Map

| pattern | 回答的問題 |
| --- | --- |
| Dependency Direction | 哪一層可以擁有 workflow |
| Dependency Injection | service / repository / adapter 應怎麼被組裝 |
| Canonical Definition | 哪裡才是定義格式的真正 owner |
| API Layer Responsibility | API handler 可以做什麼、不可以做什麼 |

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

!!! warning "Do not let entry layers fork the workflow"
    若 component、router、CLI command 各自偷偷長出一份相似但不完全相同的流程，最後一定會漂移。這頁的重點就是避免這種局部合理、全域失控的設計。

## Agent Rule { #agent-rule }

```markdown
## Design Patterns
- Keep shared workflow logic in backend services or `src/core/`, not in React components, FastAPI routers, or CLI commands.
- Use dependency injection or explicit factories for services, repositories, and adapters.
- Keep one canonical circuit definition that feeds schemdraw, simulation, analysis, API, and CLI.
- API handlers should do I/O, auth, validation, service invocation, and response mapping only.
- CLI commands should orchestrate user input/output, then delegate to shared services/core.
```
