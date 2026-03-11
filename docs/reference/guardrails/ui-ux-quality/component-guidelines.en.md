---
aliases:
  - Component Guidelines
  - Component Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Component choices, forms, dialogs, and data-table rules for the frontend.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Component Guidelines

The goal of component rules is to keep the frontend consistent under data-dense and interaction-heavy workflows.

## Component Sources

| Type | Source |
| --- | --- |
| base UI primitives | `@/components/ui/*` (shadcn/ui) |
| feature-specific UI | `frontend/src/features/<feature>/components/*` |
| app-wide layout | `frontend/src/components/layout/*` |

## Rules

- prefer `@/components/ui` wrappers for Button, Input, Select, Dialog, Tabs, Table, and related primitives
- do not use `alert()`, `confirm()`, or `prompt()`
- forms must include labels, validation, and visible error states
- destructive actions require an explicit confirmation flow
- data-dense tables need sorting, filtering, pagination, or a clear virtualization strategy

## Data Browser Contract

- load summary rows first
- fetch full payload only for row selection or detail panels
- do not reload heavy payloads just because the user changed pages

## Agent Rule { #agent-rule }

```markdown
## Component Guidelines
- Prefer components from `@/components/ui/` for interactive primitives.
- Put feature-specific UI in `frontend/src/features/<feature>/components/`.
- Do not use `alert()`, `confirm()`, or `prompt()` for product interactions.
- Destructive actions require an explicit confirmation flow.
- Forms need labels, validation, and visible error states.
- Data-dense tables must support sorting, filtering, and pagination or a clear virtualization strategy.
- Load summary rows first; fetch heavy detail payload only on explicit detail interaction.
```
