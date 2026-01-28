---
aliases:
  - "Manage Datasets with sc-db"
  - "使用 sc-db 管理資料集"
tags:
  - diataxis/how-to
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# Manage Datasets with sc-db

This guide shows how to list, inspect, and delete imported Datasets with `sc-db`.

## Prerequisites

- Data has been ingested and `data/database.db` exists.

## Steps

1. **List all Datasets**

   ```bash
   uv run sc-db list
   ```

2. **Inspect a Dataset** (by ID or Name)

   ```bash
   # By ID
   uv run sc-db info 3

   # By Name
   uv run sc-db info Checkpoint3_Single
   ```

3. **Delete a Dataset** (interactive confirmation required)

   ```bash
   uv run sc-db delete 3
   ```

   Type `y` to confirm deletion.

!!! warning "Warning"
    Deletion is **irreversible** and removes all DataRecords associated with the Dataset.

## Troubleshooting

- **Dataset not found**: Run `sc-db list` and verify the ID/Name.
- **Duplicate names**: Use the ID to avoid deleting the wrong Dataset.

## Related

- [CLI Reference: sc-db](../../reference/cli/sc-db.md)
- [Dataset Record](../../reference/data-formats/dataset-record.md)
