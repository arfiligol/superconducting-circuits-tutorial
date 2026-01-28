---
aliases:
  - "Clean Architecture"
  - "Layered Architecture"
tags:
  - diataxis/explanation
  - status/stable
  - topic/architecture
  - topic/cli
  - topic/database
status: stable
owner: docs-team
audience: team
scope: "Clean Architecture layers and dependency direction"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Clean Architecture

We use **Clean Architecture** to separate CLI, services, and persistence so core logic stays reusable and testable.

## Layers and Responsibilities

### Interface / CLI Layer

- Role: argument parsing and output rendering.
- Example: `src/scripts/database/manage_db.py`
- Rule: no business logic here; only call Services.

### Application / Service Layer

- Role: orchestrate use-cases and workflows.
- Example: `src/core/analysis/application/services/dataset_management.py`
- Rule: return DTOs instead of ORM models to avoid coupling.

### Persistence Layer

- Role: transactions and data access.
- Example: `SqliteUnitOfWork` + `DatasetRepository`
- Rule: Unit of Work controls transactions; repositories handle queries and writes.

## Dependency Direction

Dependencies go **inward only**:

```
CLI → Service → Persistence
```

Core logic must not depend on CLI or database details.

## Data and Deletion Policy

- Dataset → DataRecord uses ORM **cascade** so deleting a Dataset removes its DataRecords.
- Tags are shared labels and should not participate in parent/child cascade deletes.

## Related

- [Schema Design](schema-design.md) - Data structure decisions
- [Database CLI Reference](../../../reference/cli/sc-db.md) - CLI commands
