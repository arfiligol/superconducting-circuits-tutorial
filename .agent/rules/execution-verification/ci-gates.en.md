## CI Gates
- **Mandatory Checks**:
    1. **Pre-commit**: `ruff format` + `ruff check` + `basedpyright`.
    2. **Build**: `./scripts/build_docs_sites.sh` must pass.
    3. **Test**: `pytest` must pass.
- **Tolerance**:
    - `zensical build` during docs preview: allow benign `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
