## Component Guidelines
- Use NiceGUI components: `ui.table`, `ui.button`, `ui.label`, `ui.select`, `ui.plotly`.
- Forbidden: `ui.aggrid` (known JS compatibility errors); use `ui.table` instead.
- Forbidden: raw HTML for interactive controls (`ui.html('<button>')` etc.).
- Forbidden: `alert()`, `confirm()`, `prompt()` — use `ui.notify()` or `ui.dialog()`.
- Plotly: always render via `ui.plotly(fig)`, never via iframe or raw HTML.
- Style with `.classes()` and `.props()` — never `.style()` with literal colors.
