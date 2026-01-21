---
aliases:
  - "Type Checking Rules"
  - "類型檢查規範"
tags:
  - boundary/system
  - audience/team
  - sot
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

1. **零錯誤原則**：`uv run basedpyright src` 必須通過，無錯誤。

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

- [[./code-style.md|Code Style]] - 程式風格規範
- [[./index.md|Guardrails]] - 規範總覽
