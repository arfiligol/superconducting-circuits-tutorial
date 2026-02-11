---
aliases:
  - "Manage Datasets"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/database
status: stable
owner: team
audience: user
scope: "How to list, filter, and delete Datasets"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# Managing Datasets

This guide explains how to query, filter, and delete Datasets in the system.

---

## Steps

=== "CLI"

    Use the `sc db dataset-record` command group.

    ### 1. List All Data

    Query all Datasets and their associated records:

    ```bash
    uv run sc db dataset-record list
    ```

    **Advanced Filtering**:
    ```bash
    # Filter by name keyword
    uv run sc db dataset-record list --name-filter "LJPAL"

    # Filter by tag
    uv run sc db dataset-record list --tag-filter "verified"
    ```

    ### 2. Delete Data

    Delete a specific Dataset:

    ```bash
    uv run sc db dataset-record delete <DATASET_ID>
    ```

    !!! danger "Irreversible Operation"
        Deleting a Dataset will also remove all its associated Data Records. This cannot be undone.

=== "UI (TBD)"

    !!! warning "Under Development"
        The Database Management GUI is currently under development.

    1. Navigate to **Database** page.
    2. Use the Search Bar to find the Dataset.
    3. Click the **Trash Icon** at the end of the row to delete.

---

## See Also

- (TBD) Database Schema
