---
aliases:
  - "CLI 操作指南"
  - "CLI How-to"
tags:
  - diataxis/how-to
  - status/draft
  - audience/user
  - topic/cli
owner: I-LI CHIU
---

# CLI 使用總覽

本指南說明如何使用專案的 CLI 指令完成常見任務，並快速定位參數與說明。

## Prerequisites

- 已完成環境安裝與依賴同步（參考 [安裝環境](../getting-started/installation.md)）。

## Steps

1. **查看指令說明**

   ```bash
   uv run <command> --help
   ```

   例：

   ```bash
   uv run sc-db --help
   uv run sc-preprocess-admittance --help
   ```

2. **執行常見任務**

   - 列出已匯入的 Dataset：
     ```bash
     uv run sc-db list
     ```

   - 匯入 HFSS Admittance CSV：
     ```bash
     uv run sc-preprocess-admittance data/raw/layout_simulation/admittance/MyChip_Im_Y11.csv
     ```

   - 擬合 SQUID 模型：
     ```bash
     uv run sc-fit-squid
     ```

3. **查詢完整參數與輸出**

   詳細參數與輸出欄位請參考：

   - [CLI Reference](../../reference/cli/index.md)

## Related

- [Database 管理](../database/manage-datasets.md)
- [前處理：HFSS Admittance](../preprocess/hfss-admittance.md)
- [CLI Reference](../../reference/cli/index.md)
