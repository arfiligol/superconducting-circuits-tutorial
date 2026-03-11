---
aliases:
  - Routing
  - 路由策略
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Next.js App Router 的 route groups、dynamic routes 與 layout 邊界。
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Routing

## Rules

- 使用 App Router route groups 組織 workspace
- dynamic route 優先使用 `[id]` 或 `[resourceId]`
- 不要硬編碼 URL string 到處散落
- layout boundary 要和產品資訊架構對齊
- 避免超過 4 層以上的 route nesting

## Agent Rule { #agent-rule }

```markdown
## Routing
- Use Next.js App Router route groups for workspace organization.
- Use `[id]` or `[resourceId]` naming for dynamic routes.
- Keep layout boundaries aligned with product information architecture.
- Avoid hardcoded URLs scattered through components.
- Avoid route nesting deeper than necessary; if it exceeds four levels, reconsider the information structure.
```
