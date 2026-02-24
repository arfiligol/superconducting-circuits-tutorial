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

此頁面由自動化產生, 請勿手動編輯。

```text
Usage: sc-fit-squid [OPTIONS] [DATASETS]...                                                                            
                                                                                                                        
 Fit SQUID LC parameters (Ls, C) from admittance data.                                                                  
                                                                                                                        
 Models:                                                                                                                
 - Default: Fits with Series Inductance (Ls).                                                                           
 - --no-ls: Fits WITHOUT Series Inductance (ideal LC).                                                                  
 - --fixed-c <VAL>: Fits Ls with Fixed Capacitance.                                                                     
                                                                                                                        
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   datasets      [DATASETS]...  Dataset names or IDs.                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --modes                                  TEXT                         Modes to fit/plot (e.g. '1'). Can be used      │
│                                                                       multiple times.                                │
│                                                                       [default: Mode 1]                              │
│ --title                                  TEXT                         Plot title                                     │
│                                                                       [default: Q0 Mode Fits (by Admittance)]        │
│ --ls-min                                 FLOAT                        [default: 0.0]                                 │
│ --ls-max                                 FLOAT                                                                       │
│ --c-min                                  FLOAT                        [default: 0.0]                                 │
│ --c-max                                  FLOAT                                                                       │
│ --fixed-c                                FLOAT                        Fixed Capacitance Value (pF). Forces 'fixed_c' │
│                                                                       model.                                         │
│ --no-ls                                                               Disable Series Inductance (Ls) fitting.        │
│ --fit-min                                FLOAT                        Fit window min (GHz) [default: 15.0]           │
│ --fit-max                                FLOAT                        Fit window max (GHz) [default: 30.0]           │
│ --save-to-db          --no-save-to-db                                 Persist fit outputs into                       │
│                                                                       DataRecord/DerivedParameter tables.            │
│                                                                       [default: no-save-to-db]                       │
│ --device-type                            [resonator|qubit|jpa|other]  Device type used when saving DerivedParameter  │
│                                                                       rows.                                          │
│                                                                       [default: other]                               │
│ --replace-existing    --append                                        Replace existing lc_squid_fit outputs in DB    │
│                                                                       for each dataset.                              │
│                                                                       [default: replace-existing]                    │
│ --help                                                                Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
