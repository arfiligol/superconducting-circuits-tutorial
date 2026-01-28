---
aliases:
- Preprocess HFSS Admittance
- HFSS 虛阻納處理
tags:
- audience/team
- diataxis/how-to
- topic/preprocess
status: stable
owner: docs-team
audience: team
scope: How to process HFSS exported Admittance CSV
version: v0.2.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Preprocess HFSS Admittance

This guide explains how to import HFSS-exported Im(Y) CSV data directly into the project's SQLite database.

## Prerequisites

- Raw CSV file is placed in `data/raw/layout_simulation/admittance/`.
- The CSV should contain Frequency and columns for each $L_{jun}$ variable.

## Steps (Database Only)

1. **Confirm file path**
   ```bash
   ls data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
   ```

2. **Run Database Import**
   Use the `sc-preprocess-admittance` command (imports to `data/database.db` by default):
   ```bash
   uv run sc-preprocess-admittance data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
   ```

3. **(Optional) Specify Component ID & Tags**
   ```bash
   uv run sc-preprocess-admittance \
       --component-id "LJPAL658_v1" \
       --tags "chip/PF6FQ,experiment/2026Q1" \
       data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
   ```

4. **Verify Import**
   Use `sc-list-datasets` to check:
   ```bash
   uv run sc-list-datasets
   ```

## Next Steps

- [Run Admittance Fit](../analysis/admittance-fit.md) - Execute fitting analysis
