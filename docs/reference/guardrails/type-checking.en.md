---
aliases:
  - "Type Checking Rules"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "BasedPyright Type Checking Rules"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Type Checking

BasedPyright type checking rules and standards.

## Requirements

1. **Basic Check Only**: `uv run basedpyright src` must pass in `basic` mode. Focus on definitions and syntax.

2. **Type Annotations**: All functions must have type annotations for arguments and return values.

3. **Modern Syntax**: Use Python 3.12+ syntax.
   ```python
   # ✅ Correct
   def process(items: list[str]) -> dict[str, int]: ...
   def get_value() -> str | None: ...

   # ❌ Incorrect
   from typing import List, Dict, Optional
   def process(items: List[str]) -> Dict[str, int]: ...
   ```

## Exceptions

- **Matplotlib**: Matplotlib related calls can use `# type: ignore`.
- **lmfit**: Third-party libraries without type stubs can be marked with `# type: ignore`.

## Argparse Typing

Use `NamedTuple` to ensure `parse_args()` returns a typed object:

```python
from typing import NamedTuple
import argparse

class Args(NamedTuple):
    input_file: str
    output_dir: str
    verbose: bool

def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    # ... setup ...
    args = parser.parse_args()
    return Args(
        input_file=args.input_file,
        output_dir=args.output_dir,
        verbose=args.verbose,
    )
```

## Related

- [Code Style](code-style.md) - Coding style guidelines
- [Guardrails](index.md) - Overview

---

## Agent Rule { #agent-rule }

```markdown
## Type Checking
- **Tool**: `basedpyright`
- **Strictness**: `basic` (but treated as mandatory).
- **Rules**:
    - **No `Any`**: Avoid explicit `Any` unless interfacing with untyped libs.
    - **Return Types**: MUST explicitly type return values of all functions.
    - **Collections**: Use `list[str]`, `dict[str, int]` (Standard Collections).
- **Fixes**: If type check fails, Fix the Code, DO NOT suppress unless absolutely necessary (`# type: ignore`).
```
