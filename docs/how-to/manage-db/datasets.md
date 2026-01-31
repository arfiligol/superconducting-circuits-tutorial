---
aliases:
  - "Manage Datasets"
  - "Dataset 管理"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/database
status: stable
owner: team
audience: user
scope: "如何查詢與刪除資料庫中的 Dataset"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# Managing Datasets

本指南說明如何查詢、篩選與刪除系統中的 Datasets。

---

## 操作步驟

=== "CLI"

    使用 `sc db dataset-record` 指令群。

    ### 1. 列出所有資料 (List)

    查詢目前所有的 Dataset 及其關聯記錄：

    ```bash
    uv run sc db dataset-record list
    ```

    **進階篩選**：
    ```bash
    # 依名稱關鍵字篩選
    uv run sc db dataset-record list --name-filter "LJPAL"
    
    # 僅顯示包含特定 Tag 的資料
    uv run sc db dataset-record list --tag-filter "verified"
    ```

    ### 2. 刪除資料 (Delete)

    刪除指定的 Dataset：

    ```bash
    uv run sc db dataset-record delete <DATASET_ID>
    ```

    !!! danger "危險操作"
        刪除 Dataset 會一併移除其關聯的所有 Data Record。此動作無法復原。

=== "UI (TBD)"

    !!! warning "開發中"
        資料庫管理介面尚在開發階段。

    1. 進入 **Database** 頁面。
    2. 使用上方的 Search Bar 搜尋 Dataset。
    3. 點擊行末的 **垃圾桶圖示** 進行刪除。

---

## 相關參考

- [Database Schema](../../explanation/database-schema.md) (TBD)
