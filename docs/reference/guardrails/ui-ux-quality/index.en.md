---
aliases:
  - "Guardrails: UI/UX Quality"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: UI/UX Quality

The project's NiceGUI application (`src/app/`) follows unified UI quality standards to ensure visual consistency and maintainability.

!!! important "Source of Truth"
    All UI components, colors, and layouts must comply with the sub-rules below.

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Framework | **NiceGUI** | Python-native UI framework (Quasar/Vue under the hood) |
| Styling | **CSS Variables** (Design Tokens) | `theme.css` — `--bg`, `--surface`, `--fg`, etc. |
| Layout | **Tailwind CSS** | Layout only (`flex`, `p-4`, `gap-2`) — **never** for colors |
| Components | **NiceGUI built-ins** | `ui.table`, `ui.plotly`, `ui.label`, `ui.button` |
| Visualization | **Plotly** | Theme-synced via `plotly_theme.py` |
| Dark Mode | **`ui.dark_mode()`** | `.dark` class on root toggles CSS variables |

## Sub-rules

| Rule | Description | Agent Rule |
|---|---|---|
| [Theming](./theming.en.md) | Design tokens, dark mode, Plotly theme sync | [#agent-rule](./theming.en.md#agent-rule) |
| [Component Guidelines](./component-guidelines.en.md) | NiceGUI component usage, forbidden patterns | [#agent-rule](./component-guidelines.en.md#agent-rule) |
| [Layout Patterns](./layout-patterns.en.md) | Shell architecture, card layout, responsive rules | [#agent-rule](./layout-patterns.en.md#agent-rule) |

---

## Agent Rule { #agent-rule }

```markdown
## UI/UX Quality
- **Framework**: NiceGUI (`src/app/`). All pages inside `app_shell()`.
- **Styling**: CSS Variables (design tokens) for colors. Tailwind for layout only.
- **Dark Mode**: Default ON. `.dark` class toggles CSS variables.
- **Vis**: Plotly via `ui.plotly(fig)`, theme-synced via `get_plotly_layout(dark)`.
- **Forbidden**: hardcoded colors, `ui.aggrid`, `alert()`/`confirm()`, raw HTML controls.
- Sub-rules: Theming, Component Guidelines, Layout Patterns.
```
