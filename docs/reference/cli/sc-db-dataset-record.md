---
aliases:
  - "sc-db dataset-record 指令參考"
  - "sc-db dataset-record CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# sc-db dataset-record

管理 DatasetRecord（僅支援讀取與刪除）。

## Usage

```bash
uv run sc-db dataset-record <action> [args]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `<action>` | `list` / `info` / `delete` / `auto-reorder` | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--help` | 顯示說明 | - |
| `--sort-by` | `auto-reorder` 排序策略：`id` / `name` | `id` |

## Examples

**列出**
```bash
uv run sc-db dataset-record list
```

**查詢**
```bash
uv run sc-db dataset-record info <ID_OR_NAME>
```

**刪除**
```bash
uv run sc-db dataset-record delete <ID_OR_NAME>
```

**重排 ID**
```bash
uv run sc-db dataset-record auto-reorder
```

**依名稱重排 ID**
```bash
uv run sc-db dataset-record auto-reorder --sort-by name
```

## Notes

!!! warning "危險操作"
    `delete` 與 `auto-reorder` 會影響關聯資料，請先備份。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
(placeholder)
```

<!-- CLI-HELP-END -->
