## Design Patterns
- Keep shared workflow logic in backend services or `src/core/`, not in React components, FastAPI routers, or CLI commands.
- Use dependency injection or explicit factories for services, repositories, and adapters.
- Keep one canonical circuit definition that feeds schemdraw, simulation, analysis, API, and CLI.
- API handlers should do I/O, auth, validation, service invocation, and response mapping only.
- CLI commands should orchestrate user input/output, then delegate to shared services/core.
