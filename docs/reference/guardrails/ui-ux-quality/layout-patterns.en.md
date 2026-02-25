---
aliases:
  - "Guardrails: Layout Patterns"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: Layout Patterns

This document defines page structure, shell architecture, spacing system, and responsive layout rules.

## Spacing Scale

This project follows an **8pt grid system** — all spacing values must be multiples of 4.

!!! important "Data-Dense Dashboard"
    This application is a data-dense dashboard and should use **Compact Density**,
    prioritizing smaller spacing values to maximize data display area.

### Spacing Tokens

| Token | Value | Purpose |
|---|---|---|
| `gap-1` | 4px | Minimum spacing — elements within the same group |
| `gap-2` / `p-2` | 8px | Tight spacing — between labels and content |
| `gap-6` / `p-6` | 24px | **Default card padding** — data cards, **Default block gap** — Master-Detail, module cards, Large spacing — page-level sections only |

### Rules

1.  **Space and Margins**:
    *   **Margin**: The default gap between cards or large blocks is `gap-6`.
    *   **Padding**: The default internal padding for cards is `p-6`.
    *   **Layout Direction**: Avoid placing text and charts too closely; maintain appropriate breathing space.
2.  **App Card (Module Container)**:
    *   Apply the `.app-card` style.
    *   By default, use an internal padding of `p-6` (24px) to maintain comfortable breathing room.
    *   The module title should be placed at the top, applying `.app-section-title` with an `mb-4` bottom margin.
3. **Content area padding**: Use `px-4 py-3` (horizontal 16px, vertical 12px)
4. **Forbidden**: `p-8` (32px) or larger on cards or content areas

### Navigation Density

| Property | Value | Notes |
|---|---|---|
| Drawer width | 220px | More compact than default 300px |
| Nav buttons | `dense` prop | Reduces row height to ~32px |
| Nav padding | `px-1` | Reduces left/right whitespace |
| Section label gap | `mb-1` | Tighter section separation |

### Table Density

| Property | Value | Notes |
|---|---|---|
| Table | `dense` prop | Row height ~36px (default ~48px) |
| Column spacing | 16px minimum | Ensure adequate column separation |

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
with ui.column().classes("app-card w-full p-6"):
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
    with ui.column().classes("w-full lg:w-[60%]"):
        # Master Block (List/Table):
        # Occupies 60% of the width on large screens (`lg:w-[60%]`).
        # Should be designed to operate independently, without relying on the state of the Detail block.
        ...

    # Detail: stacks below on mobile
    with ui.column().classes("w-full lg:w-[40%]"):
        # Detail Block (Charts/Details):
        # Occupies the remaining 40% width on large screens (`lg:w-[40%]`).
        # The state should dynamically update based on the selection in the Master block.
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
| Width | `w-full` | Utilize full screen width |
| Padding | `px-4 py-3` | Horizontal 16px / Vertical 12px |
| Gap | `gap-4` | Block gap 16px |

## Navigation Management

When adding new pages, update the Left Drawer in `src/app/layout.py`:

```python
# layout.py — inside Left Drawer
ui.button(
    "New Page",
    icon="icon_name",
    on_click=lambda: ui.navigate.to("/new-page"),
).classes("w-full justify-start").props("flat no-caps dense")
```

---

## Agent Rule { #agent-rule }

```markdown
## Layout Patterns
- Shell Principle: all pages MUST render inside `app_shell(content_builder)`.
- 8pt Grid: all spacing in multiples of 4px. Use compact density for data-dense views.
- Card data: `p-3` (12px). Dashboard overview: `p-4` (16px). Section title: `mb-2`.
- Content area: `w-full px-4 py-3`, `gap-4`. Forbidden: `max-w-*` on app_shell, allow full width.
- Nav drawer: width=220, buttons with `dense` prop.
- Master/Detail proportions: tables should be `w-[60%]`, visualizations `w-[40%]`.
- Tables: use `dense` prop for compact row height (~36px).
- Responsive: use `lg:` Tailwind prefix for desktop; stack on mobile.
- Navigation: add new pages to the left drawer in `layout.py`.
- Forbidden: standalone pages outside `app_shell()`.
```
