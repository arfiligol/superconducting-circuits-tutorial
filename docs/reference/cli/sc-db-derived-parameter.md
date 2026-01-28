---
aliases:
  - "sc-db derived-parameter 指令參考"
  - "sc-db derived-parameter CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# sc-db derived-parameter

管理 DerivedParameter（僅支援讀取與刪除）。

## Usage

```bash
uv run sc-db derived-parameter <action> [args]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `<action>` | `list` / `info` / `delete` / `reorder-id` | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--help` | 顯示說明 | - |

## Examples

**列出**
```bash
uv run sc-db derived-parameter list
```

**查詢**
```bash
uv run sc-db derived-parameter info <ID>
```

**刪除**
```bash
uv run sc-db derived-parameter delete <ID>
```

**重排 ID**
```bash
uv run sc-db derived-parameter reorder-id <OLD_ID> <NEW_ID>
```

## Notes

!!! warning "危險操作"
    `delete` 與 `reorder-id` 為破壞性操作，請先備份。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
(placeholder)
```

<!-- CLI-HELP-END -->
