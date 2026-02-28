---
aliases:
  - "Guardrails: Component Guidelines"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: Component Guidelines

This document defines NiceGUI component usage rules and forbidden patterns.

## Core Principle

All UI interactive elements must use **NiceGUI built-in components**. Native HTML elements and browser-native dialogs are forbidden.

## Allowed Components

### Data Display

| Component | Purpose | Example |
|---|---|---|
| `ui.table` | Data tables (sortable, selectable) | Record listings |
| `ui.plotly` | Interactive charts | Frequency response, heatmaps |
| `ui.label` | Text display | Titles, descriptions |
| `ui.html` | **Static content only** | Formatted text, icons |

### Interactive Controls

| Component | Purpose | Example |
|---|---|---|
| `ui.button` | Action buttons | Navigation, triggers |
| `ui.select` | Dropdowns | Dataset filtering |
| `ui.input` | Text input | Search bar |
| `ui.switch` | Toggles | Dark mode switch |
| `ui.slider` | Sliders | Numeric range selection |

### Layout

| Component | Purpose |
|---|---|
| `ui.column` | Vertical arrangement |
| `ui.row` | Horizontal arrangement |
| `ui.card` | Card container (prefer `.app-card` class) |
| `ui.separator` | Divider |
| `ui.space` | Flexible spacer |

### Feedback & Dialogs

| Component | Purpose |
|---|---|
| `ui.notify` | Toast notifications |
| `ui.dialog` | Modal dialogs |
| `ui.spinner` | Loading indicators |

## Forbidden Patterns

### ❌ `ui.aggrid`

NiceGUI's internal AG Grid JavaScript wrapper has known compatibility issues (`TypeError: Cannot read properties of undefined (reading 'withPart')`).

**Alternative**: Use `ui.table` with `rowClick` event handling.

```python
# ✅ Correct
grid = ui.table(columns=cols, rows=data, row_key="id")
grid.on("rowClick", handle_click)

# ❌ Forbidden
grid = ui.aggrid(options, theme="balham-dark")
```

### ❌ Browser Native Dialogs

Forbidden: `alert()`, `confirm()`, `prompt()`.

```python
# ✅ Correct
ui.notify("Operation successful", type="positive")

with ui.dialog() as dialog, ui.card():
    ui.label("Confirm deletion?")
    ui.button("Confirm", on_click=lambda: dialog.close())

# ❌ Forbidden
ui.run_javascript("alert('Operation successful')")
```

### ❌ Native HTML Interactive Elements

Forbidden: creating interactive controls via `ui.html()`.

```python
# ✅ Correct
ui.button("Submit").classes("app-btn-primary")

# ❌ Forbidden
ui.html('<button class="app-btn-primary">Submit</button>')
```

### ❌ Inline Hardcoded Colors

Forbidden: using hardcoded color values in `.style()`.

```python
# ✅ Correct
ui.label("Title").classes("text-fg")

# ❌ Forbidden
ui.label("Title").style("color: white;")
```

## Styling Methods

Use `.classes()` and `.props()` to apply styles. Do not use `.style()` for colors.

```python
# ✅ Recommended pattern
ui.button("Action", icon="add") \
    .classes("app-btn-primary") \
    .props("flat no-caps")
```

---

## Agent Rule { #agent-rule }

```markdown
## Component Guidelines
- Use NiceGUI components: `ui.table`, `ui.button`, `ui.label`, `ui.select`, `ui.plotly`.
- Forbidden: `ui.aggrid` (known JS compatibility errors); use `ui.table` instead.
- Forbidden: raw HTML for interactive controls (`ui.html('<button>')` etc.).
- Forbidden: `alert()`, `confirm()`, `prompt()` — use `ui.notify()` or `ui.dialog()`.
- Plotly: always render via `ui.plotly(fig)`, never via iframe or raw HTML.
- Style with `.classes()` and `.props()` — never `.style()` with literal colors.
```
