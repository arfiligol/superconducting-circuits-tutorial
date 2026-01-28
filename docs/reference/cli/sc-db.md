---
aliases:
  - "sc-db 指令參考"
  - "sc-db CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# sc-db

`sc-db` 用於管理專案 SQLite 資料庫（`data/database.db`）中的 Dataset。此文件提供指令與參數的完整規格。

## 基本用法

```bash
uv run sc-db <subcommand> [args]
```

## 子指令總覽

| 子指令 | 用途 | 主要輸出 |
| --- | --- | --- |
| `list` | 列出所有 Dataset | 表格（ID、Name、Origin、Created At、Tags） |
| `info <identifier>` | 顯示單一 Dataset 詳情 | Origin、Tags、Data Records、Sweep Parameters、Source Files |
| `delete <identifier>` | 刪除 Dataset | 互動式確認（y/N） |

## Identifier 規則

`<identifier>` 可以是：

- **ID**（數字）
- **Name**（字串）

!!! tip "建議"
    若 Name 可能重複，請使用 ID 以避免誤刪。

## list

列出所有 Dataset。

```bash
uv run sc-db list
```

**輸出欄位**

- `ID`: Dataset 的唯一識別碼
- `Name`: Dataset 名稱
- `Origin`: 匯入來源（如 `measurement`）
- `Created At`: 建立時間
- `Tags`: 標籤（若無則顯示 `-`）

**範例輸出**

```text
All Datasets (3)
┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━┓
┃ ID ┃ Name               ┃ Origin      ┃ Created At       ┃ Tags ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━┩
│  3 │ DummyFlux          │ measurement │ 2026-01-28 06:03 │ -    │
│  2 │ Checkpoint3_Single │ measurement │ 2026-01-28 06:01 │ -    │
│  1 │ Checkpoint3_Test   │ measurement │ 2026-01-28 06:01 │ -    │
└────┴────────────────────┴─────────────┴──────────────────┴──────┘
```

## info

顯示單一 Dataset 的詳細資訊。

```bash
uv run sc-db info <identifier>
```

**輸出內容**

- `Origin`
- `Tags`
- `Data Records`（筆數）
- `Sweep Parameters`
- `Source Files`

**範例輸出**

```text
Dataset Details: PF6FQ_Q0_Readout
ID: 4
Origin: measurement
Data Records: 1
Sweep Parameters:
  - L_jun_nH: 0.5
Source Files:
  - .../PF6FQ_Q0_Readout_Im_Y11.csv
```

## delete

刪除 Dataset（含關聯的 DataRecords）。

```bash
uv run sc-db delete <identifier>
```

!!! warning "注意"
    刪除操作不可復原，且會連帶刪除該 Dataset 的所有 DataRecords。

**互動式確認**

- 預設為 **No**（輸入 `y` 才會執行刪除）

## Related

- [How-to: 使用 sc-db 管理資料集](../../how-to/database/manage-datasets.md)
- [Dataset Record](../data-formats/dataset-record.md)
