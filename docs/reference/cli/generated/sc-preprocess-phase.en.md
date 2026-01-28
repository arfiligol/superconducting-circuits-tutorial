---
aliases:
  - "sc-preprocess-phase CLI Reference"
  - "sc-preprocess-phase 指令參考"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-preprocess-phase

This page is auto-generated. Do not edit manually.

```text
Usage: sc-preprocess-phase [OPTIONS] [CSV]...                                  
                                                                                
 Import HFSS phase CSV to SQLite database.                                      
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   csv      [CSV]...  Path(s) to HFSS phase CSV.                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --component-id        TEXT  Override component identifier                    │
│ --tags                TEXT  Comma-separated tags for database record         │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
