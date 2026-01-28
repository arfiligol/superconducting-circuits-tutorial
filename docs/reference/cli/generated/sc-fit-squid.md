---
aliases:
  - "sc-fit-squid 指令參考"
  - "sc-fit-squid CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-fit-squid

此頁面由自動化產生，請勿手動編輯。

```text
Usage: sc-fit-squid [OPTIONS] [COMPONENTS]...                                  
                                                                                
 Batch analysis of admittance datasets.                                         
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   components      [COMPONENTS]...  Dataset names or IDs.                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --modes                            TEXT   Modes to fit/plot (e.g. 'Mode 1'). │
│                                           [default: Mode 1]                  │
│ --title                            TEXT   Plot title                         │
│                                           [default: Q0 Mode Fits (by         │
│                                           Admittance)]                       │
│ --ls-min                           FLOAT  [default: 0.0]                     │
│ --ls-max                           FLOAT                                     │
│ --c-min                            FLOAT  [default: 0.0]                     │
│ --c-max                            FLOAT                                     │
│ --fixed-c                          FLOAT                                     │
│ --fit-min                          FLOAT  Fit window min (GHz)               │
│                                           [default: 15.0]                    │
│ --fit-max                          FLOAT  Fit window max (GHz)               │
│                                           [default: 30.0]                    │
│ --matplotlib    --no-matplotlib           Use Matplotlib backend             │
│                                           [default: no-matplotlib]           │
│ --help                                    Show this message and exit.        │
╰──────────────────────────────────────────────────────────────────────────────╯
```
