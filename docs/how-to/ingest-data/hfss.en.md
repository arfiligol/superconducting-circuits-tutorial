---
aliases:
  - "Ingest HFSS Data"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/data-ingestion
status: stable
owner: team
audience: user
scope: "How to ingest HFSS Touchstone files into the database"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# Ingesting HFSS Data

This guide explains how to ingest HFSS Admittance (Y-parameter) simulation data into the system for further analysis.

!!! info "Prerequisites"
    - You have simulation files in `.sNp` format (Touchstone).
    - The filename will be used as the Dataset Name (e.g., `Design_A.s2p` -> Dataset: `Design_A`).

---

## Steps

=== "CLI"

    Use the `sc preprocess admittance` command.

    ### 1. Ingest Single File

    If you only need to analyze a specific design file:

    ```bash
    uv run sc preprocess admittance path/to/your/file.s2p
    ```

    ### 2. Batch Ingest Directory

    If you have a series of sweep data, specify the directory, and the system will process all supported files:

    ```bash
    uv run sc preprocess admittance path/to/data_folder/
    ```

    !!! tip "Duplicate Check"
        The system checks Dataset Names. Duplicate names are skipped by default.
        To force an update, utilize the database management tools to remove old data first (see [Manage Database](../manage-db/index.md)).

=== "UI (TBD)"

    !!! warning "Under Development"
        The GUI is currently under development.

    1. Open Dashboard and navigate to **Data Ingestion**.
    2. Click **Upload Files** or drag `.sNp` files into the upload area.
    3. Verify filenames and preview information.
    4. Click **Import** to start processing.

---

## Verification

After ingestion, verify that the data has been correctly created:

```bash
uv run sc db dataset-record list
```
