---
aliases:
  - Accessibility
  - A11y Rules
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: Frontend accessibility, semantic HTML, keyboard flow, and ARIA rules.
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Accessibility

## Core Rules

- use semantic HTML
- interactive elements must be keyboard accessible
- icon-only buttons need `aria-label`
- form fields need labels and error messages
- text and background contrast must meet WCAG AA

## Agent Rule { #agent-rule }

```markdown
## Accessibility
- Use semantic HTML.
- Interactive elements must be keyboard accessible.
- Icon-only buttons require `aria-label`.
- Form fields require labels and visible error messages.
- Maintain WCAG AA contrast for text and critical UI states.
- Do not use clickable `div` elements when a button or link is the correct semantic choice.
```
