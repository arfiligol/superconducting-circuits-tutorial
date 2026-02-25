---
aliases:
  - "Guardrails: Layout Patterns"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: Layout Patterns

This document defines page structure, shell architecture, and responsive layout rules.

## Shell Principle

All pages **must** render inside `app_shell()`.

```python
from app.layout import app_shell

@ui.page("/my-page")
def my_page():
    def content():
        ui.label("Page Content")

    app_shell(content)()  # ← every page follows this pattern
```

`app_shell` provides:

- **Header**: Title bar (with dark mode toggle)
- **Left Drawer**: Navigation menu
- **Content Area**: Main content area (`max-w-7xl mx-auto`)

!!! warning "No standalone pages"
    Pages must not be created without `app_shell()`. New pages must also update the navigation menu in `layout.py`.

## Card Pattern

Content blocks use `.app-card` wrapper with `.app-section-title` headings.

```python
with ui.column().classes("app-card w-full p-4"):
    ui.label("Section Title").classes("app-section-title mb-4")
    # Content here
```

### Card Specifications

| Property | Value |
|---|---|
| Background | `rgb(var(--surface))` |
| Border | `1px solid rgb(var(--border))` |
| Border radius | `0.75rem` (12px) |
| Shadow | `0 1px 2px 0 rgb(15 23 42 / 0.08)` |

## Responsive Rules

Use Tailwind's `lg:` prefix to differentiate desktop and mobile.

```python
# Master-Detail layout
with ui.row().classes("w-full gap-6 flex-wrap lg:flex-nowrap"):
    # Master: full width on mobile
    with ui.column().classes("w-full lg:w-[45%]"):
        ...

    # Detail: stacks below on mobile
    with ui.column().classes("w-full lg:w-[55%]"):
        ...
```

### Breakpoints

| Breakpoint | Width | Behavior |
|---|---|---|
| Default | < 1024px | Single column stack |
| `lg:` | ≥ 1024px | Multi-column side-by-side |

## Page Layout Patterns

### Master-Detail (Data Browsing)

Left: data list. Right: detail preview.

```
┌─────────────┬──────────────────────┐
│  Table      │  Visualization       │
│  (45%)      │  (55%)               │
│             ├──────────────────────┤
│             │  Derived Parameters  │
└─────────────┴──────────────────────┘
```

### Dashboard

Statistics cards + module link grid.

```
┌──────────┬──────────┬──────────┐
│  Stat 1  │  Stat 2  │  Stat 3  │
├──────────┴──────────┴──────────┤
│  Module Cards (grid)           │
└────────────────────────────────┘
```

## Content Area Specifications

| Property | Value | Notes |
|---|---|---|
| Max width | `max-w-7xl` (80rem) | Prevent over-stretching |
| Centering | `mx-auto` | Horizontal centering |
| Padding | `p-4 md:p-8` | Mobile / Desktop |
| Gap | `gap-6` | Uniform spacing |

## Navigation Management

When adding new pages, update the Left Drawer in `src/app/layout.py`:

```python
# layout.py — inside Left Drawer
ui.button(
    "New Page",
    icon="icon_name",
    on_click=lambda: ui.navigate.to("/new-page"),
).classes("w-full justify-start").props("flat no-caps")
```

---

## Agent Rule { #agent-rule }

```markdown
## Layout Patterns
- Shell Principle: all pages MUST render inside `app_shell(content_builder)`.
- Card pattern: wrap content sections in `.app-card` containers.
- Section title: use `.app-section-title` for headings inside cards.
- Responsive: use `lg:` Tailwind prefix for desktop; stack on mobile.
- Max width: content area is `max-w-7xl mx-auto`.
- Navigation: add new pages to the left drawer in `layout.py`.
- Forbidden: standalone pages outside `app_shell()`.
```
