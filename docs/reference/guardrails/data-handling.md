---
aliases:
  - "Data Handling Rules"
  - "數據處理規範"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "數據處理規範：原始數據唯讀、路徑常數使用"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Data Handling

數據處理與路徑規範。

## Directory Structure

```
data/
├── raw/                    # 原始數據 (唯讀)
│   ├── measurement/
│   │   └── flux_dependence/
│   ├── circuit_simulation/
│   └── layout_simulation/
│       ├── admittance/
│       └── phase/
├── preprocessed/           # 轉換後的 JSON
└── processed/
    └── reports/            # 分析輸出
```

## Rules

### 1. Raw Data is Read-Only

`data/raw/` 下的所有檔案視為不可變：

- 不修改原始檔案
- 不刪除原始檔案
- 轉換結果寫入 `data/preprocessed/`

### 2. Use Path Helpers

使用 `src/utils/paths.py` 提供的常數：

```python
from src.utils import (
    RAW_LAYOUT_ADMITTANCE_DIR,
    RAW_LAYOUT_PHASE_DIR,
    RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR,
    PREPROCESSED_DATA_DIR,
    PROCESSED_REPORTS_DIR,
)

# ✅ 正確
output_path = PROCESSED_REPORTS_DIR / "result.json"

# ❌ 錯誤
output_path = Path("data/processed/reports/result.json")
```

### 3. Output Locations

| 類型 | 目標目錄 |
|------|----------|
| 前處理 JSON | `data/preprocessed/` |
| 分析報告 | `data/processed/reports/` |
| 圖表 | `data/processed/reports/` |

## Related

- [Raw Data Layout](../data-formats/raw-data-layout.md) - 目錄結構詳情
- [Script Authoring](script-authoring.md) - 腳本撰寫規範

---

## Agent Rule { #agent-rule }

```markdown
## Data Handling
- **Immutable**: `data/raw/` is READ-ONLY.
- **Paths**: NEVER hardcode paths.
    - **MUST** import from `src.utils.paths`.
    - Keywords: `RAW_*_DIR`, `PREPROCESSED_DATA_DIR`, `PROCESSED_REPORTS_DIR`.
- **Flow**: Raw -> Preprocessing Script -> Preprocessed (JSON) -> Analysis Script -> Processed (Reports).
- **Format**: Prefer **JSON** for light data, **CSV** for tabular data.
```
