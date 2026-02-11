---
aliases:
  - "sc-preprocess-phase 指令參考"
  - "sc-preprocess-phase CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-preprocess-phase

此頁面由自動化產生，請勿手動編輯。

```text
Usage: sc-preprocess-phase [OPTIONS] [CSV]...

 Import HFSS phase CSV to SQLite database.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   csv      [CSV]...  Path(s) to HFSS phase CSV.                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --dataset-name        TEXT  Override dataset name                            │
│ --tags                TEXT  Comma-separated tags for database record         │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
