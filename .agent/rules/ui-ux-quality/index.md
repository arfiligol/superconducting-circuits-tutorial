## UI/UX Quality
- **Framework**: NiceGUI (`src/app/`). All pages inside `app_shell()`.
- **Styling**: CSS Variables (design tokens) for colors. Tailwind for layout only.
- **Dark Mode**: Default ON. `.dark` class toggles CSS variables.
- **Vis**: Plotly via `ui.plotly(fig)`, theme-synced via `get_plotly_layout(dark)`.
- **Forbidden**: hardcoded colors, `ui.aggrid`, `alert()`/`confirm()`, raw HTML controls.
- Sub-rules: Theming, Component Guidelines, Layout Patterns.
