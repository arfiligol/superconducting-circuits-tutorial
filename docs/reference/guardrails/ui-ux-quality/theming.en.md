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
- **Toggle**: `ui.dark_mode().toggle()` flips `.dark` / `body--dark` on the root element
- **Automatic**: CSS variables switch automatically with `.dark` class — no JavaScript needed

!!! warning "Every component must support dark mode"
    New CSS classes or components must define both `:root` and `.dark` values.

## Dark Mode Toggle Architecture

### Core Principle

!!! danger "NEVER trigger server-side re-render on Dark Mode toggle"
    **Forbidden**: calling `content_area.refresh()` or any DOM-rebuilding operation inside `ui.dark_mode(on_change=...)`.
    This causes: expanded panels collapsing, form state loss, severe UX degradation.

### Quasar Native Components

NiceGUI components are Quasar-based and automatically follow Dark Mode toggling (via `body--dark` class).
No extra handling needed.

### Third-Party Chart Libraries (Plotly, etc.)

Plotly and other non-Quasar components do not automatically follow theme changes. The solution is a **client-side MutationObserver**,
injected as a global `<script>` in `layout.py`, that watches `<body>` class changes and calls `Plotly.relayout()`:

```javascript
// Injected in layout.py via ui.add_head_html()
document.addEventListener('DOMContentLoaded', function() {
  const DARK_LAYOUT  = { template: 'plotly_dark',  paper_bgcolor: '...', ... };
  const LIGHT_LAYOUT = { template: 'plotly_white', paper_bgcolor: '...', ... };

  function relayoutAll() {
    requestAnimationFrame(function() {
      const isDark = document.body.classList.contains('body--dark');
      document.querySelectorAll('.js-plotly-plot').forEach(function(el) {
        Plotly.relayout(el, isDark ? DARK_LAYOUT : LIGHT_LAYOUT);
      });
    });
  }

  new MutationObserver(function(mutations) {
    for (const m of mutations) {
      if (m.attributeName === 'class') { relayoutAll(); return; }
    }
  }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
});
```

Benefits of this pattern:

- ✅ **Zero server round-trips**: runs entirely in the browser
- ✅ **Zero state loss**: expanded panels, tabs, and toggles all preserved
- ✅ **Instant effect**: Plotly chart background and text colors update synchronously

### Initial Render

When initially rendering charts, use `get_plotly_layout()` for the initial theme (server-side, runs once):

```python
from core.shared.visualization import get_plotly_layout

# ✅ Correct: specify theme at initial render
is_dark = app.storage.user.get("dark_mode", True)
fig.update_layout(**get_plotly_layout(dark=is_dark))
```

`get_plotly_layout(dark=True)` returns:

- `template`: `plotly_dark` / `plotly_white`
- `paper_bgcolor`: maps to `--surface`
- `plot_bgcolor`: maps to `--bg`
- `font.color`: maps to `--fg`
- `font.family`: `Inter, Arial, sans-serif`

!!! tip "Adding new third-party chart libraries"
    When introducing chart libraries that don't support Quasar Dark Mode,
    add corresponding relayout logic to the MutationObserver script in `layout.py`.

---

## Agent Rule { #agent-rule }

```markdown
## Theming
- Use CSS variable tokens: `--bg`, `--surface`, `--elevated`, `--fg`, `--muted`, `--border`, `--primary`.
- Forbidden: hardcoded colors (`bg-white`, `text-black`, `#hex`, `rgb(literal)`).
- Tailwind is layout-only (flex, p-4, gap-2). Colors = CSS variables.
- Dark mode: default ON. Toggle flips `.dark` / `body--dark` on root, CSS variables auto-switch.
- CRITICAL: NEVER call `content_area.refresh()` or any server-side re-render on dark mode toggle. This destroys UI state.
- Plotly theme sync uses a client-side MutationObserver in `layout.py` that watches `body--dark` and calls `Plotly.relayout()`. No server round-trip.
- Initial chart render: use `get_plotly_layout(dark=app.storage.user.get("dark_mode", True))`.
- New third-party chart libs must be registered in the MutationObserver script in `layout.py`.
- New CSS classes must define both `:root` and `.dark` values.
```
