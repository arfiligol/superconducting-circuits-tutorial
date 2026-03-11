## State Management
- Use SWR for server state.
- Use React Hook Form + Zod for form state.
- Use Context or local state for UI-only state.
- Use route params or search params for shareable page state.
- Do not scatter direct `fetch` calls across components.
- Keep read and mutation logic in hooks or services with explicit loading/error handling.
