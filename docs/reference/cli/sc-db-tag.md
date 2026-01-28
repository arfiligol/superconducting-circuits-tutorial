---
aliases:
  - "sc-db tag 指令參考"
  - "sc-db tag CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# sc-db tag

管理 Tag（支援建立、更新、刪除）。

## Usage

```bash
uv run sc-db tag <action> [args]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `<action>` | `list` / `create` / `update` / `delete` / `auto-reorder` | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--help` | 顯示說明 | - |

## Examples

**列出**
```bash
uv run sc-db tag list
```

**新增**
```bash
uv run sc-db tag create "NewTag"
```

**更名（同步關聯）**
```bash
uv run sc-db tag update "NewTag" "RenamedTag"
```

**刪除**
```bash
uv run sc-db tag delete "RenamedTag"
```

**重排 ID**
```bash
uv run sc-db tag auto-reorder
```

## Notes

!!! warning "關聯更新"
    `update` 會同步更新所有關聯的 DatasetTagLink。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
(placeholder)
```

<!-- CLI-HELP-END -->
