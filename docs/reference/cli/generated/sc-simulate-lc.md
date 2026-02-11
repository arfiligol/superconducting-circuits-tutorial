---
aliases:
  - "sc-simulate-lc 指令參考"
  - "sc-simulate-lc CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-simulate-lc

此頁面由自動化產生，請勿手動編輯。

```text
Usage: sc-simulate-lc [OPTIONS]

 Simulate an LC resonator and compute S11.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --inductance   -L      FLOAT    Inductance in nH (default: 10)               │
│                                 [default: 10.0]                              │
│ --capacitance  -C      FLOAT    Capacitance in pF (default: 1)               │
│                                 [default: 1.0]                               │
│ --start                FLOAT    Start frequency in GHz (default: 0.1)        │
│                                 [default: 0.1]                               │
│ --stop                 FLOAT    Stop frequency in GHz (default: 10)          │
│                                 [default: 10.0]                              │
│ --points       -n      INTEGER  Number of frequency points (default: 1000)   │
│                                 [default: 1000]                              │
│ --output       -o      TEXT     Output JSON file path (optional)             │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```
