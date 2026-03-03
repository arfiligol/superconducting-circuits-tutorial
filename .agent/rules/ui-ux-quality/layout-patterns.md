## Layout Patterns
- Shell Principle: all pages MUST render inside `app_shell(content_builder)`.
- Spacing:
    *   Use 8pt grid system.
    *   Card internal padding is `p-6` for spacious feel.
    *   Block gaps are `gap-6`.
    *   Title margins are `mb-4`.
    *   DO NOT use arbitrary margins like `mt-3` or `px-5`.
- Content area: `w-full px-4 py-3`, `gap-6`. Forbidden: `max-w-*` on app_shell, allow full width.
- Nav drawer: width=220, buttons with `dense` prop.
- Master/Detail proportions: tables should usually be `w-[45%]`, visualizations `w-[55%]`.
- Responsive: use `lg:` Tailwind prefix for desktop; stack on mobile.
- Navigation: add new pages to the left drawer in `layout.py`.
- Forbidden: standalone pages outside `app_shell()`.
