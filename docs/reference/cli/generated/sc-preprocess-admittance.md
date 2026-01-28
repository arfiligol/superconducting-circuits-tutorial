---
aliases:
  - "sc-preprocess-admittance 指令參考"
  - "sc-preprocess-admittance CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-preprocess-admittance

此頁面由自動化產生，請勿手動編輯。

```text
Usage: sc-preprocess-admittance [OPTIONS] [CSV]...                             
                                                                                
 Import HFSS admittance CSV to SQLite database.                                 
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   csv      [CSV]...  Path(s) to HFSS admittance CSV.                         │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --component-id        TEXT  Override component identifier (dataset name)     │
│ --tags                TEXT  Comma-separated tags for database record         │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
