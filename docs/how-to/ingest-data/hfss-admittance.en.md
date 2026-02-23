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
version: v1.1.2
last_updated: 2026-02-11
updated_by: team
---

# Ingesting HFSS Data

This guide explains how to ingest Admittance (Y-parameter) `.csv` data exported from HFSS after plotting the curves, so it can be used for downstream analysis.

!!! info "Prerequisites"
    - You have completed an HFSS simulation and created an Admittance plot (for example, Im(Y11) vs Frequency).
    - You exported the plotted data to a `.csv` file (Export Plot Data / Export to File).
    - The system automatically derives the Dataset Name from the filename by stripping suffixes like `_Im` and `_Y11` (e.g., `Design_A_Im_Y11.csv` -> Dataset: `Design_A`).

---

## Steps

=== "CLI"

    Create the plot in HFSS first, export `.csv` from that plot, then run `sc preprocess admittance`.

    ### 1. Plot in HFSS, then export `.csv`

    From the Admittance plot/report window:

    1. Create or open an Admittance plot (for example, Im(Y11) vs Frequency).
    2. Verify the plotted curve and sweep range first.
    3. Choose **Export Plot Data** / **Export to File**.
    4. Select `.csv` as the output format and save the file.

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

    !!! tip "Auto-filtering & Duplicate Check"
        - In directory mode, the system defaults to only processing `.csv` files that contain `Re_Y` or `Im_Y` in their filename. You can use `--match "Y11,Yin"` to customize the filter.
        - The system automatically checks Dataset Names. If a name already exists, it is skipped by default to avoid duplicates.
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
