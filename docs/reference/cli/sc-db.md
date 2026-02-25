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

# sc db

資料庫管理的單一入口，透過子指令操作各個模型。

## Model CRUD Scope

| Model | List | Get | Create | Update | Delete | 備註 |
|---|---|---|---|---|---|---|
| DatasetRecord | ✅ | ✅ | ❌ | ❌ | ✅ | 由匯入流程產生 |
| DataRecord | ✅ | ✅ | ❌ | ❌ | ✅ | 由匯入流程產生 |
| DerivedParameter | ✅ | ✅ | ❌ | ❌ | ✅ | 由分析流程產生 |
| Tag | ✅ | ✅ | ✅ | ✅ | ✅ | 允許手動維護與更名 |

## Usage

```bash
uv run sc db <model> <action> [args]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `<model>` | `dataset-record` / `data-record` / `derived-parameter` / `tag` | - |
| `<action>` | 依 model 而定（見各子頁） | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--help` | 顯示說明 | - |

## Examples

**列出 DatasetRecord**
```bash
uv run sc db dataset-record list
```

**查詢 DatasetRecord**
```bash
uv run sc db dataset-record info <ID_OR_NAME>
```

**刪除 DataRecord**
```bash
uv run sc db data-record delete <ID>
```

**新增 Tag**
```bash
uv run sc db tag create "NewTag"
```

**更名 Tag**
```bash
uv run sc db tag update "NewTag" "RenamedTag"
```

## Notes

!!! note "舊指令已移除"
    `sc db list/info/delete` 已移除，請改用 `sc db <model> <action>`。

<!-- CLI-HELP-START -->

## CLI Help (自動生成)

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生, 請勿手動修改.

```text
Usage: sc-db [OPTIONS] COMMAND [ARGS]...                                                                               
                                                                                                                        
 Manage SQLite database entities.                                                                                       
                                                                                                                        
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ dataset-record     Manage Datasets                                                                                   │
│ tag                Manage Tags                                                                                       │
│ data-record        Manage Data Records                                                                               │
│ derived-parameter  Manage Derived Parameters                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->





