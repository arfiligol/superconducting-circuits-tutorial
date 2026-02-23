---
aliases:
- convert-hfss-phase
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: HFSS Phase 轉換指令說明
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# sc preprocess phase

將 HFSS 匯出的 S-parameter Phase CSV 檔案匯入 SQLite Dataset (原 `sc-preprocess-phase`)。

## Usage

```bash
uv run sc preprocess phase [OPTIONS] [csv ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `csv` | HFSS Phase CSV 檔案路徑 | (None) |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dataset-name` | 強制指定 Dataset 名稱 (單檔模式生效) | |
| `--tags` | 標籤 (Tag) 用逗號分隔 | |
| `--match` | 目錄模式下用來過濾檔案名稱的關鍵字 (用逗號分隔) | `Phase,S21,deg,rad` |

## Examples

**基本轉換**
```bash
uv run sc preprocess phase data/raw/phase/LJPAL658_S11_Phase.csv
```

## Notes

!!! note "資料庫匯入"
    目前指令會將資料匯入 SQLite 資料庫，而非輸出 JSON。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

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

<!-- CLI-HELP-END -->
