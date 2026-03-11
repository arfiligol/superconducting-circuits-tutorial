## Testing Commands
- **Backend/core tests**: `uv run pytest`
- **Frontend unit tests**: `npm run test --prefix frontend`
- **Frontend E2E tests**: `npm run test:e2e --prefix frontend`
- **Docs checks**:
    - `./scripts/prepare_docs_locales.sh`
    - `uv run --group dev zensical build -f zensical.toml`
    - `uv run --group dev zensical build -f zensical.en.toml`
    - `./scripts/build_docs_sites.sh`
- Add tests for critical workflows instead of relying on manual verification only.
