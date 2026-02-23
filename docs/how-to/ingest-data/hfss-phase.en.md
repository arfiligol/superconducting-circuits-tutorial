---
aliases:
  - "Ingest HFSS Phase"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/data-ingestion
status: stable
owner: team
audience: user
scope: "How to ingest HFSS-exported phase CSV files into the database"
version: v1.1.2
last_updated: 2026-02-23
updated_by: team
---

# Ingesting HFSS Phase Data

This guide explains how to ingest S-parameter Phase `.csv` data exported from HFSS into the system for downstream analysis (e.g., resonance frequency fitting). This applies to **Driven Modal** simulation data to find resonant frequencies using Group Delay peaks.

!!! info "Prerequisites"
    - You have completed an HFSS simulation and created a Phase plot (e.g. `ang_rad(S21)` or `cang_deg(S11)`).
    - You have exported the plotted data to a `.csv` file.
    - **The filename must contain the S-parameter type** (e.g., `PF6FQ_Q1_Readout_ang_rad_S21.csv` is automatically recognized as S21).

---

## Auto-filtering & Unit Handling Mechanism

To ensure consistency in scientific computing, the system assumes the following underlying principles for Phase files:

1. **Unified Storage in Radians**: The system automatically scans the file. If your file or its filename contains `deg` (Degree), the system will **automatically convert the values to Radians** before writing to the database. If it's `rad`, the values are stored as-is.
2. **Distinguishing Wrapped vs Unwrapped**:
    - If the filename or column name contains `cang` (Continuous Angle), the database `representation` will be labeled as `unwrapped_phase`.
    - If it only contains `ang` (or `phase`), the `representation` will be labeled as `phase` (defaulting to the $[-\pi, \pi]$ bound).

> When using the system, you **only need to ingest one type**. There is no need to export multiple versions for different units. The analysis modules can dynamically convert units or unwrap data on the fly.

---

## Steps

=== "CLI"

    Use `sc preprocess phase` to ingest data.

    ### 1. Ingest Single `.csv` File

    ```bash
    uv run sc preprocess phase path/to/your/phase_file.csv
    ```

    ### 2. Batch Ingest a Directory of `.csv` Files

    If you have a series of sweep data, specify the directory:

    ```bash
    uv run sc preprocess phase path/to/data_folder/
    ```

    !!! tip "Auto-filtering & Duplicate Check"
        - In directory mode, the system defaults to only processing `.csv` files that contain `Phase`, `S21`, `deg` or `rad` in their filename. You can use `--match` to customize the filter.
        - The system automatically derives the Dataset Name from the filename. If that Dataset already exists in the database, it skips it by default to avoid duplicates.

=== "UI (TBD)"

    !!! warning "Under Development"
        The GUI data ingestion feature is currently under development.

---

## Verification

After ingestion, verify that the data has been correctly created:

```bash
uv run sc db data-record list
```
You should see the newly added records in the table, with their `Type` as `s_parameters` and their `Rep` as `phase` or `unwrapped_phase`.
