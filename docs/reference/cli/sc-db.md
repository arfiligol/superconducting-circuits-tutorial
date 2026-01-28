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
  - sot/true
owner: I-LI CHIU
---

# sc-db

管理資料庫中的 Dataset（列出、查看、刪除）。適合需要完整管理功能時使用。

## Model CRUD Scope

| Model | List | Get | Create | Update | Delete | 備註 |
|---|---|---|---|---|---|---|
| DatasetRecord | ✅ | ✅ | ❌ | ❌ | ✅ | 由匯入流程產生 |
| DataRecord | ✅ | ✅ | ❌ | ❌ | ✅ | 由匯入流程產生 |
| DerivedParameter | ✅ | ✅ | ❌ | ❌ | ✅ | 由分析流程產生 |
| Tag | ✅ | ✅ | ✅ | ✅ | ✅ | 允許手動維護與更名 |

## Usage

```bash
uv run sc-db <command> [args]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `<command>` | `list` / `info` / `delete` | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--help` | 顯示說明 | - |

## Examples

**列出全部資料集**
```bash
uv run sc-db list
```

**查看資料集詳情**
```bash
uv run sc-db info 3
```

**刪除資料集**
```bash
uv run sc-db delete 3
```

## Notes

!!! warning "危險操作"
    `delete` 會刪除資料集與其關聯的 DataRecords，且不可復原。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: sc-db [OPTIONS] COMMAND [ARGS]...                                       
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ list    Handle 'list' subcommand.                                            │
│ info    Handle 'info' subcommand.                                            │
│ delete  Handle 'delete' subcommand.                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->
