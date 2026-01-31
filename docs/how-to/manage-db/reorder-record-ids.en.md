---
aliases:
  - "Reorder Record IDs"
  - "Reorder Record IDs (sc-db)"
tags:
  - diataxis/how-to
  - status/stable
  - topic/cli
  - topic/database
status: stable
owner: docs-team
audience: user
scope: "Auto-reorder record IDs with sc-db"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Reorder Record IDs (sc-db)

Use `auto-reorder` to keep record IDs contiguous after deletions.

## Usage

```bash
uv run sc-db <model> auto-reorder
```

## Examples

### Dataset Records

```bash
uv run sc-db dataset-record auto-reorder
```

### Data Records

```bash
uv run sc-db data-record auto-reorder
```

### Derived Parameters

```bash
uv run sc-db derived-parameter auto-reorder
```

### Tags

```bash
uv run sc-db tag auto-reorder
```

## Notes / Warnings

!!! warning "Duplicate IDs"
    `auto-reorder` checks for ID conflicts and aborts with an error if duplicates would occur.

## CLI Help (Auto-generated)

See the model-specific CLI references:

- [sc-db dataset-record](../../reference/cli/sc-db-dataset-record.md)
- [sc-db data-record](../../reference/cli/sc-db-data-record.md)
- [sc-db derived-parameter](../../reference/cli/sc-db-derived-parameter.md)
- [sc-db tag](../../reference/cli/sc-db-tag.md)
