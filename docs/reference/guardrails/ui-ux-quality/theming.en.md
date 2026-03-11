---
aliases:
  - Theming
  - Theme Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Theme-system, semantic-token, and dark-mode rules for the frontend.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Theming

The theme system must serve the Next.js frontend rather than scattering color decisions across components.

## Theme Management

- use `next-themes`
- provide the `ThemeProvider` from the root layout
- support `light`, `dark`, and `system`

## Semantic Tokens

Prefer semantic tokens such as:

- `background`
- `foreground`
- `card`
- `muted`
- `border`
- `primary`
- `destructive`

Do not treat `bg-white`, `text-black`, or raw hex colors as product semantics.

## Rules

- Tailwind is fine for layout and semantic classes, but not for scattering hardcoded color decisions
- every new component must be readable in both light and dark themes
- charts must follow the active theme
- theme switching must not reset form state or selections

## Agent Rule { #agent-rule }

```markdown
## Theming
- Use `next-themes` for theme management.
- Provide `light`, `dark`, and `system` modes.
- Prefer semantic tokens such as `background`, `foreground`, `card`, `muted`, `border`, and `primary`.
- Do not hardcode product colors with raw utility choices like `bg-white`, `text-black`, or literal hex values unless there is a documented exception.
- Every component must remain readable in both light and dark themes.
- Chart styling must follow the active theme.
- Theme switching must not trigger avoidable state loss.
```
