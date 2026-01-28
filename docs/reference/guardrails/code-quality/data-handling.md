---
aliases:
  - "Data Handling Rules"
  - "數據處理規範"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "數據處理規範：原始數據唯讀、路徑常數、資料庫存取"
version: v1.1.0
last_updated: 2026-01-26
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
├── preprocessed/           # Legacy JSON Archive (唯讀/棄用)
├── processed/
│   └── reports/            # 分析輸出
└── database.db             # SQLite 資料庫
```

## Rules

### 1. Raw Data is Read-Only

`data/raw/` 下的所有檔案視為不可變：

- 不修改原始檔案
- 不刪除原始檔案
- 轉換結果必須寫入 **SQLite 資料庫**

### 2. Use Path Helpers

使用 `src/core/shared/persistence/database.py` 提供的常數：

```python
from core.shared.persistence.database import DATABASE_PATH
```

### 3. Database Access (Unit of Work)

所有資料庫存取必須透過 Unit of Work 模式：

```python
from core.shared.persistence import get_unit_of_work

# ✅ 正確：使用 UoW
with get_unit_of_work() as uow:
    dataset = uow.datasets.get_by_name("PF6FQ_Q0_XY")
    uow.datasets.add(new_dataset)
    uow.commit()

# ❌ 錯誤：直接操作 Session
session = get_session()
session.query(DatasetRecord).filter_by(...)
```

### 4. Output Locations

| 類型 | 目標位置 |
|------|----------|
| 數據紀錄 | `data/database.db` (SQLite) |
| 分析報告 | `data/processed/reports/` |
| 圖表 | `data/processed/reports/` |

## Related

- [Dataset Record Schema](../../data-formats/dataset-record.md) - 資料庫 Schema
- [Raw Data Layout](../../data-formats/raw-data-layout.md) - 目錄結構詳情
- [Script Authoring](script-authoring.md) - 腳本撰寫規範

---

## Agent Rule { #agent-rule }

```markdown
## Data Handling
- **Immutable**: `data/raw/` is READ-ONLY.
- **Paths**: NEVER hardcode paths.
    - **MUST** import from `core.shared.persistence.database`.
- **Database**: Use Unit of Work pattern.
    - **MUST** use `with get_unit_of_work() as uow:` for all DB operations.
    - **NEVER** access Session directly in CLI/UI code.
    - **MUST** call `uow.commit()` explicitly.
- **Flow**: Raw -> Import CLI -> SQLite DB -> Analysis CLI -> Reports.
- **Format**: Prefer **SQLite** for structured data, **JSON** for config, **CSV** for export.
- **Legacy**: `data/preprocessed/` is ARCHIVED. Do not write new JSON files there.
```
