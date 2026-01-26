---
trigger: always_on
---

## Type Checking
- **Tool**: `basedpyright`
- **Strictness**: `basic` (but treated as mandatory).
- **Rules**:
    - **No `Any`**: Avoid explicit `Any` unless interfacing with untyped libs.
    - **Return Types**: MUST explicitly type return values of all functions.
    - **Collections**: Use `list[str]`, `dict[str, int]` (Standard Collections).
- **Fixes**: If type check fails, Fix the Code, DO NOT suppress unless absolutely necessary (`# type: ignore`).
