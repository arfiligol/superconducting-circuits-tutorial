---
aliases:
- sc-plot-admittance
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 虛阻納繪圖指令說明
version: v0.1.0
last_updated: 2026-02-11
updated_by: docs-team
---

# sc plot admittance

繪製前處理後的虛阻納 ($Im(Y)$) 線圖，可用於檢查共振點提取品質。

## Usage

```bash
uv run sc plot admittance [OPTIONS] [datasets ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `datasets` | Dataset 名稱或 ID（可多個） | 必填 |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--show-zeros` | 標示零點交越 ($Im(Y)=0$) | False |
| `--freq-min` | 最低顯示頻率 (GHz) | |
| `--freq-max` | 最高顯示頻率 (GHz) | |
| `--title` | 自訂圖表標題 | |
| `--show` / `--no-show` | 是否直接開啟瀏覽器預覽 | `--show` |
| `--save-html` / `--no-save-html` | 是否輸出 HTML | `--no-save-html` |
| `--output`, `-o` | HTML 輸出路徑 | 自動產生 |

## Examples

**繪製虛阻納線圖**
```bash
uv run sc plot admittance LJPAL658_v1
```

**標示共振點並限制頻率範圍**
```bash
uv run sc plot admittance --show-zeros --freq-min 4.0 --freq-max 8.0 LJPAL658_v1
```

## Notes

!!! note "CLI 架構"
    此功能已整合至 `sc plot` 子指令樹，不再使用獨立命令 `plot-admittance`。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: sc plot admittance [OPTIONS] DATASETS...

 Plot admittance records from DB (line views).

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    datasets      DATASETS...  Dataset names or IDs. [required]             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --parameter                          TEXT   Admittance parameter to plot.    │
│                                             [default: Y11]                   │
│ --show-zeros      --no-show-zeros           Mark Im(Y)=0 crossings.          │
│                                             [default: no-show-zeros]         │
│ --freq-min                           FLOAT  Minimum frequency (GHz).         │
│ --freq-max                           FLOAT  Maximum frequency (GHz).         │
│ --title                              TEXT   Custom figure title.             │
│ --show            --no-show                 Open interactive preview in      │
│                                             browser.                         │
│                                             [default: show]                  │
│ --save-html       --no-save-html            Save output as HTML.             │
│                                             [default: no-save-html]          │
│ --output      -o                     PATH   Output HTML path.                │
│ --help                                      Show this message and exit.      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->
