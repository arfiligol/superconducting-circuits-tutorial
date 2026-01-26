---
trigger: model_decision
description: When doing tasks with data.
---

## Data Handling
- **Immutable**: `data/raw/` is READ-ONLY.
- **Paths**: NEVER hardcode paths.
    - **MUST** import from `core.shared.persistence.database` or `core.analysis.infrastructure.paths`.
- **Database**: Use Unit of Work pattern.
    - **MUST** use `with get_unit_of_work() as uow:` for all DB operations.
    - **NEVER** access Session directly in CLI/UI code.
    - **MUST** call `uow.commit()` explicitly.
- **Flow**: Raw -> Import CLI -> SQLite DB -> Analysis CLI -> Reports.
- **Format**: Prefer **SQLite** for structured data, **JSON** for config, **CSV** for export.
