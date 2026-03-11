---
aliases:
  - State Management
  - Frontend State Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Strategy for server, client, form, and URL state in the frontend.
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# State Management

## State Categories

| Type | Tool | Purpose |
| --- | --- | --- |
| Server State | SWR | API reads, cache, revalidation |
| Client UI State | React Context or local state | shell state, selections, transient UI state |
| Form State | React Hook Form + Zod | validation and submission |
| URL State | route params / search params | shareable, replayable page state |

## Rules

- do not scatter `fetch` calls directly across components
- API reads should live in hooks / services
- mutations should handle loading, success, and error explicitly
- if state belongs in the URL, do not hide it in global context

## Agent Rule { #agent-rule }

```markdown
## State Management
- Use SWR for server state.
- Use React Hook Form + Zod for form state.
- Use Context or local state for UI-only state.
- Use route params or search params for shareable page state.
- Do not scatter direct `fetch` calls across components.
- Keep read and mutation logic in hooks or services with explicit loading/error handling.
```
