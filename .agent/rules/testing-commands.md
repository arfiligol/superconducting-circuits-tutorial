---
trigger: model_decision
description: When trying to write or test the codes.
---

## Testing Commands
- **Framework**: `pytest`
- **Command**: `uv run pytest` (Runs all tests in `tests/`)
- **Naming**:
    - Files: `test_*.py`
    - Funcs: `test_*()`
- **Structure**: `tests/` mirrors `src/sc_analysis/` structure.
    - e.g. `src/sc_analysis/domain/model.py` -> `tests/domain/test_model.py`.
- **Julia Tests**: `julia --project=. -e 'using Pkg; Pkg.test()'`
