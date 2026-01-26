---
trigger: model_decision
description: When trying to commit or do other stuffs of version control.
---

## CI Gates
- **Mandatory Checks**:
    1. **Pre-commit**: `ruff format` + `ruff check` + `basedpyright`.
    2. **Build**: `mkdocs build` must pass.
    3. **Test**: `pytest` must pass.
- **Tolerance**:
    - `mkdocs build`: Allow `404` warnings logic.
    - Code Coverage: Not strictly enforced yet.
- **Fast Fail**: Any lint error fails the pipeline immediately.
