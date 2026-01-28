---
aliases:
- plot-admittance
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 虛阻納繪圖指令說明
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# plot-admittance

繪製前處理後的虛阻納 ($Im(Y)$) 數據，可用於檢查共振點提取品質。

## Usage

```bash
uv run plot-admittance [OPTIONS] [components ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `components` | Dataset 名稱或 ID | |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | 視覺化模式 (`lines`, `heatmap`, `both`) | `both` |
| `--show-zeros` | 標示零點交越 ($Im(Y)=0$) | False |
| `--freq-min` | 最低顯示頻率 (GHz) | |
| `--freq-max` | 最高顯示頻率 (GHz) | |
| `--title` | 自訂圖表標題 | |
| `--matplotlib` | 使用 Matplotlib 渲染 (預設: Plotly) | False |

## Examples

**繪製線圖與熱圖**
```bash
uv run plot-admittance LJPAL658_v1
```

**標示共振點並限制頻率範圍**
```bash
uv run plot-admittance --show-zeros --freq-min 4.0 --freq-max 8.0 LJPAL658_v1
```

## Notes

!!! note "Legacy 指令"
    此指令為舊版 CLI，若未在 `pyproject.toml` 註冊，請優先使用新版本對應指令。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: plot-admittance [OPTIONS] [COMPONENTS]...

Options:
  --mode TEXT          Visualization mode (lines/heatmap/both)
  --show-zeros         Mark zero crossings
  --freq-min FLOAT     Min frequency (GHz)
  --freq-max FLOAT     Max frequency (GHz)
  --title TEXT         Plot title
  --matplotlib         Use Matplotlib backend
  --help               Show this message and exit.
```

<!-- CLI-HELP-END -->
