---
aliases:
  - Layout Patterns
  - App Layout Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: App Router layout, workspace shell, and data-dense page-structure rules.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Layout Patterns

## App Router Responsibilities

- root layout: providers, theme, fonts, global styles
- workspace layout: sidebar, top bar, shared workspace context
- feature layout: tabs, breadcrumbs, sub-navigation

## Route Groups

- `(workspace)`: main product area
- `(docs)` or other non-product areas can be grouped separately
- do not dump every page under one flat root layout

## Data-Dense View Pattern

Data-heavy pages should prefer a master-detail structure:

- left side: table / list / search / filters
- right side: detail panel / chart / analysis output
- mobile layouts must stack safely

## Spacing

- use a consistent spacing scale
- keep page sections moderately spaced
- keep cards compact but readable
- do not sacrifice data density just to look roomy

## Agent Rule { #agent-rule }

```markdown
## Layout Patterns
- Use App Router layouts intentionally:
    - root layout for providers/theme/fonts
    - workspace layout for shared shell
    - feature layout for sub-navigation
- Use route groups to separate workspace surfaces from other sections.
- Data-dense pages should prefer a master-detail structure with mobile-safe stacking.
- Keep spacing consistent and compact enough for dense data workflows.
- Do not collapse the entire product into one flat page tree without layout boundaries.
```
