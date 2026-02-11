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
scope: "How to ingest HFSS-exported admittance CSV files into the database"
version: v1.1.1
last_updated: 2026-02-11
updated_by: team
---

# Ingesting HFSS Data

This guide explains how to ingest HFSS report-exported Admittance (Y-parameter) `.csv` data into the system for further analysis.

!!! info "Prerequisites"
    - You have completed an HFSS simulation and created an Admittance report (for example, Im(Y11) vs Frequency).
    - You have exported the report data to a `.csv` file.
    - The filename will be used as the Dataset Name (e.g., `Design_A_Im_Y11.csv` -> Dataset: `Design_A_Im_Y11`).

---

## Steps

=== "CLI"

    Export `.csv` from HFSS first, then use `sc preprocess admittance`.

    ### 1. Export `.csv` in HFSS

    From the Admittance report window:

    1. Create or open an Admittance report (for example, Im(Y11)).
    2. In the report window, choose **Export** / **Export to File**.
    3. Select `.csv` as the output format and save the file.

    ### 2. Ingest Single `.csv` File

    If you only need to analyze a specific design file:

    ```bash
    uv run sc preprocess admittance path/to/your/file.csv
    ```

    ### 3. Batch Ingest a Directory of `.csv` Files

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
    2. Click **Upload Files** or drag `.csv` files into the upload area.
    3. Verify filenames and preview information.
    4. Click **Import** to start processing.

---

## Verification

After ingestion, verify that the data has been correctly created:

```bash
uv run sc db dataset-record list
```
