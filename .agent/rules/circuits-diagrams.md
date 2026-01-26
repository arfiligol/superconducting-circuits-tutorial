---
trigger: model_decision
description: When you are handling things with circuit diagrams especially when handling docs.
---

## Circuit Diagrams
- **Tool**: Schemdraw (Python)
- **Workflow**:
    1. Create script in `scripts/docs/` (e.g., `generate_lc.py`).
    2. Run with `uv run`.
    3. Output SVG to `docs/assets/`.
- **Markdown Embedding**:
    - MUST use `![Alt](../assets/file.svg)`.
    - MUST include source code in `??? quote "Source Code"`.
- **Pattern**: See "範例樣板" in doc for boilerplate.
