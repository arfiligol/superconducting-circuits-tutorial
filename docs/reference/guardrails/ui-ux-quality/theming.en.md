---
aliases:
  - "Guardrails: Theming"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: Theming

This document defines the Design Token system, dark mode conventions, and Plotly theme synchronization rules.

## Design Token System

All colors must be defined through CSS Variables (Design Tokens) in `src/app/styles/theme.css`.

### Token Reference

| Token | Light Value | Dark Value | Purpose |
|---|---|---|---|
| `--bg` | slate-50 | slate-900 | Page background |
| `--surface` | white | slate-800 | Cards, panels |
| `--elevated` | slate-100 | slate-700 | Hover states, nested surfaces |
| `--fg` | slate-900 | slate-200 | Primary text |
| `--muted` | slate-500 | slate-400 | Secondary text |
| `--border` | slate-200 | slate-700 | Dividers |
| `--primary` | blue-500 | blue-400 | Buttons, active states |
| `--primary-fg` | white | slate-900 | Text on primary surfaces |
| `--danger` | red-600 | red-400 | Error states |
| `--warning` | amber-500 | amber-400 | Warning states |
| `--success` | emerald-500 | emerald-400 | Success states |

### Usage

```css
/* ✅ Correct: use tokens */
background-color: rgb(var(--surface));
color: rgb(var(--fg));
border: 1px solid rgb(var(--border));

/* ❌ Forbidden: hardcoded colors */
background-color: white;
color: #0f172a;
background-color: rgb(30, 41, 59);
```

### Semantic Utility Classes

`theme.css` provides semantic utility classes:

| Class | Maps to Token | Purpose |
|---|---|---|
| `.bg-bg` | `--bg` | Page background |
| `.bg-surface` | `--surface` | Card background |
| `.bg-elevated` | `--elevated` | Hover / nested elements |
| `.text-fg` | `--fg` | Primary text |
| `.text-muted` | `--muted` | Secondary text |
| `.border-border` | `--border` | Border color |

## Tailwind CSS Rules

Tailwind is **layout only** — never use it for colors.

```python
# ✅ Correct: Tailwind = layout
ui.column().classes("w-full flex flex-col gap-4 p-4")

# ✅ Correct: Token class = color
ui.column().classes("bg-surface text-fg border-border")

# ❌ Forbidden: Tailwind colors
ui.column().classes("bg-white text-black bg-blue-500")
```

## Dark Mode

- **Default**: Dark mode is ON (`ui.run(dark=True)`)
- **Toggle**: `ui.dark_mode().toggle()` flips `.dark` on the root element
- **Automatic**: CSS variables switch automatically with `.dark` class — no JavaScript needed

!!! warning "Every component must support dark mode"
    New CSS classes or components must define both `:root` and `.dark` values.

## Plotly Theme Synchronization

Plotly chart backgrounds and fonts must sync with the app theme.

```python
from core.shared.visualization import get_plotly_layout

# ✅ Correct: use theme sync function
fig = build_line_chart(record, dark=ui.dark_mode().value)

# ❌ Forbidden: hardcoded Plotly layout colors
fig.update_layout(paper_bgcolor="white", font_color="black")
```

`get_plotly_layout(dark=True)` returns:

- `template`: `plotly_dark` / `plotly_white`
- `paper_bgcolor`: maps to `--surface`
- `plot_bgcolor`: maps to `--bg`
- `font.color`: maps to `--fg`
- `font.family`: `Inter, Arial, sans-serif`

---

## Agent Rule { #agent-rule }

```markdown
## Theming
- Use CSS variable tokens: `--bg`, `--surface`, `--elevated`, `--fg`, `--muted`, `--border`, `--primary`.
- Forbidden: hardcoded colors (`bg-white`, `text-black`, `#hex`, `rgb(literal)`).
- Tailwind is layout-only (flex, p-4, gap-2). Colors = CSS variables.
- Dark mode: default ON. Toggle flips `.dark` on root, CSS variables auto-switch.
- Plotly theme sync: always pass `dark=ui.dark_mode().value` to figure builders.
- New CSS classes must define both `:root` and `.dark` values.
```
