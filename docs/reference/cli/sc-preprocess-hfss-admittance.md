---
aliases:
- convert-hfss-admittance
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: HFSS Admittance 轉換指令說明
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# sc preprocess hfss admittance

將 HFSS 匯出的 Admittance CSV 檔案匯入 SQLite Dataset (原 `sc-preprocess-admittance`)。

## Usage

```bash
uv run sc preprocess hfss admittance [OPTIONS] [csv ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `csv` | HFSS Admittance CSV 檔案路徑 | (None) |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dataset-name` | 強制指定 Dataset 名稱 (單檔模式生效) | |
| `--tags` | 標籤 (Tag) 用逗號分隔 | |
| `--match` | 目錄模式下用來過濾檔案名稱的關鍵字 (用逗號分隔) | `Re_Y,Im_Y` |

## Examples

**基本轉換**
```bash
uv run sc preprocess hfss admittance data/raw/admittance/LJPAL658_v1_Im_Y11.csv
```

**批次匯入**
```bash
uv run sc preprocess hfss admittance data/raw/admittance/
```

**指定 Dataset 名稱 (單檔)**
```bash
uv run sc preprocess hfss admittance \
    --dataset-name MyJPA_v2 \
    data/raw/admittance/raw_export_final.csv
```

## Notes

!!! note "資料庫匯入"
    目前指令會將資料匯入 SQLite 資料庫，不再產生 JSON。

<!-- CLI-HELP-START -->

## CLI Help (自動生成)

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生, 請勿手動修改.

```text
Usage:                       
 sc-preprocess-hfss-admittanc 
 e [OPTIONS] [CSV]...         
                              
 Import HFSS admittance CSV   
 to SQLite database.          
                              
 Supports both single files   
 and directories.             
 - If a directory is          
 provided, scans for all      
 *.csv files.                 
 - AUTOMATICALLY SKIPS        
 datasets that already exist  
 in the database (by name).   
 - --dataset-name is ignored  
 in batch/directory mode.     
 - --tags are applied to all  
 NEWLY imported datasets in   
 this run.                    
 - --match filters files in   
 directories to only those    
 containing any of the        
 keywords.                    
                              
╭─ Arguments ────────────────╮
│   csv      [CSV].  Path(s) │
│            ..      to HFSS │
│                    admitt… │
│                    CSV     │
│                    files   │
│                    or      │
│                    direct… │
╰────────────────────────────╯
╭─ Options ──────────────────╮
│ --dat…        TEXT  Overr… │
│                     datas… │
│                     name   │
│                     (Sing… │
│                     file   │
│                     only)  │
│ --tags        TEXT  Comma… │
│                     tags   │
│                     for    │
│                     datab… │
│                     record │
│ --mat…        TEXT  Comma… │
│                     keywo… │
│                     to     │
│                     filter │
│                     files  │
│                     (e.g., │
│                     'Re_Y… │
│                     Fits   │
│                     admit… │
│                     natur… │
│                     [defa… │
│                     Re_Y,… │
│ --help              Show   │
│                     this   │
│                     messa… │
│                     and    │
│                     exit.  │
╰────────────────────────────╯
```

<!-- CLI-HELP-END -->


