---
aliases:
  - Routing
  - Route Strategy
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Route groups, dynamic routes, and layout boundaries for Next.js App Router.
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Routing

## Rules

- use App Router route groups to organize the workspace
- prefer `[id]` or `[resourceId]` for dynamic routes
- do not scatter hardcoded URL strings across the codebase
- align layout boundaries with product information architecture
- avoid route nesting deeper than four levels unless there is a strong reason

## Agent Rule { #agent-rule }

```markdown
## Routing
- Use Next.js App Router route groups for workspace organization.
- Use `[id]` or `[resourceId]` naming for dynamic routes.
- Keep layout boundaries aligned with product information architecture.
- Avoid hardcoded URLs scattered through components.
- Avoid route nesting deeper than necessary; if it exceeds four levels, reconsider the information structure.
```
