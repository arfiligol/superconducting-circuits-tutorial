---
aliases:
  - "sc-db data-record 指令參考"
  - "sc-db data-record CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# sc-db data-record

管理 DataRecord（僅支援讀取與刪除）。

## Usage

```bash
uv run sc-db data-record <action> [args]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `<action>` | `list` / `info` / `delete` / `auto-reorder` | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--help` | 顯示說明 | - |

## Examples

**列出**
```bash
uv run sc-db data-record list
```

**查詢**
```bash
uv run sc-db data-record info <ID>
```

**刪除**
```bash
uv run sc-db data-record delete <ID>
```

**重排 ID**
```bash
uv run sc-db data-record auto-reorder
```

## Notes

!!! warning "危險操作"
    `delete` 與 `auto-reorder` 為破壞性操作，請先備份。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
(placeholder)
```

<!-- CLI-HELP-END -->
