---
aliases:
  - "sc-preprocess-admittance CLI Reference"
  - "sc-preprocess-admittance 指令參考"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-preprocess-admittance

This page is auto-generated. Do not edit manually.

```text
Usage: sc-preprocess-admittance [OPTIONS] [CSV]...

 Import HFSS admittance CSV to SQLite database.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   csv      [CSV]...  Path(s) to HFSS admittance CSV.                         │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --dataset-name        TEXT  Override dataset name                            │
│ --tags                TEXT  Comma-separated tags for database record         │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
