---
aliases:
  - "Type Checking Rules"
  - "類型檢查規範"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "BasedPyright 類型檢查規範"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Type Checking

BasedPyright 類型檢查規範。

## Requirements

1. **Basic Check Only**：`uv run basedpyright src` 需通過 `basic` 模式檢查。專注於變數是否定義與基本語法。

2. **類型標註**：所有函數必須標註參數與回傳值類型。

3. **現代語法**：使用 Python 3.12+ 語法。
   ```python
   # ✅ 正確
   def process(items: list[str]) -> dict[str, int]: ...
   def get_value() -> str | None: ...

   # ❌ 錯誤
   from typing import List, Dict, Optional
   def process(items: List[str]) -> Dict[str, int]: ...
   ```

## Exceptions

- **Matplotlib**：Matplotlib 相關呼叫可使用 `# type: ignore`。
- **lmfit**：第三方庫無類型存根時標記 `# type: ignore`。

## Argparse Typing

使用 `NamedTuple` 確保 `parse_args()` 回傳有類型的物件：

```python
from typing import NamedTuple

class Args(NamedTuple):
    input_file: str
    output_dir: str
    verbose: bool

def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    # ... setup ...
    ns = parser.parse_args()
    return Args(
        input_file=ns.input_file,
        output_dir=ns.output_dir,
        verbose=ns.verbose,
    )
```

## Related

- [Code Style](code-style.md) - 程式風格規範
- [Guardrails](../index.md) - 規範總覽

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
