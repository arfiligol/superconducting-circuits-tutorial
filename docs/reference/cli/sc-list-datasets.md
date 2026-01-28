---
aliases:
  - "sc-list-datasets 指令參考"
  - "sc-list-datasets CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
owner: I-LI CHIU
---

# sc-list-datasets

列出資料庫中的 Dataset。此指令較輕量，適合快速檢視資料清單。

## Usage

```bash
uv run sc-list-datasets [--tag <tag>] [--verbose]
```

## Related

- [sc-db](sc-db.md) - 完整的資料集管理指令

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: sc-list-datasets [OPTIONS]                                              
                                                                                
 List datasets stored in SQLite database.                                       
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --tag              TEXT  Filter by tag (can be specified multiple times)     │
│ --verbose  -v            Show more details                                   │
│ --help                   Show this message and exit.                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->



