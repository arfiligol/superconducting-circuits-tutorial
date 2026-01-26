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
last_updated: 2026-01-12
updated_by: docs-team
---

# convert-hfss-phase

將 HFSS 匯出的 S-parameter Phase CSV 檔案轉換為標準 `ComponentRecord` JSON 格式。

## Usage

```bash
uv run convert-hfss-phase [OPTIONS] [csv ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `csv` | HFSS Phase CSV 檔案路徑 | (None) |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--component-id` | 強制指定 Component ID (預設使用檔名) | |
| `--output` | 輸出 JSON 路徑 | `data/preprocessed/<id>.json` |

## Examples

**基本轉換**
```bash
uv run convert-hfss-phase data/raw/phase/LJPAL658_S11_Phase.csv
```
