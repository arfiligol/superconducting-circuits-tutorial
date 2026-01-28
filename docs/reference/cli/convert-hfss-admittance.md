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
last_updated: 2026-01-12
updated_by: docs-team
---

# convert-hfss-admittance

將 HFSS 匯出的 Admittance CSV 檔案轉換為標準 `ComponentRecord` JSON 格式。

## Usage

```bash
uv run convert-hfss-admittance [OPTIONS] [csv ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `csv` | HFSS Admittance CSV 檔案路徑 | (None) |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--component-id` | 強制指定 Component ID (預設使用檔名) | |
| `--output` | 輸出 JSON 路徑 | `data/preprocessed/<id>.json` |

## Examples

**基本轉換**
```bash
uv run convert-hfss-admittance data/raw/admittance/LJPAL658_v1_Im_Y11.csv
```

**指定 Component ID**
```bash
uv run convert-hfss-admittance \
    --component-id MyJPA_v2 \
    data/raw/admittance/raw_export_final.csv
```

## Notes

!!! note "資料庫匯入"
    目前指令會將資料匯入 SQLite 資料庫，而非輸出 JSON。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

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

<!-- CLI-HELP-END -->



