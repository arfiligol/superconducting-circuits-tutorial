## Backend Architecture
- Treat backend as a headless application backend, not just a thin CRUD API.
- Keep API handlers limited to parsing, auth, service invocation, response mapping, and transport error translation.
- Keep service errors framework-agnostic; FastAPI-specific exceptions belong in the API layer.
- Keep persistence, TraceStore, and execution adapters in infrastructure.
- Reuse `sc_core` for canonical scientific contracts instead of duplicating them in backend adapters.
- Do not let frontend state, Electron concerns, or transport-only display state leak into backend services or domain.
