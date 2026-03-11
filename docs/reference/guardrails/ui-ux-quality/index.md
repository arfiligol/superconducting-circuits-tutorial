---
aliases:
  - UI/UX Quality
  - UI/UX 規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Next.js frontend 與 Electron desktop shell 的 UI/UX 品質規範索引。
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# UI/UX Quality

本區描述 rewrite branch 中 frontend 的 UI/UX 規範。
這些規則的目的，是讓 Data Browser、Editor、Simulation、Characterization 等功能在資料密集情境下仍可維持一致且可維護的介面。
若以 Electron 包裝 desktop app，視覺與互動規則仍以這套 frontend 規範為主，不另起一套桌面 UI 語言。

## Frontend Stack

| 層級 | 工具 | 說明 |
| --- | --- | --- |
| Framework | Next.js App Router | route groups、nested layouts、server/client 組合 |
| Components | Radix UI + shadcn/ui | 可組合且具 a11y 基礎的元件 |
| Theme | next-themes | light / dark / system |
| Styling | Tailwind CSS v4 + semantic tokens | 佈局與語意化樣式 |
| Server State | SWR | cache、revalidation、loading states |
| Form State | React Hook Form + Zod | validation 與提交 |

## Sub-rules

- [Theming](./theming.md)
- [Component Guidelines](./component-guidelines.md)
- [Layout Patterns](./layout-patterns.md)
- [State Management](./state-management.md)
- [Accessibility](./accessibility.md)
- [Routing](./routing.md)

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
