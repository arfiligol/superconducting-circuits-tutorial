---
aliases:
  - UI/UX Quality
  - Frontend UX Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: UI/UX quality rules for the Next.js frontend and Electron desktop shell.
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# UI/UX Quality

This section describes the frontend UI/UX rules for the rewrite branch.
The goal is to keep data-dense surfaces like the Data Browser, Editor, Simulation, and Characterization views consistent and maintainable.
If the app is packaged with Electron, the same frontend UI/UX rules still apply; do not invent a separate desktop-only visual language.

## Frontend Stack

| Layer | Tool | Notes |
| --- | --- | --- |
| Framework | Next.js App Router | route groups, nested layouts, server/client composition |
| Components | Radix UI + shadcn/ui | composable primitives with accessibility foundations |
| Theme | next-themes | light / dark / system |
| Styling | Tailwind CSS v4 + semantic tokens | layout and semantic styling |
| Server State | SWR | cache, revalidation, loading states |
| Form State | React Hook Form + Zod | validation and submission |

## Sub-rules

- [Theming](./theming.en.md)
- [Component Guidelines](./component-guidelines.en.md)
- [Layout Patterns](./layout-patterns.en.md)
- [State Management](./state-management.en.md)
- [Accessibility](./accessibility.en.md)
- [Routing](./routing.en.md)

## Agent Rule { #agent-rule }

```markdown
## UI/UX Quality
- Use Next.js App Router for the frontend.
- Electron desktop packaging must preserve the same frontend UI/UX rules instead of inventing a separate desktop-only UI system.
- Use Radix UI + shadcn/ui for interactive components.
- Use next-themes for theme switching.
- Use semantic design tokens; avoid hardcoded colors.
- Use SWR for server state and React Hook Form + Zod for forms.
- Every UI surface must work in both light and dark themes.
- Load sub-rules as needed: Theming / Component Guidelines / Layout Patterns / State Management / Accessibility / Routing.
```
