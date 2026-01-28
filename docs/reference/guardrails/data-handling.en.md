---
aliases:
  - "Data Handling Rules"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Data handling rules: read-only raw data, path constants, database access"
version: v1.1.0
last_updated: 2026-01-26
updated_by: docs-team
---

# Data Handling

Data handling and path standards.

## Directory Structure

```
data/
├── raw/                    # Raw data (read-only)
│   ├── measurement/
│   │   └── flux_dependence/
│   ├── circuit_simulation/
│   └── layout_simulation/
│       ├── admittance/
│       └── phase/
├── preprocessed/           # Legacy JSON archive (read-only/deprecated)
├── processed/
│   └── reports/            # Analysis outputs
└── database.db             # SQLite database
```

## Rules

### 1. Raw Data is Read-Only

All files under `data/raw/` are immutable:

- Do not modify raw files
- Do not delete raw files
- Transformation results **must** be written to **SQLite database**

### 2. Use Path Helpers

Use constants provided by `src/core/shared/persistence/database.py`:

```python
from core.shared.persistence.database import DATABASE_PATH
```

### 3. Database Access (Unit of Work)

All database access must use the Unit of Work pattern:

```python
from core.shared.persistence import get_unit_of_work

# ✅ Correct: use UoW
with get_unit_of_work() as uow:
    dataset = uow.datasets.get_by_name("PF6FQ_Q0_XY")
    uow.datasets.add(new_dataset)
    uow.commit()

# ❌ Incorrect: direct session usage
session = get_session()
session.query(DatasetRecord).filter_by(...)
```

### 4. Output Locations

| Type | Target Directory |
|------|------------------|
| Data records | `data/database.db` (SQLite) |
| Analysis reports | `data/processed/reports/` |
| Figures/Plots | `data/processed/reports/` |

## Related

- [Dataset Record Schema](../data-formats/dataset-record.md) - Database schema
- [Raw Data Layout](../data-formats/raw-data-layout.md) - Directory structure details
- [Script Authoring](script-authoring.md) - Script writing rules

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
