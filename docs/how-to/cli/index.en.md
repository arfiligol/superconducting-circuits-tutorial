---
aliases:
  - "CLI How-to"
  - "CLI 操作指南"
tags:
  - diataxis/how-to
  - status/draft
  - audience/user
  - topic/cli
owner: I-LI CHIU
---

# CLI Overview

This guide explains how to use the project CLI commands for common tasks and quickly locate parameters and outputs.

## Prerequisites

- Environment is installed and dependencies are synced (see [Installation](../getting-started/installation.md)).

## Steps

1. **Show command help**

   ```bash
   uv run <command> --help
   ```

   Examples:

   ```bash
   uv run sc-db --help
   uv run sc-preprocess-admittance --help
   ```

2. **Run common tasks**

   - List imported Datasets:
     ```bash
     uv run sc-db list
     ```

   - Import HFSS Admittance CSV:
     ```bash
     uv run sc-preprocess-admittance data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
     ```

   - Fit SQUID model:
     ```bash
     uv run sc-fit-squid
     ```

3. **Find full parameters and outputs**

   See:

   - [CLI Reference](../../reference/cli/index.md)

## Related

- [Database Management](../database/manage-datasets.md)
- [Preprocess HFSS Admittance](../preprocess/hfss-admittance.md)
- [CLI Reference](../../reference/cli/index.md)
