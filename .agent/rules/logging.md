---
trigger: model_decision
description: When implementing codes.
---

## Logging
- **No `print()` in `core/`**: Use `logging` module only.
- **`print()` allowed ONLY in `scripts/`**: For final CLI output.
- **Setup**:
    - Import: `import logging; logger = logging.getLogger(__name__)`
    - Configure in CLI: `from core.shared.logging import setup_logging`
- **Levels**:
    - `logger.debug()`: Development details.
    - `logger.info()`: Normal flow (e.g., "Processing file...").
    - `logger.warning()`: Potential issues (e.g., "File not found").
    - `logger.error()`: Errors that allow continuation.
    - `logger.critical()`: Fatal errors.
- **Never**: Use f-string in logger. Use `logger.info("Value: %s", value)`.
