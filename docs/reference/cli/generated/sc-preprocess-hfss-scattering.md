---
aliases:
  - "sc-preprocess-hfss-scattering 指令參考"
  - "sc-preprocess-hfss-scattering CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# sc-preprocess-hfss-scattering

此頁面由自動化產生, 請勿手動編輯。

```text
Usage: sc-preprocess-hfss-scattering [OPTIONS] [CSV]...                                                                
                                                                                                                        
 Import HFSS scattering matrix CSV to SQLite database.                                                                  
                                                                                                                        
 Supports both single files and directories.                                                                            
 - If a directory is provided, scans for all *.csv files.                                                               
 - AUTOMATICALLY SKIPS datasets that already exist in the database (by name).                                           
 - --dataset-name is ignored in batch/directory mode.                                                                   
 - --tags are applied to all NEWLY imported datasets in this run.                                                       
 - --match filters files in directories to only those containing any of the keywords.                                   
                                                                                                                        
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   csv      [CSV]...  Path(s) to HFSS S-Parameter or Phase CSV.                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --dataset-name        TEXT  Override dataset name                                                                    │
│ --tags                TEXT  Comma-separated tags for database record                                                 │
│ --match               TEXT  Comma-separated keywords to filter files (e.g., 'Phase,S21,deg,rad,re,im,mag').          │
│                             [default: Phase,S21,deg,rad,re,im,mag,S11]                                               │
│ --help                      Show this message and exit.                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
