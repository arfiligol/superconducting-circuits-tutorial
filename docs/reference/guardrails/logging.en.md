---
aliases:
  - "Logging Rules"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Logging standards: levels, colors, usage"
version: v1.0.0
last_updated: 2026-01-27
updated_by: docs-team
---

# Logging Standards

This project uses the standard Python `logging` module combined with **Rich** for colored output.

## Principles

1.  **No `print()` in `core/`** - Only `scripts/` layer can perform direct output.
2.  **Use `logging` in `core/`** - Let the caller decide how to handle logs.
3.  **Colored Levels** - Use Rich Console output.
4.  **Rich is the standard logger output** - CLI must use `RichHandler`.

## Log Levels

| Level | Usage | Color |
| :--- | :--- | :--- |
| `DEBUG` | Development details | Gray |
| `INFO` | Normal flow information | Green |
| `WARNING` | Potential issues | Yellow |
| `ERROR` | Errors allowing continuation | Red |
| `CRITICAL` | Fatal errors | Bold Red |

## Usage

### In `core/` Layer

```python
import logging

logger = logging.getLogger(__name__)

def process_data(path: Path) -> Result:
    logger.info("Processing %s", path.name)

    if not path.exists():
        logger.warning("File not found: %s", path)
        return None

    try:
        result = do_something()
        logger.debug("Result: %s", result)
        return result
    except ValueError as e:
        logger.error("Failed to process: %s", e)
        raise
```

### In `scripts/` Layer (CLI Entry Point)

```python
from core.shared.logging import setup_logging

def main() -> None:
    setup_logging(level="INFO")  # or DEBUG for verbose

    # Now all core/ logging will be colored
    result = process_data(path)

    # CLI layer can use print() for final output
    print(f"Result: {result}")
```

## Configuration

### Default Logger Setup (`core/shared/logging.py`)

```python
from rich.logging import RichHandler

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
```

## Migration Guide

Replace existing `print()` calls with `logging`:

| Original | Replacement |
| :--- | :--- |
| `print(f"[Info] ...")` | `logger.info("...")` |
| `print(f"[Warning] ...")` | `logger.warning("...")` |
| `print(f"[Error] ...")` | `logger.error("...")` |
| `print(f"[OK] ...")` | `logger.info("...")` |

---

## Agent Rule { #agent-rule }

```markdown
## Logging
- **No `print()` in `core/`**: Use `logging` module only.
- **`print()` allowed ONLY in `scripts/`**: For final CLI output.
- **Setup**:
    - Import: `import logging; logger = logging.getLogger(__name__)`
    - Configure in CLI: `from core.shared.logging import setup_logging`
    - **Handler**: Use `RichHandler` for colored output in CLI.
- **Levels**:
    - `logger.debug()`: Development details.
    - `logger.info()`: Normal flow (e.g., "Processing file...").
    - `logger.warning()`: Potential issues (e.g., "File not found").
    - `logger.error()`: Errors that allow continuation.
    - `logger.critical()`: Fatal errors.
- **Never**: Use f-string in logger. Use `logger.info("Value: %s", value)`.
```
