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
