---
aliases:
  - "使用 sc-db 管理資料集"
  - "Manage Datasets with sc-db"
tags:
  - diataxis/how-to
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# 使用 sc-db 管理資料集

本指南示範如何使用 `sc-db` 列出、查看與刪除已匯入的 Dataset。

## Prerequisites

- 已完成資料匯入，並存在 `data/database.db`。

## Steps

1. **列出所有 Dataset**

   ```bash
   uv run sc-db list
   ```

2. **查看單一 Dataset 詳情**（可用 ID 或 Name）

   ```bash
   # 使用 ID
   uv run sc-db info 3

   # 使用 Name
   uv run sc-db info Checkpoint3_Single
   ```

3. **刪除指定 Dataset**（需要互動式確認）

   ```bash
   uv run sc-db delete 3
   ```

   輸入 `y` 後才會執行刪除。

!!! warning "注意"
    刪除後 **無法復原**，且會連帶刪除該 Dataset 的所有 DataRecords。

## Troubleshooting

- **找不到 Dataset**：請先執行 `sc-db list` 確認 ID/Name 是否正確。
- **Name 重複**：請改用 ID 以避免誤刪。

## Related

- [CLI Reference: sc-db](../../reference/cli/sc-db.md)
- [Dataset Record](../../reference/data-formats/dataset-record.md)
